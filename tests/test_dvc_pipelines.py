from unittest.mock import MagicMock, call, patch

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

    # Use a single "data" directory and create subdirectories
    data_dir = tmpdir.mkdir("data")
    processed_data_dir = data_dir.mkdir("processed")
    raw_data_path = data_dir.mkdir("raw")

    # Update the configuration to use dynamic paths
    updated_config_path = tmpdir.join("pipeline_config.yaml")
    with open(mock_config_path) as f:
        config = (
            f.read()
            .replace("data/raw", str(raw_data_path))
            .replace("data/processed", str(processed_data_dir))
        )
    updated_config_path.write(config)

    # Debugging: Log updated configuration
    print(f"Updated configuration: {updated_config_path.read()}")

    # Run the pipeline
    run_dvc_pipeline(str(updated_config_path))

    # Debugging: Log actual subprocess calls
    print(f"Actual subprocess.run calls: {mock_subprocess_run.call_args_list}")

    # Validate subprocess calls for DVC operations
    expected_calls = [
        call(["dvc", "add", str(raw_data_path)], check=True),
        call(
            [
                "dvc",
                "run",
                "-n",
                "preprocess",
                "-d",
                "src/data_preprocessing/preprocessing.py",
                "-d",
                str(raw_data_path),
                "-o",
                str(processed_data_dir),
                "python src/data_preprocessing/preprocessing.py",
            ],
            check=True,
        ),
    ]
    mock_subprocess_run.assert_has_calls(expected_calls, any_order=False)

    # Validate data quality and drift report generation
    mock_check_data_quality.assert_called_once_with(mock_df)
    mock_generate_drift_report.assert_called_once()
