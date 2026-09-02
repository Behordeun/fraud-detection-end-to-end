import math

import pytest
from pyspark.sql import SparkSession

from src.fraud_detection.data.feature_engineering import (
    create_amount_features,
    create_interaction_features,
    create_pca_features,
    create_time_features,
)


@pytest.fixture(scope="module")
def spark():
    """Shared Spark session for the feature-engineering tests."""
    session = (
        SparkSession.builder.appName("TestFeatureEngineering")
        .master("local[1]")
        .getOrCreate()
    )
    yield session
    session.stop()


def _pca_row(**overrides):
    """Build a row carrying Time, Amount and V1..V28, with optional overrides."""
    row = {"Time": 0.0, "Amount": 0.0}
    for i in range(1, 29):
        row[f"V{i}"] = 0.0
    row.update(overrides)
    return row


def test_create_time_features_adds_hour_and_period(spark):
    # 9 * 3600 seconds -> hour 9 -> Morning; 20 * 3600 -> hour 20 -> Evening
    data = spark.createDataFrame(
        [(9 * 3600.0,), (20 * 3600.0,)],
        ["Time"],
    )

    result = create_time_features(data)

    assert "Hour" in result.columns
    assert "Time_Period" in result.columns

    rows = result.orderBy("Time").collect()
    assert rows[0]["Hour"] == pytest.approx(9.0)
    assert rows[0]["Time_Period"] == "Morning"
    assert rows[1]["Hour"] == pytest.approx(20.0)
    assert rows[1]["Time_Period"] == "Evening"


def test_create_amount_features_transforms_and_categorizes(spark):
    data = spark.createDataFrame(
        [(0.0,), (50.0,), (5000.0,)],
        ["Amount"],
    )

    result = create_amount_features(data)

    assert {"Amount_log", "Amount_sqrt", "Amount_Category"}.issubset(
        set(result.columns)
    )

    rows = result.orderBy("Amount").collect()
    # Zero amount: log(0 + 1) == 0, sqrt(0) == 0, category "Zero"
    assert rows[0]["Amount_log"] == pytest.approx(0.0)
    assert rows[0]["Amount_sqrt"] == pytest.approx(0.0)
    assert rows[0]["Amount_Category"] == "Zero"
    # 50 -> Medium, log(51), sqrt(50)
    assert rows[1]["Amount_log"] == pytest.approx(math.log(51.0))
    assert rows[1]["Amount_sqrt"] == pytest.approx(math.sqrt(50.0))
    assert rows[1]["Amount_Category"] == "Medium"
    # 5000 -> Very_Large
    assert rows[2]["Amount_Category"] == "Very_Large"


def test_create_pca_features_computes_magnitude_and_group_sums(spark):
    # Set V1=3, V2=4, rest 0 -> magnitude 5; group sums isolate the ranges.
    row = _pca_row(V1=3.0, V2=4.0, V15=2.0, V25=7.0)
    data = spark.createDataFrame([row])

    result = create_pca_features(data)

    assert {
        "PCA_Magnitude",
        "V1_to_V10_sum",
        "V11_to_V20_sum",
        "V21_to_V28_sum",
    }.issubset(set(result.columns))

    out = result.collect()[0]
    assert out["PCA_Magnitude"] == pytest.approx(
        math.sqrt(3.0**2 + 4.0**2 + 2.0**2 + 7.0**2)
    )
    assert out["V1_to_V10_sum"] == pytest.approx(7.0)  # V1 + V2
    assert out["V11_to_V20_sum"] == pytest.approx(2.0)  # V15
    assert out["V21_to_V28_sum"] == pytest.approx(7.0)  # V25


def test_create_interaction_features_requires_hour(spark):
    # Interaction features need the Hour column produced by create_time_features.
    row = _pca_row(Time=6 * 3600.0, Amount=10.0, V1=2.0, V2=3.0, V3=4.0)
    data = spark.createDataFrame([row])

    result = create_interaction_features(create_time_features(data))

    assert {
        "Amount_Hour_Interaction",
        "V1_Amount",
        "V2_Amount",
        "V3_Amount",
    }.issubset(set(result.columns))

    out = result.collect()[0]
    assert out["Amount_Hour_Interaction"] == pytest.approx(10.0 * 6.0)
    assert out["V1_Amount"] == pytest.approx(2.0 * 10.0)
    assert out["V2_Amount"] == pytest.approx(3.0 * 10.0)
    assert out["V3_Amount"] == pytest.approx(4.0 * 10.0)
