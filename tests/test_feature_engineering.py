import pytest
from pyspark.sql import SparkSession

from src.data_preprocessing.feature_engineering import (
    add_derived_features,
    load_data,
    save_engineered_data,
    select_features,
)


@pytest.fixture(scope="module")
def spark():
    """
    Fixture for creating a shared Spark session for tests.
    """
    return (
        SparkSession.builder.appName("TestFeatureEngineering")
        .master("local[1]")
        .getOrCreate()
    )


def test_load_data(spark, tmpdir):
    """
    Test that load_data correctly loads Parquet files into a DataFrame.
    """
    # Create sample data and save as Parquet
    data = spark.createDataFrame(
        [(1, 100.0, "A"), (2, 200.0, "B")], ["id", "amount", "category"]
    )
    input_path = tmpdir.join("input_data.parquet")
    data.write.parquet(str(input_path))

    # Load data using load_data
    loaded_data = load_data(str(input_path))

    # Validate the loaded data
    assert loaded_data.count() == data.count()
    assert set(loaded_data.columns) == set(data.columns)


def test_add_derived_features(spark):
    """
    Test that add_derived_features correctly adds derived features to the DataFrame.
    """
    # Create sample data
    data = spark.createDataFrame(
        [(1, 100.0, 200.0), (2, 300.0, 400.0)], ["id", "feature1", "feature2"]
    )

    # Add derived features
    processed_data = add_derived_features(data)

    # Validate derived features
    assert "log_feature1" in processed_data.columns
    assert "log_feature2" in processed_data.columns
    assert "interaction" in processed_data.columns
    assert "feature1_squared" in processed_data.columns
    assert "feature2_squared" in processed_data.columns
    assert "feature1_sqrt" in processed_data.columns
    assert "feature2_sqrt" in processed_data.columns

    # Validate interaction term
    interaction = processed_data.select("interaction").collect()
    assert interaction[0]["interaction"] == 100.0 * 200.0
    assert interaction[1]["interaction"] == 300.0 * 400.0


def test_select_features(spark):
    """
    Test that select_features creates the engineered feature vector.
    """
    # Create sample data
    data = spark.createDataFrame(
        [
            (1, 100.0, 200.0),
            (2, 300.0, 400.0),
        ],
        ["id", "feature1", "feature2"],
    )

    # Select features
    selected_columns = ["feature1", "feature2"]
    processed_data = select_features(data, selected_columns)

    # Validate the feature vector
    assert "engineered_features" in processed_data.columns
    feature_vectors = processed_data.select("engineered_features").collect()
    assert feature_vectors[0]["engineered_features"].toArray().tolist() == [
        100.0,
        200.0,
    ]
    assert feature_vectors[1]["engineered_features"].toArray().tolist() == [
        300.0,
        400.0,
    ]


def test_save_engineered_data(spark, tmpdir):
    """
    Test that save_engineered_data correctly saves data as Parquet.
    """
    # Create sample data
    data = spark.createDataFrame(
        [(1, 100.0, 200.0), (2, 300.0, 400.0)], ["id", "feature1", "feature2"]
    )

    # Save data using save_engineered_data
    output_path = tmpdir.join("engineered_data.parquet")
    save_engineered_data(data, str(output_path))

    # Validate the saved file
    loaded_data = spark.read.parquet(str(output_path))
    assert loaded_data.count() == data.count()
    assert set(loaded_data.columns) == set(data.columns)
