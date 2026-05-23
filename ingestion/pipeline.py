from datetime import datetime, timedelta
from typing import Iterator
import logging
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq

from .connectors import get_connector
from .base import Watermark, SourceRecord
from .validation import MultiSchemaValidator
from .dlq import DeadLetterQueue

logger = logging.getLogger(__name__)

class IngestionPipeline:
    def __init__(
        self,
        sources: list[dict],
        output_path: str,
        dlq_path: str = "/tmp/dlq",
        watermark_path: str = "/tmp/watermarks"
    ):
        self.sources = sources
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.dlq = DeadLetterQueue(dlq_path)
        self.watermark_path = Path(watermark_path)
        self.watermark_path.mkdir(parents=True, exist=True)
        self.validator = MultiSchemaValidator()
    
    def add_schema(self, schema_name: str, schema: dict) -> None:
        self.validator.add_schema(schema_name, schema)
    
    def _load_watermark(self, source_id: str) -> Watermark | None:
        wm_file = self.watermark_path / f"{source_id}.json"
        if not wm_file.exists():
            return None
        import json
        with open(wm_file) as f:
            data = json.load(f)
        return Watermark(
            source_id=source_id,
            last_processed=datetime.fromisoformat(data["last_processed"]),
            watermark_key=data.get("watermark_key", "last_processed")
        )
    
    def _save_watermark(self, watermark: Watermark) -> None:
        import json
        wm_file = self.watermark_path / f"{watermark.source_id}.json"
        with open(wm_file, 'w') as f:
            json.dump({
                "source_id": watermark.source_id,
                "last_processed": watermark.last_processed.isoformat(),
                "watermark_key": watermark.watermark_key
            }, f)
    
    def run(self) -> dict:
        """Run the pipeline for all sources"""
        results = {
            "sources_processed": 0,
            "total_records": 0,
            "error_records": 0,
            "source_details": []
        }
        
        for source in self.sources:
            source_result = self._process_source(source)
            results["source_details"].append(source_result)
            results["total_records"] += source_result["records_read"]
            results["error_records"] += source_result["errors"]
            if source_result["records_read"] > 0:
                results["sources_processed"] += 1
        
        return results
    
    def _process_source(self, source: dict) -> dict:
        source_id = source["source_id"]
        source_type = source["source_type"]
        config = source["config"]
        schema_name = source.get("schema_name")
        
        logger.info(f"Processing source: {source_id} ({source_type})")
        
        records = []
        errors = 0
        watermark = self._load_watermark(source_id)
        
        try:
            connector = get_connector(source_type, source_id, config)
            connector.connect()
            
            for record in connector.fetch(watermark):
                if schema_name:
                    is_valid, errs = self.validator.validate(record.data, schema_name)
                    if not is_valid:
                        self.dlq.write(record.data, source_id, "; ".join(errs), record.data)
                        errors += 1
                        continue
                
                records.append({
                    "data": record.data,
                    "source_id": record.source_id,
                    "ingested_at": record.ingested_at.isoformat(),
                    "metadata": record.metadata
                })
            
            connector.close()
            
        except Exception as e:
            logger.error(f"Error processing source {source_id}: {e}")
            # Write all buffered records to DLQ
            for rec in records:
                self.dlq.write(rec["data"], source_id, str(e), rec["data"])
            errors += len(records)
            records = []
        
        # Write to Bronze parquet
        output_file = None
        if records:
            table = pa.Table.from_pylist(records)
            date_key = datetime.utcnow().strftime("%Y-%m-%d")
            output_file = self.output_path / f"bronze_{source_id}_{date_key}.parquet"
            pq.write_table(table, output_file)
            logger.info(f"Written {len(records)} records to {output_file}")
        
        # Update watermark
        new_watermark = Watermark(
            source_id=source_id,
            last_processed=datetime.utcnow()
        )
        self._save_watermark(new_watermark)
        
        return {
            "source_id": source_id,
            "records_read": len(records),
            "errors": errors,
            "output_file": str(output_file) if output_file else None
        }