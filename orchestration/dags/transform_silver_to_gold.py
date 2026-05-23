"""
Airflow DAG for Silver to Gold transformation
Runs every hour
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'retries': 2,
}

with DAG(
    'transform_silver_to_gold',
    default_args=default_args,
    description='Transform Silver to Gold layer',
    schedule_interval='30 * * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
) as dag:
    
    def run_dbt_gold(**context):
        import subprocess
        result = subprocess.run(
            ['dbt', 'run', '--project-dir', '/home/deploy/squad/build-worker/JOB-20260523152746-000047/storage/gold', '--target', 'dev'],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise Exception(f"dbt gold failed: {result.stderr}")
        return result.stdout
    
    dbt_gold_task = PythonOperator(
        task_id='run_dbt_gold_transform',
        python_callable=run_dbt_gold,
    )
    
    dbt_gold_task