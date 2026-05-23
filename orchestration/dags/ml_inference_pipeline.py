"""
Airflow DAG for ML batch inference
Runs every 15 minutes
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'retries': 2,
}

with DAG(
    'ml_inference_pipeline',
    default_args=default_args,
    description='Run batch inference on new records',
    schedule_interval='*/15 * * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:
    
    def run_inference(**context):
        import sys
        sys.path.insert(0, '/home/deploy/squad/build-worker/JOB-20260523152746-000047')
        from ml.inference import BatchInference
        
        bi = BatchInference()
        results = bi.run()
        return results
    
    inference_task = PythonOperator(
        task_id='run_inference',
        python_callable=run_inference,
    )
    
    inference_task