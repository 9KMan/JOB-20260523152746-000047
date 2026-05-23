import boto3
from botoc.config import Config as BotoConfig
from typing import Iterator
import json
import csv
import io
from .base import BaseConnector, Watermark, SourceRecord

class S3Connector(BaseConnector):
    def connect(self) -> None:
        self.s3 = boto3.client(
            's3',
            endpoint_url=self.config.get("endpoint_url"),
            aws_access_key_id=self.config.get("aws_access_key_id"),
            aws_secret_access_key=self.config.get("aws_secret_access_key"),
            config=BotoConfig(signature_version='s3v4')
        )
        self.bucket = self.config["bucket"]
        self.prefix = self.config.get("prefix", "")
        self.format = self.config.get("format", "json")  # json or csv
    
    def fetch(self, watermark: Watermark | None = None) -> Iterator[SourceRecord]:
        paginator = self.s3.get_paginator('list_objects_v2')
        
        prefix = self.prefix
        if watermark:
            # Filter by last modified after watermark
            pass  # Let the listing handle it
        
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for obj in page.get('Contents', []):
                key = obj['Key']
                if not self._should_process(key):
                    continue
                
                response = self.s3.get_object(Bucket=self.bucket, Key=key)
                content = response['Body'].read().decode('utf-8')
                
                if self.format == "json":
                    for record in self._parse_json(content):
                        yield SourceRecord(data=record, source_id=self.source_id, metadata={"key": key})
                elif self.format == "csv":
                    for record in self._parse_csv(content):
                        yield SourceRecord(data=record, source_id=self.source_id, metadata={"key": key})
    
    def _should_process(self, key: str) -> bool:
        return key.endswith(f".{self.format}")
    
    def _parse_json(self, content: str):
        data = json.loads(content)
        if isinstance(data, list):
            return data
        return [data]
    
    def _parse_csv(self, content: str):
        reader = csv.DictReader(io.StringIO(content))
        return list(reader)
    
    def close(self) -> None:
        pass