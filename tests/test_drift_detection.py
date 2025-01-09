import pytest
from pyspark.sql import SparkSession
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.linalg import Vectors
from pyspark.sql import Row
from src.monitoring.data_drift import calculate_statistics, compare_distributions
from src.monitoring.model_drift import evaluate_model


@pytest.fixture(scope="module")
def spark():
    return SparkSession.builder.appName("TestSpark").getOrCreate()


def test_calculate_statistics(spark):
    # Sample data
    data = spark.createDataFrame([(1.0,), (2.0,), (3.0,)], ["amount"])

    stats = calculate_statistics(data, ["amount"])

    # Validate statistics
    assert "amount" in stats
    assert stats["amount"]["mean"] == 2.0
    assert stats["amount"]["stddev"] > 0.0


def test_compare_distributions():
    baseline_stats = {"amount": {"mean": 2.0, "stddev": 1.0}}
    current_stats = {"amount": {"mean": 3.5, "stddev": 1.0}}

    drift_report = compare_distributions(baseline_stats, current_stats)

    # Validate drift detection
    assert drift_report["amount"]["drift_detected"] is True


def test_model_drift_evaluation(spark):
    # Mock model
    data = spark.createDataFrame(
        [
            (0.0, Vectors.dense([1.0, 2.0])),
            (1.0, Vectors.dense([2.0, 3.0])),
        ],
        ["label", "features"],
    )
    lr = LogisticRegression(featuresCol="features", labelCol="label", maxIter=5)
    model = lr.fit(data)

    # Mock test data
    test_data = spark.createDataFrame(
        [
            Row(label=0.0, features=Vectors.dense([1.0, 2.0])),
            Row(label=1.0, features=Vectors.dense([2.0, 3.0])),
        ]
    )

    # Evaluate model
    result = evaluate_model(model, test_data)
    assert result >= 0  # Example assertion for model drift evaluation
