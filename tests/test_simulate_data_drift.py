import pytest
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, mean

from src.monitoring.simulate_data_drift import simulate_data_drift


@pytest.fixture(scope="module")
def spark():
    """
    Create a Spark session for testing.
    """
    return (
        SparkSession.builder.appName("TestSimulateDataDrift")
        .master("local[*]")
        .getOrCreate()
    )


def test_simulate_data_drift(spark, tmpdir):
    """
    Test that simulate_data_drift introduces drift as expected.
    """
    original_data = spark.createDataFrame(
        [
            (1.0, 2.0, 100.0, 0),
            (2.0, 3.0, 200.0, 1),
            (3.0, 4.0, 300.0, 0),
            (4.0, 5.0, 400.0, 1),
        ],
        ["V1", "V11", "Amount", "Class"],
    )

    original_data_path = tmpdir.join("original_data.parquet")
    original_data.write.mode("overwrite").parquet(str(original_data_path))

    drift_columns = ["V1", "Amount"]
    drift_factor = 0.2
    n_samples = 4
    drifted_data = simulate_data_drift(
        spark,
        original_data_path=str(original_data_path),
        drift_columns=drift_columns,
        drift_type="mean",
        drift_factor=drift_factor,
        n_samples=n_samples,
        random_state=42,
    )

    assert drifted_data.count() == n_samples

    # Verify drift in specified columns
    for col_name in drift_columns:
        original_mean = original_data.select(mean(col(col_name))).collect()[0][0]
        drifted_mean = drifted_data.select(mean(col(col_name))).collect()[0][0]
        assert drifted_mean > original_mean  # Drift applied

    # Verify no drift in other columns
    for col_name in set(original_data.columns) - set(drift_columns):
        original_mean = original_data.select(mean(col(col_name))).collect()[0][0]
        drifted_mean = drifted_data.select(mean(col(col_name))).collect()[0][0]
        assert abs(drifted_mean - original_mean) < 1e-2  # Minor variations allowed
