import os
from unittest.mock import MagicMock, patch

import pytest
from pyspark.sql import SparkSession

from src.utils import (
    check_data_quality,
    generate_drift_report,
    get_spark_session,
    handle_error,
    load_config,
    log_artifacts_to_mlflow,
    log_metrics_to_mlflow,
    save_dataframe_as_parquet,
    setup_logging,
    setup_mlflow_experiment,
    upload_to_minio,
    validate_data,
)


@pytest.fixture(scope="module")
def spark():
    """
    Fixture for creating a shared Spark session for tests.
    """
    return SparkSession.builder.appName("TestUtils").master("local[1]").getOrCreate()


# ------------------------------
# Logging and Configuration Tests
# ------------------------------


def test_setup_logging(tmpdir):
    """
    Test that setup_logging creates the log file and configures logging.
    """
    log_file = tmpdir.join("test.log")  # Use a single file directly

    # Call setup_logging
    logger = setup_logging(str(log_file))
    logger.info("This is a test log message.")

    # Print debugging info
    print(f"Expected log file path: {log_file}")
    print(f"Does the directory exist? {os.path.exists(tmpdir)}")

    # Validate that the log file exists
    assert os.path.exists(str(log_file)), f"Log file was not created at {log_file}"

    # Validate that the log message was written
    with open(str(log_file), "r") as f:
        content = f.read()
    assert "This is a test log message." in content


def test_get_spark_session():
    """
    Test that get_spark_session creates a valid SparkSession.
    """
    spark = get_spark_session("TestSparkApp")
    assert spark is not None
    assert spark.version is not None


def test_load_config(tmpdir):
    """
    Test that load_config correctly loads YAML configuration.
    """
    config_content = """
    app:
        name: TestApp
        version: 1.0
    """
    config_file = tmpdir.join("config.yaml")
    config_file.write(config_content)

    config = load_config(str(config_file))
    assert config["app"]["name"] == "TestApp"
    assert config["app"]["version"] == 1.0


# ------------------------------
# Data Validation and Quality Tests
# ------------------------------


def test_validate_data(spark):
    """
    Test that validate_data checks for required columns.
    """
    data = spark.createDataFrame([(1, "A"), (2, "B")], ["id", "category"])

    # Test with valid columns
    assert validate_data(data, ["id", "category"]) is True

    # Test with missing column
    with pytest.raises(
        ValueError, match="Missing required columns: \\['missing_column'\\]"
    ):
        validate_data(data, ["id", "missing_column"])


def test_check_data_quality(spark, capsys):
    """
    Test that check_data_quality identifies missing values and duplicates correctly.
    """
    data = spark.createDataFrame([(1, "A"), (2, None), (1, "A")], ["id", "category"])

    check_data_quality(data)

    captured = capsys.readouterr()
    assert "Total Rows" in captured.out
    assert "Missing Values" in captured.out
    assert "Duplicate Rows" in captured.out


# ------------------------------
# Data Saving Tests
# ------------------------------


def test_save_dataframe_as_parquet(spark, tmpdir):
    """
    Test that save_dataframe_as_parquet writes data to a Parquet file.
    """
    data = spark.createDataFrame([(1, "A"), (2, "B")], ["id", "category"])

    output_path = tmpdir.join("data.parquet")
    save_dataframe_as_parquet(data, str(output_path))

    # Validate the file was created
    assert os.path.exists(output_path)


# ------------------------------
# Error Handling Tests
# ------------------------------


def test_handle_error():
    """
    Test that handle_error raises a CustomError with the correct message.
    """
    with pytest.raises(Exception, match="Test Error Message"):
        handle_error("Test Error Message")


# ------------------------------
# Drift Report Tests
# ------------------------------


def test_generate_drift_report(tmpdir):
    """
    Test that generate_drift_report creates a heatmap image file.
    """
    drift_data = {
        "feature1": {"baseline_mean": 0.5, "current_mean": 0.7, "drift_detected": 1},
        "feature2": {"baseline_mean": 1.0, "current_mean": 1.2, "drift_detected": 0},
    }
    output_path = tmpdir.join("drift_report.png")

    generate_drift_report(drift_data, str(output_path))

    # Validate that the heatmap file was created
    assert os.path.exists(output_path)


# ------------------------------
# MinIO Utilities Tests
# ------------------------------


@patch("src.utils.boto3.client")
def test_connect_to_minio(mock_boto_client):
    """
    Test that connect_to_minio returns a valid MinIO client.
    """
    from src.utils import connect_to_minio

    mock_config = {
        "endpoint_url": "http://localhost:9000",
        "access_key": "minioadmin",
        "secret_key": "minioadmin",
    }

    # Mock client return value
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client

    # Call connect_to_minio
    client = connect_to_minio(mock_config)

    # Validate that the boto3 client was called correctly
    mock_boto_client.assert_called_once_with(
        "s3",
        endpoint_url="http://localhost:9000",
        aws_access_key_id="minioadmin",
        aws_secret_access_key="minioadmin",
    )

    # Validate that the returned client is the mocked one
    assert client == mock_client


@patch("src.utils.boto3.client")
def test_upload_to_minio(mock_boto_client):
    """
    Test that upload_to_minio calls the correct boto3 method.
    """
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client

    upload_to_minio(mock_client, "/path/to/file.txt", "my-bucket", "file.txt")

    # Validate the call to upload_file
    mock_client.upload_file.assert_called_once_with(
        "/path/to/file.txt", "my-bucket", "file.txt"
    )


# ------------------------------
# MLflow Utilities Tests
# ------------------------------


@patch("src.utils.mlflow.set_tracking_uri")
@patch("src.utils.mlflow.set_experiment")
def test_setup_mlflow_experiment(mock_set_experiment, mock_set_tracking_uri):
    """
    Test that setup_mlflow_experiment correctly configures MLflow.
    """
    setup_mlflow_experiment("TestExperiment")

    mock_set_tracking_uri.assert_called_once_with("http://localhost:5000")
    mock_set_experiment.assert_called_once_with("TestExperiment")


@patch("src.utils.mlflow.log_metric")
def test_log_metrics_to_mlflow(mock_log_metric):
    """
    Test that log_metrics_to_mlflow logs metrics correctly.
    """
    metrics = {"accuracy": 0.95, "precision": 0.85}
    log_metrics_to_mlflow(metrics)

    mock_log_metric.assert_any_call("accuracy", 0.95)
    mock_log_metric.assert_any_call("precision", 0.85)


@patch("src.utils.mlflow.log_artifact")
def test_log_artifacts_to_mlflow(mock_log_artifact):
    """
    Test that log_artifacts_to_mlflow logs artifacts correctly.
    """
    log_artifacts_to_mlflow("/path/to/artifact.txt")
    mock_log_artifact.assert_called_once_with("/path/to/artifact.txt")
