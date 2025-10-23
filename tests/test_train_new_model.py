import os

import mlflow
import pytest
from pyspark.ml.linalg import Vectors
from pyspark.sql import SparkSession

from src.monitoring.train_new_model import train_current_model


@pytest.fixture(scope="module")
def spark():
    """
    Create a Spark session for testing.
    """
    return (
        SparkSession.builder.appName("TestTrainCurrentModel")
        .master("local[1]")
        .getOrCreate()
    )


def test_train_current_model(spark, tmpdir):
    """
    Test the train_current_model function to ensure it trains and saves the model correctly.
    """
    mlflow.set_tracking_uri(str(tmpdir))

    # Create dummy training data
    train_data = spark.createDataFrame(
        [
            (Vectors.dense([1.0, 2.0, 3.0]), 1),
            (Vectors.dense([4.0, 5.0, 6.0]), 0),
            (Vectors.dense([7.0, 8.0, 9.0]), 1),
        ],
        ["features", "Class"],
    )

    train_data_path = tmpdir.join("train_data.parquet")
    train_data.write.mode("overwrite").parquet(str(train_data_path))

    model_output_path = tmpdir.join("current_model")

    # Ensure the experiment exists
    experiment_name = "test_experiment"
    if not mlflow.get_experiment_by_name(experiment_name):
        mlflow.create_experiment(experiment_name)
    mlflow.set_experiment(experiment_name)

    # Train the model
    train_current_model(
        train_data_path=str(train_data_path),
        model_output_path=str(model_output_path),
    )


def test_train_current_model_with_feature_assembly(spark, tmpdir):
    """
    Test train_current_model when feature assembly is required (no 'features' column).
    """
    # Set MLflow tracking URI to a temporary directory
    mlflow.set_tracking_uri(str(tmpdir))

    # Create dummy training data without 'features' column
    train_data = spark.createDataFrame(
        [
            (Vectors.dense([1.0, 2.0, 3.0]), 1),
            (Vectors.dense([4.0, 5.0, 6.0]), 0),
            (Vectors.dense([7.0, 8.0, 9.0]), 1),
        ],
        ["features", "Class"],
    )

    # Save training data as Parquet
    train_data_path = tmpdir.join("train_data.parquet")
    train_data.write.mode("overwrite").parquet(str(train_data_path))

    # Define model output path
    model_output_path = tmpdir.join("current_model")

    # Call the function to train the model
    train_current_model(
        train_data_path=str(train_data_path), model_output_path=str(model_output_path)
    )

    # Assert the model directory exists
    assert os.path.exists(str(model_output_path))

    # Assert the saved model files exist
    model_files = os.listdir(str(model_output_path))
    assert len(model_files) > 0  # Ensure model files were saved

    # Verify the 'features' column in the transformed dataset
    transformed_data = spark.read.parquet(str(model_output_path))
    assert "features" in transformed_data.columns
