import os
import shutil
from unittest.mock import patch

import pytest
from pyspark.ml import PipelineModel
from pyspark.ml.linalg import Vectors, VectorUDT
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    DoubleType,
    Row,
    StringType,
    StructField,
    StructType,
)

from src.models.predict import make_predictions


@pytest.fixture(scope="module")
def spark():
    """
    Pytest fixture to initialize and provide a Spark session.
    The session is shared across tests in the module.
    """
    return SparkSession.builder.master("local[2]").appName("TestPredict").getOrCreate()


@pytest.fixture
def setup_test_data(spark):
    """
    Fixture to set up test data and model paths for the tests.

    Creates:
    - A mock dataset with `engineered_features` column (VectorUDT type) saved in Parquet format.
    - A mock trained model (empty pipeline) saved to disk.
    - An output directory to hold predictions.

    Yields:
    A dictionary containing paths to the input data, model, and output directory.

    Cleans up the test data and output directories after tests.
    """
    # Define the schema for the input data
    schema = StructType([StructField("engineered_features", VectorUDT(), True)])

    # Create mock input data
    data = [
        Row(engineered_features=Vectors.dense([0.1, 0.2, 0.3])),
        Row(engineered_features=Vectors.dense([0.4, 0.5, 0.6])),
        Row(engineered_features=Vectors.dense([0.7, 0.8, 0.9])),
    ]
    input_df = spark.createDataFrame(data, schema)

    # Save input data to Parquet format
    input_path = "test_data/input_data.parquet"
    input_df.write.mode("overwrite").parquet(input_path)

    # Create a mock trained model
    mock_model_path = "test_data/mock_model"
    model = PipelineModel(stages=[])  # Empty pipeline to mock a trained model
    model.write().overwrite().save(mock_model_path)

    # Define an output path
    output_path = "test_data/output_data"
    if os.path.exists(output_path):
        shutil.rmtree(output_path)

    yield {
        "input_path": input_path,
        "model_path": mock_model_path,
        "output_path": output_path,
    }

    # Cleanup test directories
    shutil.rmtree("test_data")


def test_make_predictions_valid_data(spark, setup_test_data):
    """
    Test the make_predictions function with valid input data and a mock model.

    Verifies:
    - The predictions output contains the expected columns.
    - The row count in the predictions matches the input data.
    - A default prediction column is created when the mock model doesn't produce predictions.
    """
    paths = setup_test_data

    # Call the function under test
    make_predictions(
        new_data_path=paths["input_path"],
        model_path=paths["model_path"],
        output_path=paths["output_path"],
    )

    # Load predictions from the output directory
    output_df = spark.read.parquet(paths["output_path"])

    # Validate output columns
    assert "engineered_features" in output_df.columns
    assert "prediction" in output_df.columns

    # Validate row count matches input
    input_df = spark.read.parquet(paths["input_path"])
    assert output_df.count() == input_df.count()

    # Validate default predictions
    assert output_df.filter(output_df["prediction"] == 0.0).count() == input_df.count()


def test_make_predictions_missing_column(spark, setup_test_data):
    """
    Test the make_predictions function raises an error for missing required columns.

    Simulates a dataset missing the required `engineered_features` column and verifies
    that a ValueError is raised.
    """
    paths = setup_test_data

    # Create input data missing the required column
    schema = StructType([StructField("irrelevant_column", DoubleType(), True)])
    invalid_data = spark.createDataFrame([Row(irrelevant_column=1.0)], schema)
    invalid_data_path = "test_data/invalid_input_data.parquet"
    invalid_data.write.mode("overwrite").parquet(invalid_data_path)

    # Expect a ValueError due to missing required columns
    with pytest.raises(ValueError, match="Missing required columns in input data"):
        make_predictions(
            new_data_path=invalid_data_path,
            model_path=paths["model_path"],
            output_path=paths["output_path"],
        )


def test_make_predictions_empty_input(spark, setup_test_data):
    """
    Test the make_predictions function raises an error for empty input data.

    Verifies that an empty input dataset results in a ValueError.
    """
    paths = setup_test_data

    # Create an empty dataset
    empty_df = spark.createDataFrame(
        [], StructType([StructField("engineered_features", VectorUDT(), True)])
    )
    empty_input_path = "test_data/empty_input_data.parquet"
    empty_df.write.mode("overwrite").parquet(empty_input_path)

    # Expect a ValueError due to empty input data
    with pytest.raises(
        ValueError, match="Input data is empty. Cannot proceed with predictions"
    ):
        make_predictions(
            new_data_path=empty_input_path,
            model_path=paths["model_path"],
            output_path=paths["output_path"],
        )


def test_make_predictions_missing_prediction_column(spark, setup_test_data):
    """
    Test the make_predictions function handles missing prediction columns gracefully.

    Verifies that a default prediction column is added when it is missing in the model output.
    """
    paths = setup_test_data

    # Call the function under test
    make_predictions(
        new_data_path=paths["input_path"],
        model_path=paths["model_path"],
        output_path=paths["output_path"],
    )

    # Load predictions and validate
    output_df = spark.read.parquet(paths["output_path"])
    assert "prediction" in output_df.columns
    assert output_df.filter(output_df["prediction"] == 0.0).count() == output_df.count()


@patch("src.models.predict.logging.getLogger")
def test_logging_messages(mock_logger, spark, setup_test_data):
    """
    Test that appropriate logging messages are generated during execution.

    Uses a mock logger to verify that specific log messages are emitted.
    """
    paths = setup_test_data

    # Call the function under test
    make_predictions(
        new_data_path=paths["input_path"],
        model_path=paths["model_path"],
        output_path=paths["output_path"],
    )

    # Verify that key log messages were generated
    mock_logger().info.assert_any_call("Starting predictions process...")
    mock_logger().info.assert_any_call("Loading new data...")


def test_output_partitioning(spark, setup_test_data):
    """
    Test that output data is partitioned correctly by the specified column.

    Verifies that partitioning by `prediction` results in correctly organized output.
    """
    paths = setup_test_data

    # Call the function with partitioning enabled
    make_predictions(
        new_data_path=paths["input_path"],
        model_path=paths["model_path"],
        output_path=paths["output_path"],
        partition_by="prediction",
    )

    # Validate the output directory structure
    assert os.path.exists(f"{paths['output_path']}/prediction=0.0")


def test_invalid_model_path(spark, setup_test_data):
    """
    Test behavior when the model path is invalid or the model cannot be loaded.

    Verifies that an appropriate error is raised.
    """
    paths = setup_test_data

    # Provide an invalid model path
    invalid_model_path = "invalid/path/to/model"

    # Adjust the regex to match the actual exception message
    with pytest.raises(
        Exception, match="Input path does not exist"
    ):
        make_predictions(
            new_data_path=paths["input_path"],
            model_path=invalid_model_path,
            output_path=paths["output_path"],
        )


def test_column_type_validation(spark, setup_test_data):
    """
    Test validation of column types for required columns.

    Simulates a dataset with an incorrect data type for `engineered_features`
    and verifies that a ValueError is raised.
    """
    paths = setup_test_data

    # Create input data with incorrect column type
    invalid_data = spark.createDataFrame(
        [Row(engineered_features="not_a_vector")],
        StructType([StructField("engineered_features", StringType(), True)]),
    )
    invalid_data_path = "test_data/invalid_column_type.parquet"
    invalid_data.write.mode("overwrite").parquet(invalid_data_path)

    with pytest.raises(
        ValueError, match="Column 'engineered_features' must be of type VectorUDT"
    ):
        make_predictions(
            new_data_path=invalid_data_path,
            model_path=paths["model_path"],
            output_path=paths["output_path"],
        )
