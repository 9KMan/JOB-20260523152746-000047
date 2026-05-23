from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class DagRunResponse(BaseModel):
    dag_id: str
    run_id: Optional[str] = None
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None

class SourceResponse(BaseModel):
    source_id: str
    source_type: str
    source_name: Optional[str] = None
    status: str
    last_ingested: Optional[datetime] = None
    record_count: int = 0

class ReportResponse(BaseModel):
    report_id: str
    name: str
    schedule: str
    recipients: List[str]
    format: str
    status: str
    last_run: Optional[datetime] = None

class MetricsResponse(BaseModel):
    timestamp: datetime
    total_records_processed: int
    error_count: int
    error_rate: float
    avg_latency_ms: float
    sources_by_type: Dict[str, int]