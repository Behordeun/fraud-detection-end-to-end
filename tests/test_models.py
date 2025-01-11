import logging

import pytest
from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.linalg import Vectors, VectorUDT
from pyspark.sql import SparkSession
from pyspark.sql.types import DoubleType, StructField, StructType

from src.models.evaluate import evaluate_model
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
