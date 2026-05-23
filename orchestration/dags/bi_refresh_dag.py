"""
Airflow DAG for BI dashboard refresh
Runs every hour
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'bi-team',
    'depends_on_past': False,
}

with DAG(
    'bi_refresh_dag',
    default_args=default_args,
    description='Refresh BI dashboards',
    schedule_interval='0 * * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:
    
    def refresh_dashboards(**context):
        import subprocess
        # Refresh Metabase dashboards
        result = subprocess.run(
            ['python3', '-c', 'import requests; requests.post("http://metabase:3000/api/card/1/query")'],
            capture_output=True
        )
        return result.stdout
    
    refresh_task = PythonOperator(
        task_id='refresh_dashboards',
        python_callable=refresh_dashboards,
    )
    
    refresh_task