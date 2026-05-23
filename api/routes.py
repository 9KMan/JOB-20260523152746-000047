from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter(prefix="/api/v1", tags=["pipeline"])

@router.get("/pipeline/status")
async def get_all_pipeline_status():
    """Get status of all pipelines"""
    return {"status": "implemented"}

@router.get("/sources/{source_id}/health")
async def get_source_health(source_id: str):
    """Get health status of a specific source"""
    return {"source_id": source_id, "status": "healthy"}