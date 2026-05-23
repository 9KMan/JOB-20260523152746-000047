import json
from datetime import datetime
from pathlib import Path
from typing import Any
import logging

logger = logging.getLogger(__name__)

class DeadLetterQueue:
    def __init__(self, base_path: str = "/tmp/dlq"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def write(self, record: Any, source_id: str, error: str, original_data: dict) -> str:
        """Write failed record to DLQ, return path to the file"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{source_id}_{timestamp}.json"
        filepath = self.base_path / filename
        
        dlq_entry = {
            "original_data": original_data,
            "source_id": source_id,
            "error": error,
            "failed_at": datetime.utcnow().isoformat(),
            "filename": filename
        }
        
        with open(filepath, 'w') as f:
            json.dump(dlq_entry, f, indent=2)
        
        logger.info(f"Written to DLQ: {filepath}")
        return str(filepath)
    
    def read_all(self, limit: int = 100) -> list[dict]:
        """Read all DLQ entries, up to limit"""
        entries = []
        for filepath in sorted(self.base_path.glob("*.json"))[:limit]:
            with open(filepath) as f:
                entries.append(json.load(f))
        return entries
    
    def retry(self, filepath: str) -> dict:
        """Read a DLQ entry for retry"""
        with open(filepath) as f:
            return json.load(f)