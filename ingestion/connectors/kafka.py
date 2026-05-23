from kafka import KafkaConsumer
from typing import Iterator
import json
from .base import BaseConnector, Watermark, SourceRecord

class KafkaConnector(BaseConnector):
    def connect(self) -> None:
        self.consumer = KafkaConsumer(
            self.config["topic"],
            bootstrap_servers=self.config["bootstrap_servers"],
            auto_offset_reset=self.config.get("auto_offset_reset", "earliest"),
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            group_id=self.config.get("group_id", "pipeline-consumer"),
            enable_auto_commit=True
        )
    
    def fetch(self, watermark: Watermark | None = None) -> Iterator[SourceRecord]:
        for message in self.consumer:
            record = message.value
            if self.validate_record(record):
                yield SourceRecord(
                    data=record,
                    source_id=self.source_id,
                    metadata={"offset": message.offset, "partition": message.partition}
                )
    
    def close(self) -> None:
        self.consumer.close()