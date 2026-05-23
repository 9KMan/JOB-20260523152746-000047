import requests
from datetime import datetime
from typing import Iterator
from .base import BaseConnector, Watermark, SourceRecord

class RESTAPIConnector(BaseConnector):
    def connect(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(self.config.get("headers", {}))
        self.base_url = self.config["base_url"]
        self.page_size = self.config.get("page_size", 100)
    
    def fetch(self, watermark: Watermark | None = None) -> Iterator[SourceRecord]:
        params = self.config.get("params", {}).copy()
        if watermark:
            params[self.config.get("watermark_field", "updated_since")] = watermark.last_processed.isoformat()
        
        page = 1
        while True:
            params["page"] = page
            params["limit"] = self.page_size
            response = self.session.get(f"{self.base_url}/{self.config.get('endpoint', '')}", params=params)
            response.raise_for_status()
            data = response.json()
            
            records = data if isinstance(data, list) else data.get(self.config.get("data_key", "data"), [])
            if not records:
                break
            
            for record in records:
                if self.validate_record(record):
                    yield SourceRecord(data=record, source_id=self.source_id)
                else:
                    self.logger.warning(f"Record failed validation from {self.source_id}")
            
            page += 1
            if page > self.config.get("max_pages", 10):
                break
    
    def close(self) -> None:
        self.session.close()