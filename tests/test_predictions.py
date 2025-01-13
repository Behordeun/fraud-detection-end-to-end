import os
from unittest.mock import patch

import pytest
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.linalg import Vectors, VectorUDT
from pyspark.sql import SparkSession
from pyspark.sql.types import DoubleType, Row, StringType, StructField, StructType

from src.models.predict import make_predictions


@pytest.fixture(scope="module")
def spark():
    """
    Pytest fixture to initialize and provide a Spark session.

    This fixture creates a Spark session that is shared across all tests in the module.
    The Spark session is used for creating and manipulating test data.

    Returns:
        SparkSession: A local Spark session for testing.
    """
    return SparkSession.builder.master("local[2]").appName("TestPredict").getOrCreate()


@pytest.fixture
def setup_test_data(tmpdir, spark):
    """
    Fixture to set up test data and model paths for predictions tests.

    This fixture creates:
    - A mock dataset containing a `features` column (VectorUDT type) saved as a Parquet file.
    - A mock trained model (PipelineModel) that includes a simple transformation stage.
    - An output directory to hold the predictions.

    After the test, it cleans up the created files and directories.

    Args:
        tmpdir (LocalPath): A pytest-provided temporary directory for test data isolation.
        spark (SparkSession): The Spark session fixture.

    Yields:
        dict: Paths to the input data, model, and output directory.
    """
    # Create mock input data
    schema = StructType([StructField("features", VectorUDT(), True)])
    data = [
        Row(features=Vectors.dense([0.1, 0.2, 0.3])),
        Row(features=Vectors.dense([0.4, 0.5, 0.6])),
        Row(features=Vectors.dense([0.7, 0.8, 0.9])),
    ]
    input_df = spark.createDataFrame(data, schema)

    # Save input data to Parquet
    input_path = tmpdir.join("input_data.parquet")
    input_df.write.mode("overwrite").parquet(str(input_path))

    # Create a mock trained model
    assembler = VectorAssembler(inputCols=["features"], outputCol="assembled_features")
    pipeline = Pipeline(stages=[assembler])
    pipeline_model = pipeline.fit(input_df)

    # Save the trained PipelineModel
    model_path = tmpdir.mkdir("mock_model")
    pipeline_model.write().overwrite().save(str(model_path))

    # Create output directory
    output_path = tmpdir.mkdir("output_data")

    yield {
        "input_path": str(input_path),
        "model_path": str(model_path),
        "output_path": str(output_path),
    }


def test_make_predictions_valid_data(spark, setup_test_data):
    """
    Test the make_predictions function with valid input data.

    This test ensures:
    - Predictions output contains the expected columns (`features` and `prediction`).
    - The row count in the predictions matches the input data.

    Args:
        spark (SparkSession): The Spark session fixture.
        setup_test_data (dict): Paths to input data, model, and output directory.
    """
    paths = setup_test_data

    # Run the make_predictions function
    make_predictions(
        new_data_path=paths["input_path"],
        model_path=paths["model_path"],
        output_path=paths["output_path"],
    )

    # Load predictions
    output_df = spark.read.parquet(paths["output_path"])

    # Validate output columns
    assert (
        "features" in output_df.columns
    ), "Missing 'features' column in predictions output"
    assert (
        "prediction" in output_df.columns
    ), "Missing 'prediction' column in predictions output"

    # Validate row count
    input_df = spark.read.parquet(paths["input_path"])
    assert (
        output_df.count() == input_df.count()
    ), "Row count mismatch between input and output data"


def test_make_predictions_missing_column(spark, setup_test_data, tmpdir):
    """
    Test the make_predictions function raises an error for missing required columns.

    This test simulates a dataset missing the required `features` column and verifies
    that a ValueError is raised.

    Args:
        spark (SparkSession): The Spark session fixture.
        setup_test_data (dict): Paths to input data, model, and output directory.
    """
    paths = setup_test_data

    # Create invalid input data without the `features` column
    schema = StructType([StructField("irrelevant_column", DoubleType(), True)])
    invalid_df = spark.createDataFrame([Row(irrelevant_column=1.0)], schema)
    invalid_data_path = tmpdir.join("invalid_input_data.parquet")
    invalid_df.write.mode("overwrite").parquet(str(invalid_data_path))

    # Expect a ValueError
    with pytest.raises(ValueError, match="Missing required columns in input data"):
        make_predictions(
            new_data_path=str(invalid_data_path),
            model_path=paths["model_path"],
            output_path=paths["output_path"],
        )


def test_make_predictions_empty_input(spark, setup_test_data, tmpdir):
    """
    Test the make_predictions function raises an error for empty input data.

    This test ensures an empty input dataset results in a ValueError.

    Args:
        spark (SparkSession): The Spark session fixture.
        setup_test_data (dict): Paths to input data, model, and output directory.
    """
    paths = setup_test_data

    # Create an empty dataset
    empty_df = spark.createDataFrame(
        [], StructType([StructField("features", VectorUDT(), True)])
    )
    empty_input_path = tmpdir.join("empty_input_data.parquet")
    empty_df.write.mode("overwrite").parquet(str(empty_input_path))

    # Expect a ValueError
    with pytest.raises(
        ValueError, match="Input data is empty. Cannot proceed with predictions"
    ):
        make_predictions(
            new_data_path=str(empty_input_path),
            model_path=paths["model_path"],
            output_path=paths["output_path"],
        )


def test_make_predictions_missing_prediction_column(spark, setup_test_data):
    """
    Test that missing prediction columns are handled gracefully.

    This test ensures a default prediction column (`0.0`) is created when the model
    does not output a prediction column.

    Args:
        spark (SparkSession): The Spark session fixture.
        setup_test_data (dict): Paths to input data, model, and output directory.
    """
    paths = setup_test_data

    # Run the make_predictions function
    make_predictions(
        new_data_path=paths["input_path"],
        model_path=paths["model_path"],
        output_path=paths["output_path"],
    )

    # Validate default predictions
    output_df = spark.read.parquet(paths["output_path"])
    assert "prediction" in output_df.columns
    assert output_df.filter(output_df["prediction"] == 0.0).count() == output_df.count()


def test_output_partitioning(spark, setup_test_data):
    """
    Test that predictions are correctly partitioned by a specified column.

    This test ensures that when the `partition_by` argument is provided, the
    output data is organized into subdirectories based on the specified column.

    Args:
        spark (SparkSession): The Spark session fixture.
        setup_test_data (dict): Paths to input data, model, and output directory.
    """
    paths = setup_test_data

    # Run the make_predictions function with partitioning enabled
    make_predictions(
        new_data_path=paths["input_path"],
        model_path=paths["model_path"],
        output_path=paths["output_path"],
        partition_by="prediction",
    )

    # Validate partitioning
    assert os.path.exists(
        f"{paths['output_path']}/prediction=0.0"
    ), "Partitioning failed"


def test_invalid_model_path(spark, setup_test_data):
    """
    Test the make_predictions function raises an error for an invalid model path.

    Args:
        spark (SparkSession): The Spark session fixture.
        setup_test_data (dict): Paths to input data, model, and output directory.
    """
    paths = setup_test_data

    # Provide an invalid model path
    invalid_model_path = "invalid/path/to/model"

    # Expect an Exception
    with pytest.raises(Exception, match="Input path does not exist"):
        make_predictions(
            new_data_path=paths["input_path"],
            model_path=invalid_model_path,
            output_path=paths["output_path"],
        )


def test_column_type_validation(spark, setup_test_data, tmpdir):
    """
    Test validation of column types in the input data.

    This test simulates a dataset where the `features` column has an incorrect data
    type and verifies that a ValueError is raised.

    Args:
        spark (SparkSession): The Spark session fixture.
        setup_test_data (dict): Paths to input data, model, and output directory.
    """
    paths = setup_test_data

    # Create input data with incorrect column type
    invalid_data = spark.createDataFrame(
        [Row(features="not_a_vector")],
        StructType([StructField("features", StringType(), True)]),
    )
    invalid_data_path = tmpdir.join("invalid_column_type.parquet")
    invalid_data.write.mode("overwrite").parquet(str(invalid_data_path))

    # Expect a ValueError
    with pytest.raises(ValueError, match="Column 'features' must be of type VectorUDT"):
        make_predictions(
            new_data_path=str(invalid_data_path),
            model_path=paths["model_path"],
            output_path=paths["output_path"],
        )


@patch("src.models.predict.logging.getLogger")
def test_logging_messages(mock_logger, spark, setup_test_data):
    """
    Test that appropriate logging messages are generated during predictions.

    This test uses a mock logger to verify that key log messages are emitted
    during the execution of the make_predictions function.

    Args:
        mock_logger (MagicMock): Mock logger to capture log messages.
        spark (SparkSession): The Spark session fixture.
        setup_test_data (dict): Paths to input data, model, and output directory.
    """
    paths = setup_test_data

    # Run the make_predictions function
    make_predictions(
        new_data_path=paths["input_path"],
        model_path=paths["model_path"],
        output_path=paths["output_path"],
    )

    # Verify log messages
    mock_logger().info.assert_any_call("Starting predictions process...")
    mock_logger().info.assert_any_call("Loading new data...")


def test_output_partitioning(spark, setup_test_data):
    """
    Test that predictions are correctly partitioned by the specified column.

    This test ensures that when the `partition_by` argument is provided, the output data
    is organized into subdirectories based on the specified column (e.g., `prediction`).

    Args:
        spark (SparkSession): The Spark session fixture.
        setup_test_data (dict): Paths to input data, model, and output directory.

    Steps:
        1. Run `make_predictions` with the `partition_by="prediction"` argument.
        2. Verify that the output directory contains subdirectories for each unique value in the `prediction` column.
    """
    paths = setup_test_data

    # Run the `make_predictions` function with partitioning enabled
    make_predictions(
        new_data_path=paths["input_path"],
        model_path=paths["model_path"],
        output_path=paths["output_path"],
        partition_by="prediction",
    )

    # Validate that the output directory is partitioned by the `prediction` column
    partitioned_path = os.path.join(paths["output_path"], "prediction=0.0")
    assert os.path.exists(
        partitioned_path
    ), f"Partitioning by 'prediction' failed: {partitioned_path} does not exist"


def test_invalid_model_path(spark, setup_test_data):
    """
    Test that the `make_predictions` function raises an error for an invalid model path.

    This test simulates the scenario where the provided model path does not exist or the
    model file is corrupted. The function should raise an appropriate exception.

    Args:
        spark (SparkSession): The Spark session fixture.
        setup_test_data (dict): Paths to input data, model, and output directory.

    Steps:
        1. Pass an invalid model path to `make_predictions`.
        2. Expect an exception with an appropriate error message.
    """
    paths = setup_test_data

    # Define an invalid model path
    invalid_model_path = "invalid/path/to/model"

    # Expect an Exception when the model path is invalid
    with pytest.raises(Exception, match="Input path does not exist"):
        make_predictions(
            new_data_path=paths["input_path"],
            model_path=invalid_model_path,
            output_path=paths["output_path"],
        )
