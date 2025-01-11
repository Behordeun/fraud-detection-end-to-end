from unittest.mock import MagicMock, patch

import pytest
from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.linalg import DenseVector, Vectors
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import DoubleType

from src.models.evaluate import evaluate_model
from src.models.predict import make_predictions
from src.models.train import train_model


@pytest.fixture(scope="module")
def spark():
    """
    Fixture for creating a shared Spark session for tests.
    """
    return SparkSession.builder.appName("TestSpark").master("local[1]").getOrCreate()


def test_train_model(spark, tmpdir):
    """
    Test the train_model function with valid data.
    """
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
    assert model_output_path.check()


def test_evaluate_model(spark, tmpdir):
    """
    Test the evaluate_model function with valid test data.
    """
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
    assert 0.0 <= auc <= 1.0


@patch("pyspark.sql.DataFrameReader.parquet")
@patch("src.models.predict.PipelineModel.load")
def test_make_predictions(mock_model_load, mock_read_parquet, spark, tmpdir):
    """
    Test the make_predictions function end-to-end.
    """
    # Mock new data
    new_data = spark.createDataFrame(
        [
            (Vectors.dense([1.0, 2.0, 3.0]),),
            (Vectors.dense([4.0, 5.0, 6.0]),),
        ],
        ["engineered_features"],
    )
    mock_read_parquet.return_value = new_data

    # Create a mock DataFrame with predictions
    mock_predictions = spark.createDataFrame(
        [
            (Vectors.dense([1.0, 2.0, 3.0]), 0.5),
            (Vectors.dense([4.0, 5.0, 6.0]), 0.8),
        ],
        ["engineered_features", "prediction"],
    )

    # Mock model
    mock_model = MagicMock()
    mock_model.transform.return_value = mock_predictions
    mock_model_load.return_value = mock_model

    # Temporary paths
    input_path = tmpdir.join("new_data.parquet")
    model_path = tmpdir.join("model")
    output_path = tmpdir.join("predictions.parquet")

    # Write mock data to input path
    new_data.write.parquet(str(input_path))

    # Call make_predictions
    make_predictions(str(input_path), str(model_path), str(output_path))

    # Validate that parquet file was read
    mock_read_parquet.assert_called_once_with(str(input_path))

    # Validate that the model was loaded
    mock_model_load.assert_called_once_with(str(model_path))

    # Validate that predictions were saved
    saved_data = spark.read.parquet(str(output_path))

    # Explicitly overwrite the output path for testing
    saved_data.select("*").write.mode("overwrite").parquet(str(output_path))

    # Validate the saved data
    saved_data = spark.read.parquet(str(output_path))
    assert "engineered_features" in saved_data.columns
    assert "prediction" in saved_data.columns
    assert saved_data.count() == new_data.count()
