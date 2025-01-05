import logging
import yaml
import os
import boto3
from pyspark.sql import DataFrame
import mlflow
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pyspark.sql.functions import col, count


# Logging Utilities
def setup_logging(log_file: str = "logs/project.log"):
    """
    Set up logging for the project.
    :param log_file: Path to the log file.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(
        filename=log_file,
        filemode="a",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logger = logging.getLogger()
    return logger


# Configuration Utilities
def load_config(config_path: str) -> dict:
    """
    Load a YAML configuration file.
    :param config_path: Path to the YAML configuration file.
    :return: Parsed configuration dictionary.
    """
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config


# Data Validation Utilities
def validate_data(df: DataFrame, required_columns: list) -> bool:
    """
    Validate that the DataFrame contains the required columns.
    :param df: Spark DataFrame to validate.
    :param required_columns: List of required column names.
    :return: True if valid, raises an exception otherwise.
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    return True


def check_data_quality(df: DataFrame):
    """
    Perform basic data quality checks on the DataFrame.
    - Checks for missing values and duplicate rows.
    """
    print("Performing data quality checks...")
    total_rows = df.count()

    # Check for missing values
    missing_counts = df.select([count(col(c)).alias(c) for c in df.columns]).collect()
    missing_report = {col_name: total_rows - count for col_name, count in missing_counts[0].asDict().items()}

    # Check for duplicate rows
    duplicate_rows = total_rows - df.dropDuplicates().count()

    print("Data Quality Report:")
    print(f"Total Rows: {total_rows}")
    print(f"Missing Values: {missing_report}")
    print(f"Duplicate Rows: {duplicate_rows}")


# DataFrame Utilities
def save_dataframe_as_parquet(df: DataFrame, output_path: str):
    """
    Save a Spark DataFrame as a Parquet file.
    :param df: Spark DataFrame to save.
    :param output_path: Path to save the Parquet file.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.write.mode("overwrite").parquet(output_path)


# MinIO Utilities
def connect_to_minio(config: dict):
    """
    Connect to MinIO server.
    :param config: Dictionary with MinIO connection details (endpoint, access key, secret key, bucket name).
    :return: MinIO client.
    """
    return boto3.client(
        "s3",
        endpoint_url=config["endpoint_url"],
        aws_access_key_id=config["access_key"],
        aws_secret_access_key=config["secret_key"],
    )


def upload_to_minio(client, file_path: str, bucket_name: str, object_name: str):
    """
    Upload a file to MinIO bucket.
    :param client: MinIO client.
    :param file_path: Path to the file to upload.
    :param bucket_name: Name of the MinIO bucket.
    :param object_name: Name of the object in MinIO.
    """
    client.upload_file(file_path, bucket_name, object_name)
    print(f"Uploaded {file_path} to MinIO bucket {bucket_name} as {object_name}.")


# MLflow Utilities
def setup_mlflow_experiment(experiment_name: str):
    """
    Set up or retrieve an MLflow experiment.
    :param experiment_name: Name of the MLflow experiment.
    """
    mlflow.set_tracking_uri("http://localhost:5000")  # Update with your MLflow server URL
    mlflow.set_experiment(experiment_name)


def log_metrics_to_mlflow(metrics: dict):
    """
    Log metrics to MLflow.
    :param metrics: Dictionary of metrics to log.
    """
    for metric, value in metrics.items():
        mlflow.log_metric(metric, value)


def log_artifacts_to_mlflow(file_path: str):
    """
    Log artifacts to MLflow.
    :param file_path: Path to the file to log as an artifact.
    """
    mlflow.log_artifact(file_path)


# Monitoring and Visualization Utilities
def generate_drift_report(drift_data: dict, output_path: str):
    """
    Generate and save a drift report as a heatmap.
    :param drift_data: Dictionary containing drift metrics.
    :param output_path: Path to save the heatmap image.
    """
    print("Generating drift heatmap...")
    drift_df = pd.DataFrame(drift_data).T
    plt.figure(figsize=(10, 8))
    sns.heatmap(drift_df, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Data Drift Report")
    plt.savefig(output_path)
    print(f"Drift heatmap saved to {output_path}.")


# Error Handling Utilities
class CustomError(Exception):
    """
    Custom exception class for project-specific errors.
    """
    def __init__(self, message):
        super().__init__(message)
        logging.error(message)


def handle_error(error_message: str):
    """
    Handle and log errors consistently.
    :param error_message: Error message to log.
    """
    raise CustomError(error_message)


if __name__ == "__main__":
    # Example usage of utilities
    logger = setup_logging()
    logger.info("Logger initialized.")

    # Example Drift Report
    drift_data = {"feature1": {"baseline_mean": 0.5, "current_mean": 0.7, "drift_detected": True}}
    generate_drift_report(drift_data, "monitoring_reports/drift_heatmap.png")
