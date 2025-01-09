import pytest
from pyspark.ml.classification import RandomForestClassifier
from pyspark.sql import SparkSession

from src.models.evaluate import evaluate_model
from src.models.train import train_model


@pytest.fixture(scope="module")
def spark():
    return SparkSession.builder.appName("TestSpark").getOrCreate()


def test_train_model(spark, tmpdir):
    # Sample training data
    train_data = spark.createDataFrame(
        [(0, [1.0, 2.0]), (1, [2.0, 3.0]), (0, [3.0, 4.0])], ["label", "features"]
    )

    model_output_path = tmpdir.mkdir("models").join("rf_model")
    train_model(train_data, str(model_output_path))

    # Validate that model is saved
    assert model_output_path.check()


def test_evaluate_model(spark, tmpdir):
    # Sample test data
    test_data = spark.createDataFrame(
        [(0, [1.0, 2.0]), (1, [2.0, 3.0])], ["label", "features"]
    )

    # Load a pre-trained RandomForest model
    rf = RandomForestClassifier(featuresCol="features", labelCol="label", numTrees=5)
    model = rf.fit(test_data)

    auc = evaluate_model(model, test_data)

    # Validate AUC
    assert 0.0 <= auc <= 1.0
