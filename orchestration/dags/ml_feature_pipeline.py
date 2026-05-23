"""
Airflow DAG for ML feature engineering
Runs every 6 hours
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'retries': 2,
}

with DAG(
    'ml_feature_pipeline',
    default_args=default_args,
    description='Compute ML features from Gold layer',
    schedule_interval='0 */6 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:
    
    def compute_features(**context):
        import sys
        sys.path.insert(0, '/home/deploy/squad/build-worker/JOB-20260523152746-000047')
        from ml.features import FeatureEngineering
        
        fe = FeatureEngineering()
        features = fe.compute_all_features()
        return features
    
    features_task = PythonOperator(
        task_id='compute_features',
        python_callable=compute_features,
    )
    
    trigger_training = TriggerDagRunOperator(
        task_id='trigger_ml_training',
        trigger_dag_id='ml_training_pipeline',
        wait_for_completion=False,
    )
    
    trigger_inference = TriggerDagRunOperator(
        task_id='trigger_ml_inference',
        trigger_dag_id='ml_inference_pipeline',
        wait_for_completion=False,
    )
    
    features_task >> [trigger_training, trigger_inference]