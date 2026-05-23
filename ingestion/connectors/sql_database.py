from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import Iterator
from .base import BaseConnector, Watermark, SourceRecord
import json

class SQLDatabaseConnector(BaseConnector):
    def connect(self) -> None:
        conn_str = self.config["connection_string"]
        self.engine: Engine = create_engine(conn_str)
    
    def fetch(self, watermark: Watermark | None = None) -> Iterator[SourceRecord]:
        query = self.config["query"]
        params = {}
        
        if watermark:
            # Replace placeholder in query with watermark value
            watermark_field = self.config.get("watermark_field", "updated_at")
            query = query.replace(f"{{{watermark_field}}}", watermark.last_processed.isoformat())
        
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            for row in result:
                record = row._asdict()
                if self.validate_record(record):
                    yield SourceRecord(data=record, source_id=self.source_id)
    
    def close(self) -> None:
        self.engine.dispose()