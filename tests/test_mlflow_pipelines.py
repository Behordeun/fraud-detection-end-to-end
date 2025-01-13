import logging
from unittest.mock import MagicMock, call, patch

import pytest

from src.pipelines.mlflow_pipeline import run_mlflow_pipeline

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


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
            tracking_uri: "http://localhost:5000"
            model_metrics:
                auc: 0.95
                accuracy: 0.92
        """
    )
    return str(config_file)


@patch("src.pipelines.mlflow_pipeline.subprocess.run")
@patch("src.pipelines.mlflow_pipeline.setup_mlflow_experiment")
@patch("src.pipelines.mlflow_pipeline.log_metrics_to_mlflow")
@patch("src.pipelines.mlflow_pipeline.mlflow")
def test_run_mlflow_pipeline(
    mock_mlflow,
    mock_log_metrics_to_mlflow,
    mock_setup_mlflow_experiment,
    mock_subprocess_run,
    mock_config_path,
):
    """
    Test the MLflow pipeline with mocked dependencies.
    """
    # Mock MLflow client
    mock_mlflow_client = MagicMock()
    mock_mlflow.tracking.MlflowClient.return_value = mock_mlflow_client

    # Call the pipeline
    run_mlflow_pipeline(mock_config_path)

    # Debug log for MlflowClient usage
    logger.debug(
        f"MLflowClient call count: {mock_mlflow.tracking.MlflowClient.call_count}"
    )

    # Validate subprocess calls
    expected_calls = [
        call(["python", "src/models/train.py"], check=True),
        call(["python", "src/models/evaluate.py"], check=True),
    ]
    mock_subprocess_run.assert_has_calls(expected_calls, any_order=False)

    # Validate MLflow setup
    mock_setup_mlflow_experiment.assert_called_once_with("Credit Card Fraud Detection")

    # Validate metrics logging
    mock_log_metrics_to_mlflow.assert_called_once_with({"auc": 0.95, "accuracy": 0.92})

    # Ensure MLflow client interactions are mocked
    if mock_mlflow.tracking.MlflowClient.call_count > 0:
        mock_mlflow.tracking.MlflowClient.assert_called_once()
