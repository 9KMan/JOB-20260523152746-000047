from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterator
import logging

logger = logging.getLogger(__name__)

@dataclass
class Watermark:
    source_id: str
    last_processed: datetime
    watermark_key: str = "last_processed"

@dataclass
class SourceRecord:
    data: dict
    source_id: str
    ingested_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)

class BaseConnector(ABC):
    def __init__(self, source_id: str, config: dict):
        self.source_id = source_id
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the source"""
        pass
    
    @abstractmethod
    def fetch(self, watermark: Watermark | None = None) -> Iterator[SourceRecord]:
        """Fetch records since watermark, yield SourceRecord objects"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close connection"""
        pass
    
    def validate_record(self, record: dict) -> bool:
        """Override in subclass for schema validation"""
        return True