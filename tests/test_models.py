import logging
from unittest.mock import MagicMock, patch

import pytest
from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.linalg import Vectors, VectorUDT
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, rand
from pyspark.sql.types import DoubleType, StructField, StructType

from src.models.evaluate import evaluate_model
from src.models.predict import make_predictions
from src.models.train import train_model

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)



@pytest.fixture(scope="module")
def spark():
    """
    Fixture for creating a shared Spark session for tests.
    """
    return SparkSession.builder.appName("TestSpark").master("local[1]").getOrCreate()


def get_spark_session():
    """
    Ensure Spark session is active or create a new one.
    """
    spark = SparkSession.getActiveSession()
    if spark is None:
        spark = (
            SparkSession.builder.appName("TestSpark").master("local[1]").getOrCreate()
        )
    return spark


def test_train_model(spark, tmpdir):
    """
    Test the train_model function with valid data.
    """
    logger.info("Starting test_train_model...")

    # Create sample training data
    train_data = spark.createDataFrame(
        [
            (0, Vectors.dense([1.0, 2.0, 3.0])),
            (1, Vectors.dense([2.0, 3.0, 4.0])),
        ],
        ["label", "engineered_features"],
    )

    # Write training data to a temporary Parquet file
    train_data_path = tmpdir.join("train_data.parquet")
    train_data.write.parquet(str(train_data_path))

    # Define model output path
    model_output_path = tmpdir.mkdir("models").join("rf_model")

    # Call train_model
    train_model(str(train_data_path), str(model_output_path))

    # Validate that the model was saved
    assert model_output_path.check(), "Model output path does not exist"
    assert len(list(model_output_path.listdir())) > 0, "Model output path is empty"
    logger.info("test_train_model passed successfully.")


def test_evaluate_model(spark, tmpdir):
    """
    Test the evaluate_model function with valid test data.
    """
    logger.info("Starting test_evaluate_model...")

    # Create sample test data
    test_data = spark.createDataFrame(
        [
            (0, Vectors.dense([1.0, 2.0, 3.0])),
            (1, Vectors.dense([2.0, 3.0, 4.0])),
        ],
        ["label", "engineered_features"],
    )

    # Write test data to a temporary Parquet file
    test_data_path = tmpdir.join("test_data.parquet")
    test_data.write.parquet(str(test_data_path))

    # Train a dummy Pipeline model
    rf = RandomForestClassifier(
        featuresCol="engineered_features", labelCol="label", numTrees=5
    )
    pipeline = Pipeline(stages=[rf])
    pipeline_model = pipeline.fit(test_data)

    # Save the PipelineModel
    model_path = tmpdir.mkdir("models").join("pipeline_model")
    pipeline_model.write().overwrite().save(str(model_path))

    # Evaluate the model
    auc = evaluate_model(str(test_data_path), str(model_path))

    # Validate the AUC metric
    assert 0.0 <= auc <= 1.0, f"AUC metric {auc} is outside the valid range [0.0, 1.0]"
    logger.info("test_evaluate_model passed successfully.")


@patch("pyspark.sql.DataFrameReader.parquet")
@patch("src.models.predict.PipelineModel.load")
def test_make_predictions(mock_model_load, mock_read_parquet, spark, tmpdir):
    """
    Test the make_predictions function end-to-end.
    """
    logger.info("Starting test_make_predictions...")

    # Mock input data
    new_data = spark.createDataFrame(
        [
            (Vectors.dense([1.0, 2.0, 3.0]),),
            (Vectors.dense([4.0, 5.0, 6.0]),),
        ],
        ["engineered_features"],
    )
    mock_read_parquet.return_value = new_data

    # Mock predictions
    mock_predictions = spark.createDataFrame(
        [
            (Vectors.dense([1.0, 2.0, 3.0]), 0.5),
            (Vectors.dense([4.0, 5.0, 6.0]), 0.8),
        ],
        StructType(
            [
                StructField("engineered_features", VectorUDT(), True),
                StructField("prediction", DoubleType(), True),
            ]
        ),
    )
    mock_model = MagicMock()
    mock_model.transform.return_value = mock_predictions
    mock_model_load.return_value = mock_model

    # Paths
    input_path = tmpdir.join("new_data.parquet")
    model_path = tmpdir.join("model")
    output_path = tmpdir.join("predictions.parquet")

    # Write mock data to input path
    new_data.write.parquet(str(input_path))

    # Call make_predictions
    make_predictions(
        new_data_path=str(input_path),
        model_path=str(model_path),
        output_path=str(output_path),
        partition_by="prediction",
        required_columns=["engineered_features"],
        output_columns=["engineered_features", "prediction"],
    )

    # Validate saved predictions
    saved_data = spark.read.parquet(str(output_path))
    logger.debug(f"Saved predictions schema: {saved_data.schema}")
    logger.debug(f"Saved predictions row count: {saved_data.count()}")

    # Assertions
    required_columns = ["engineered_features", "prediction"]
    actual_columns = saved_data.columns
    for col in required_columns:
        assert col in actual_columns, f"Missing '{col}' in saved predictions"
    assert saved_data.count() == new_data.count(), "Row count mismatch between input and saved predictions"

    logger.info("test_make_predictions passed successfully.")


@pytest.mark.parametrize("num_rows", [10, 1000, 100000])
@patch("src.models.train_model")
@patch("src.models.make_predictions")
def test_large_data_predictions(
    mock_make_predictions, mock_train_model, tmpdir, num_rows
):
    """
    Test predictions with datasets of varying sizes to validate scalability.
    """
    logger.info(f"Starting test_large_data_predictions with {num_rows} rows...")

    # Get Spark session
    spark = get_spark_session()

    # UDF to convert arrays to vectors
    @udf(VectorUDT())
    def array_to_vector(arr):
        return Vectors.dense(arr)

    # Generate synthetic large data
    large_data = (
        spark.range(num_rows)
        .selectExpr("id as label", "array(rand(), rand(), rand()) as array_features")
        .withColumn("engineered_features", array_to_vector(col("array_features")))
        .drop("array_features")
    )
    logger.debug(f"Generated large_data schema: {large_data.schema}")

    # Paths
    data_path = tmpdir.join("large_data.parquet")
    model_path = tmpdir.mkdir("models").join("pipeline_model")
    output_path = tmpdir.join("large_predictions.parquet")

    # Save large data
    large_data.write.mode("overwrite").parquet(str(data_path))
    logger.debug(f"Large data saved to: {data_path}")

    # Mock train_model and make_predictions
    mock_train_model.return_value = None
    mock_make_predictions.return_value = None

    # Call train_model and make_predictions
    train_model(str(data_path), str(model_path))
    make_predictions(str(data_path), str(model_path), str(output_path))

    # Load and validate saved predictions
    saved_data = spark.read.parquet(str(output_path))
    logger.debug(f"Saved predictions schema: {saved_data.schema}")

    # Validate row count
    assert (
        saved_data.count() == num_rows
    ), f"Expected {num_rows} predictions, got {saved_data.count()}"

    # Validate presence of required columns
    required_columns = {"label", "engineered_features", "prediction"}
    actual_columns = set(saved_data.columns)
    assert required_columns.issubset(
        actual_columns
    ), f"Missing required columns: {required_columns - actual_columns}"

    # Validate schema
    schema = saved_data.schema
    assert (
        schema["engineered_features"].dataType == VectorUDT()
    ), "engineered_features column is not VectorUDT"
    assert (
        schema["prediction"].dataType == DoubleType()
    ), "prediction column is not DoubleType"

    logger.info(f"test_large_data_predictions passed successfully for {num_rows} rows.")


def test_train_with_empty_data(spark, tmpdir):
    """
    Test training with an empty dataset.
    """
    logger.info("Starting test_train_with_empty_data...")

    spark = get_spark_session()

    # Define schema explicitly
    schema = StructType(
        [
            StructField("label", DoubleType(), True),
            StructField("engineered_features", VectorUDT(), True),
        ]
    )

    # Create empty DataFrame
    empty_data = spark.createDataFrame([], schema)
    assert empty_data.schema == schema, "Schema mismatch in empty_data DataFrame"

    # Save the empty dataset to Parquet
    train_data_path = tmpdir.join("train_data.parquet")
    empty_data.write.parquet(str(train_data_path))
    logger.debug(f"Empty dataset saved to: {train_data_path}")

    # Define model output path
    model_output_path = tmpdir.mkdir("models").join("rf_model")
    logger.debug(f"Model output path: {model_output_path}")

    # Expect an exception when training with empty data
    with pytest.raises(Exception, match=".*empty data.*") as exc_info:
        train_model(str(train_data_path), str(model_output_path))

    # Log details of the exception
    logger.debug(f"Exception raised: {exc_info.value}")
    logger.info("test_train_with_empty_data passed successfully.")
