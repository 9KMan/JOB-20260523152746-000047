from .rest_api import RESTAPIConnector
from .sql_database import SQLDatabaseConnector
from .s3 import S3Connector
from .kafka import KafkaConnector

CONNECTOR_MAP = {
    "rest_api": RESTAPIConnector,
    "sql_database": SQLDatabaseConnector,
    "s3": S3Connector,
    "kafka": KafkaConnector,
}

def get_connector(source_type: str, source_id: str, config: dict):
    connector_cls = CONNECTOR_MAP.get(source_type)
    if not connector_cls:
        raise ValueError(f"Unknown connector type: {source_type}")
    return connector_cls(source_id, config)