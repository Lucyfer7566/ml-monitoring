from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'ml_admin',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def train_and_register_model():
    """Trains the model and registers it to MLFlow."""
    import mlflow
    import mlflow.sklearn
    from sklearn.datasets import load_wine
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
    import os

    # Configure MLFlow for docker-compose internal networking
    MLFLOW_TRACKING_URI = 'http://mlflow:5000'
    MODEL_NAME = "wine_quality_model"
    EXPERIMENT_NAME = "wine_quality_experiment"

    # Configure MinIO S3 for artifacts
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://minio:9000'
    os.environ['AWS_ACCESS_KEY_ID'] = 'minio'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'minio123'
    os.environ['MLFLOW_S3_IGNORE_TLS'] = 'true'

    print(f"🔧 MLFlow Tracking URI: {MLFLOW_TRACKING_URI}")
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    print("📊 Loading wine dataset...")
    wine = load_wine()
    X, y = wine.data, wine.target

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("\n🎯 Training model...")
    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run(run_name="RandomForest_Pipeline") as run:
        params = {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 2,
            'random_state': 42
        }
        
        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        print(f"\n📈 Model Performance: Accuracy={accuracy:.4f}, F1={f1:.4f}")
        
        mlflow.log_params(params)
        mlflow.log_metrics({
            'accuracy': accuracy,
            'f1_score': f1
        })
        
        mlflow.sklearn.log_model(
            model,
            artifact_path="model",
            registered_model_name=MODEL_NAME,
            signature=mlflow.models.infer_signature(X_train, y_pred),
            input_example=X_train[:5]
        )
        run_id = run.info.run_id

    print("\n Promoting model to Production stage...")
    client = mlflow.tracking.MlflowClient()
    model_versions = client.get_latest_versions(MODEL_NAME, stages=["None"])

    if model_versions:
        latest_version = model_versions[0].version
        client.transition_model_version_stage(
            name=MODEL_NAME,
            version=latest_version,
            stage="Production",
            archive_existing_versions=True
        )
        print(f"✅ Model promoted to Production! Version: {latest_version}")
    else:
        print("❌ No model versions found")

with DAG(
    'ml_training_pipeline',
    default_args=default_args,
    description='A data pipeline to train model and log to MLFlow',
    schedule_interval=timedelta(days=1),
    catchup=False
) as dag:
    
    train_model_task = PythonOperator(
        task_id='train_and_register_model',
        python_callable=train_and_register_model,
    )

    train_model_task
