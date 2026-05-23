"""
Airflow DAG for data ingestion pipeline
Runs every 15 minutes
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'ingestion_dag',
    default_args=default_args,
    description='Ingest data from all sources',
    schedule_interval='*/15 * * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
) as dag:
    
    def run_ingestion(**context):
        import sys
        sys.path.insert(0, '/home/deploy/squad/build-worker/JOB-20260523152746-000047')
        from ingestion.pipeline import IngestionPipeline
        
        sources = [
            {
                "source_id": "api_source_1",
                "source_type": "rest_api",
                "config": {
                    "base_url": "https://api.example.com",
                    "endpoint": "data",
                    "page_size": 100,
                    "watermark_field": "updated_since"
                }
            },
            {
                "source_id": "db_source_1", 
                "source_type": "sql_database",
                "config": {
                    "connection_string": "postgresql://user:pass@localhost/db",
                    "query": "SELECT * FROM events WHERE updated_at > '{updated_at}'"
                }
            },
            {
                "source_id": "s3_source_1",
                "source_type": "s3",
                "config": {
                    "bucket": "data-bucket",
                    "prefix": "raw/",
                    "format": "json"
                }
            }
        ]
        
        pipeline = IngestionPipeline(
            sources=sources,
            output_path="/tmp/warehouse/bronze"
        )
        result = pipeline.run()
        return result
    
    ingestion_task = PythonOperator(
        task_id='run_ingestion',
        python_callable=run_ingestion,
        provide_context=True,
    )
    
    trigger_transform = TriggerDagRunOperator(
        task_id='trigger_bronze_to_silver',
        trigger_dag_id='transform_bronze_to_silver',
        wait_for_completion=False,
    )
    
    ingestion_task >> trigger_transform