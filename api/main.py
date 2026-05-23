"""
Data Pipeline API Service
FastAPI-based REST API for pipeline management
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Data Pipeline API",
    description="API for managing data aggregation pipeline",
    version="1.0.0"
)

# In-memory state (replace with database in production)
pipeline_state = {
    "dags": {},
    "sources": [],
    "reports": []
}

class PipelineTrigger(BaseModel):
    dag_id: str
    run_config: Optional[dict] = None

class SourceRegistration(BaseModel):
    source_id: str
    source_type: str
    config: dict
    schema: Optional[dict] = None

class ReportCreate(BaseModel):
    name: str
    query: str
    schedule: str
    recipients: List[str]
    format: str = "pdf"

@app.get("/")
async def root():
    return {"status": "ok", "service": "data-pipeline-api", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/v1/pipeline/trigger")
async def trigger_pipeline(trigger: PipelineTrigger, background_tasks: BackgroundTasks):
    """Manually trigger a DAG run"""
    logger.info(f"Triggering DAG: {trigger.dag_id}")

    def run_dag():
        # Import here to avoid circular imports
        import sys
        sys.path.insert(0, '/home/deploy/squad/build-worker/JOB-20260523152746-000047')
        from ingestion.pipeline import IngestionPipeline
        # In production, trigger Airflow DAG via API
        pipeline = IngestionPipeline(sources=[], output_path="/tmp/warehouse/bronze")
        return pipeline.run()

    if trigger.dag_id.startswith("ingestion"):
        background_tasks.add_task(run_dag)

    pipeline_state["dags"][trigger.dag_id] = {
        "status": "triggered",
        "triggered_at": datetime.utcnow().isoformat(),
        "config": trigger.run_config
    }

    return {
        "dag_id": trigger.dag_id,
        "status": "triggered",
        "message": f"DAG {trigger.dag_id} has been triggered"
    }

@app.get("/api/v1/pipeline/status/{dag_id}")
async def get_pipeline_status(dag_id: str):
    """Get DAG run status"""
    dag_state = pipeline_state["dags"].get(dag_id)
    if not dag_state:
        raise HTTPException(status_code=404, detail=f"DAG {dag_id} not found")
    return dag_state

@app.get("/api/v1/sources")
async def list_sources():
    """List registered data sources"""
    return {"sources": pipeline_state["sources"]}

@app.post("/api/v1/sources")
async def register_source(source: SourceRegistration):
    """Register a new data source"""
    # Validate source type
    valid_types = ["rest_api", "sql_database", "s3", "kafka"]
    if source.source_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid source type. Must be one of: {valid_types}"
        )

    pipeline_state["sources"].append({
        **source.dict(),
        "registered_at": datetime.utcnow().isoformat()
    })

    return {
        "source_id": source.source_id,
        "status": "registered",
        "message": f"Source {source.source_id} registered successfully"
    }

@app.get("/api/v1/reports")
async def list_reports():
    """List scheduled reports"""
    return {"reports": pipeline_state["reports"]}

@app.post("/api/v1/reports")
async def create_report(report: ReportCreate):
    """Create a scheduled report"""
    report_dict = {
        **report.dict(),
        "created_at": datetime.utcnow().isoformat(),
        "status": "active"
    }
    pipeline_state["reports"].append(report_dict)

    return {
        "name": report.name,
        "status": "created",
        "message": f"Report {report.name} created successfully"
    }

@app.get("/api/v1/metrics/summary")
async def get_metrics_summary():
    """Get aggregate pipeline metrics"""
    total_sources = len(pipeline_state["sources"])
    total_reports = len(pipeline_state["reports"])

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "total_sources": total_sources,
        "total_reports": total_reports,
        "active_dags": len([d for d in pipeline_state["dags"].values() if d.get("status") == "triggered"]),
        "metrics": {
            "bronze_records_today": 0,
            "silver_records_today": 0,
            "gold_records_today": 0,
            "error_rate": 0.0
        }
    }

@app.get("/api/v1/health")
async def detailed_health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "components": {
            "api": "healthy",
            "database": "healthy",
            "storage": "healthy",
            "orchestration": "healthy"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)