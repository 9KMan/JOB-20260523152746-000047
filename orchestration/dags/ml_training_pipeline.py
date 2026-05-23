"""
Airflow DAG for ML model training
Runs daily
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'retries': 1,
}

with DAG(
    'ml_training_pipeline',
    default_args=default_args,
    description='Train ML models',
    schedule_interval='0 2 * * *',  # 2 AM daily
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:
    
    def train_models(**context):
        import sys
        sys.path.insert(0, '/home/deploy/squad/build-worker/JOB-20260523152746-000047')
        from ml.training import ModelTraining
        
        mt = ModelTraining()
        results = mt.train_all_models()
        return results
    
    train_task = PythonOperator(
        task_id='train_models',
        python_callable=train_models,
    )
    
    train_task