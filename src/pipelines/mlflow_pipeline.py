import os
import subprocess
import sys

import mlflow  # Import MLflow
from mlflow import log_metric, log_param  # For direct logging if needed

# Add the 'src' directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils import (
    handle_error,
    load_config,
    log_metrics_to_mlflow,
    setup_mlflow_experiment,
)


def run_mlflow_pipeline(config_path: str):
    """
    Executes the MLflow pipeline with parameterized configuration.
    """
    try:
        # Load configuration
        config = load_config(config_path)
        mlflow_config = config["mlflow_pipeline"]

        print("Initializing MLflow pipeline...")
        setup_mlflow_experiment(mlflow_config["experiment_name"])

        # Start an MLflow run
        with mlflow.start_run(
            run_name=mlflow_config.get("run_name", "mlflow_pipeline_run")
        ):
            # Log pipeline-level parameters
            mlflow.log_param("config_path", config_path)

            # Step 1: Train the model
            print("Training the model...")
            subprocess.run(["python", "src/models/train.py"], check=True)

            # Step 2: Evaluate the model
            print("Evaluating the model...")
            subprocess.run(["python", "src/models/evaluate.py"], check=True)

            # Log metrics to MLflow
            print("Logging metrics to MLflow...")
            log_metrics_to_mlflow(mlflow_config["model_metrics"])

            print("MLflow pipeline execution completed.")
    except Exception as e:
        handle_error(f"Error in MLflow pipeline: {str(e)}")
        # Log the error to MLflow if the run has started
        if mlflow.active_run():
            mlflow.log_param("pipeline_error", str(e))
        raise


if __name__ == "__main__":
    CONFIG_PATH = "pipeline_config.yaml"
    run_mlflow_pipeline(CONFIG_PATH)
