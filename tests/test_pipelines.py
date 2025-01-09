import os
import sys

import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from src.pipelines.dvc_pipeline import run_dvc_pipeline
from src.pipelines.mlflow_pipeline import run_mlflow_pipeline


@pytest.fixture
def mock_config_path(tmpdir):
    # Create a mock pipeline configuration
    config_file = tmpdir.join("pipeline_config.yaml")
    config_file.write(
        """
    dvc_pipeline:
        raw_data_path: "data/raw"
        processed_data_path: "data/processed"
        engineered_data_path: "data/processed/engineered"
        drift_report_path: "monitoring_reports/data_drift_heatmap.png"

    mlflow_pipeline:
        experiment_name: "Credit Card Fraud Detection"
        model_metrics:
        auc: 0.95
        accuracy: 0.92
    """
    )
    return str(config_file)


def test_run_dvc_pipeline(mock_config_path):
    # Test the DVC pipeline
    run_dvc_pipeline(mock_config_path)


def test_run_mlflow_pipeline(mock_config_path):
    # Test the MLflow pipeline
    run_mlflow_pipeline(mock_config_path)
