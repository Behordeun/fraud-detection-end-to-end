from unittest.mock import patch

import pytest

from src.pipelines.mlflow_pipeline import run_mlflow_pipeline


@pytest.fixture
def mock_config_path(tmpdir):
    """
    Create a mock pipeline configuration file.
    """
    config_file = tmpdir.join("pipeline_config.yaml")
    config_file.write(
        """
        mlflow_pipeline:
            experiment_name: "Credit Card Fraud Detection"
            model_metrics:
                auc: 0.95
                accuracy: 0.92
        """
    )
    return str(config_file)


@patch("src.pipelines.mlflow_pipeline.subprocess.run")
@patch("src.pipelines.mlflow_pipeline.setup_mlflow_experiment")
@patch("src.pipelines.mlflow_pipeline.log_metrics_to_mlflow")
def test_run_mlflow_pipeline(
    mock_log_metrics_to_mlflow,
    mock_setup_mlflow_experiment,
    mock_subprocess_run,
    mock_config_path,
):
    """
    Test the MLflow pipeline with mocked dependencies.
    """
    run_mlflow_pipeline(mock_config_path)

    # Validate subprocess calls
    mock_subprocess_run.assert_any_call(["python", "src/models/train.py"], check=True)
    mock_log_metrics_to_mlflow.assert_called_once_with({"auc": 0.95, "accuracy": 0.92})
