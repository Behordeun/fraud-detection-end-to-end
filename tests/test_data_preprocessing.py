import os
import sys

import pytest
from pyspark.sql import SparkSession

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from src.data_processing.feature_engineering import add_derived_features
from src.data_processing.preprocess import preprocess_data


@pytest.fixture(scope="module")
def spark():
    return SparkSession.builder.appName("TestSpark").getOrCreate()


def test_preprocess_data(spark):
    # Sample raw data
    raw_data = spark.createDataFrame(
        [(1, 200.0, None), (2, None, 1.0), (3, 300.0, 0.0)], ["id", "amount", "label"]
    )

    processed_data = preprocess_data(raw_data)

    # Validate that missing values are handled
    assert processed_data.filter("amount is NULL").count() == 0
    assert processed_data.filter("label is NULL").count() == 0


def test_add_derived_features(spark):
    # Sample processed data
    processed_data = spark.createDataFrame([(1, 200.0), (2, 300.0)], ["id", "amount"])

    derived_data = add_derived_features(processed_data)

    # Validate derived features
    assert "log_amount" in derived_data.columns
    assert "amount_squared" in derived_data.columns
