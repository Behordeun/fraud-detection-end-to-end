import os
from unittest.mock import MagicMock, patch

import pytest

from src.pipelines.dvc_pipeline import run_dvc_pipeline


@pytest.fixture
def mock_config_path(tmpdir):
    """
    Create a mock pipeline configuration file.
    """
    config_file = tmpdir.join("pipeline_config.yaml")
    config_file.write(
        """
        dvc_pipeline:
            raw_data_path: "data/raw"
            processed_data_path: "data/processed"
            engineered_data_path: "data/processed/engineered"
            drift_report_path: "monitoring_reports/data_drift_heatmap.png"
        """
    )
    return str(config_file)


@patch("src.pipelines.dvc_pipeline.subprocess.run")
@patch("src.pipelines.dvc_pipeline.get_spark_session")
@patch("src.pipelines.dvc_pipeline.check_data_quality")
@patch("src.pipelines.dvc_pipeline.generate_drift_report")
def test_run_dvc_pipeline(
    mock_generate_drift_report,
    mock_check_data_quality,
    mock_get_spark_session,
    mock_subprocess_run,
    mock_config_path,
    tmpdir,
):
    """
    Test the DVC pipeline with mocked dependencies.
    """
    # Mock Spark session and DataFrame
    mock_spark = MagicMock()
    mock_df = MagicMock()
    mock_get_spark_session.return_value = mock_spark
    mock_spark.read.parquet.return_value = mock_df

    # Create the directory expected by the pipeline
    processed_data_dir = tmpdir.mkdir("data").mkdir("processed").mkdir("train")

    # Run the pipeline
    run_dvc_pipeline(mock_config_path)

    # Validate subprocess calls
    mock_subprocess_run.assert_any_call(["dvc", "add", "data/raw"], check=True)
    mock_subprocess_run.assert_any_call(
        [
            "dvc",
            "run",
            "-n",
            "preprocess",
            "-d",
            "src/data_preprocessing/preprocessing.py",
            "-d",
            "data/raw",
            "-o",
            "data/processed",
            "python src/data_preprocessing/preprocessing.py",
        ],
        check=True,
    )

    # Validate Spark session and data quality checks
    mock_get_spark_session.assert_called_once_with("DataQualityCheck")
    mock_check_data_quality.assert_called_once_with(mock_df)

    # Validate drift report generation
    mock_generate_drift_report.assert_called_once()
