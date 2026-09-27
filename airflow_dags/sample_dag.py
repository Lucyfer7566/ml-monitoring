from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import requests

default_args = {
    'owner': 'ml_admin',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def check_api_health():
    """Check if the model serving API is healthy."""
    # The API is running on the 'api' container port 8000
    try:
        response = requests.get('http://api:8000/health')
        response.raise_for_status()
        print(f"API is healthy: {response.json()}")
        return True
    except Exception as e:
        print(f"Failed to check API health: {e}")
        raise

with DAG(
    'ml_monitoring_health_check',
    default_args=default_args,
    description='A simple DAG to check API health periodically',
    schedule_interval=timedelta(hours=1),
    catchup=False
) as dag:
    
    health_check_task = PythonOperator(
        task_id='check_api_health',
        python_callable=check_api_health,
    )

    health_check_task
