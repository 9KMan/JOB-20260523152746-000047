"""
Airflow DAG for Bronze to Silver transformation
Runs every hour
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'retries': 2,
    'retry_delay': timedelta(minutes=3),
}

with DAG(
    'transform_bronze_to_silver',
    default_args=default_args,
    description='Transform Bronze to Silver layer',
    schedule_interval='0 * * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
) as dag:
    
    def run_dbt_silver(**context):
        import subprocess
        result = subprocess.run(
            ['dbt', 'run', '--project-dir', '/home/deploy/squad/build-worker/JOB-20260523152746-000047/storage/silver', '--target', 'dev'],
            capture_output=True,
            text=True,
            cwd='/home/deploy/squad/build-worker/JOB-20260523152746-000047/storage/silver'
        )
        if result.returncode != 0:
            raise Exception(f"dbt silver failed: {result.stderr}")
        return result.stdout
    
    dbt_silver_task = PythonOperator(
        task_id='run_dbt_silver_transform',
        python_callable=run_dbt_silver,
    )
    
    run_tests = PythonOperator(
        task_id='run_dbt_tests',
        python_callable=lambda **context: subprocess.run(
            ['dbt', 'test', '--project-dir', '/home/deploy/squad/build-worker/JOB-20260523152746-000047/storage/silver'],
            capture_output=True,
        ),
    )
    
    trigger_gold = TriggerDagRunOperator(
        task_id='trigger_silver_to_gold',
        trigger_dag_id='transform_silver_to_gold',
        wait_for_completion=False,
    )
    
    dbt_silver_task >> run_tests >> trigger_gold