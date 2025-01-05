from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from src.pipelines.dvc_pipeline import run_dvc_pipeline
from src.pipelines.mlflow_pipeline import run_mlflow_pipeline


CONFIG_PATH = "../src/pipelines/pipeline_config.yml"

default_args = {
    "owner": "behordeun",
    "depends_on_past": False,
    "start_date": datetime(2025, 1, 1),
    "retries": 1,
}

dag = DAG(
    "dvc_mlflow_pipeline",
    default_args=default_args,
    description="A DAG to execute DVC and MLflow pipelines",
    schedule_interval="@daily",
)

dvc_pipeline = PythonOperator(
    task_id="run_dvc_pipeline",
    python_callable=run_dvc_pipeline,
    op_args=[CONFIG_PATH],
    dag=dag,
)

mlflow_pipeline = PythonOperator(
    task_id="run_mlflow_pipeline",
    python_callable=run_mlflow_pipeline,
    op_args=[CONFIG_PATH],
    dag=dag,
)

dvc_pipeline >> mlflow_pipeline
