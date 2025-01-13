import os

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import DoubleType, StructField, StructType

from src.data_preprocessing.feature_engineering import save_engineered_data
from src.data_preprocessing.preprocessing import (
    handle_missing_values,
    load_data,
    save_preprocessed_data,
    scale_features,
    set_features_and_target,
    split_data,
)


@pytest.fixture(scope="module")
def spark():
    """
    Fixture for creating a shared Spark session for tests.
    """
    return (
        SparkSession.builder.appName("TestPreprocessing")
        .master("local[1]")
        .getOrCreate()
    )


def test_handle_missing_values(spark):
    """
    Test that handle_missing_values replaces missing values with appropriate values.
    """
    # Sample data
    data = spark.createDataFrame(
        [(1, 200.0, None), (2, None, "B"), (3, 300.0, None)],
        ["id", "amount", "category"],
    )

    # Call the function
    processed_data = handle_missing_values(data, target_column="id")

    # Validate missing value handling
    assert processed_data.filter("amount IS NULL").count() == 0
    assert processed_data.filter("category IS NULL").count() == 0

    # Validate replacements
    replaced_data = processed_data.filter("id == 2").first()
    assert replaced_data["amount"] == 200.0, "Expected median value for amount"
    assert replaced_data["category"] == "B", "Expected mode value for category"


def test_load_data(spark, tmpdir):
    """
    Test that load_data correctly loads data from a CSV file.
    """
    # Create sample data
    csv_content = "id,category\n1,A\n2,B\n3,C"
    input_path = tmpdir.join("input_data.csv")
    input_path.write(csv_content)

    # Load data using the load_data function
    loaded_data = load_data(str(input_path))

    # Validate the schema and content
    assert set(loaded_data.columns) == {"id", "category"}  # Check column names
    assert loaded_data.count() == 3  # Check row count

    # Validate data content
    data_content = loaded_data.collect()
    expected_content = [(1, "A"), (2, "B"), (3, "C")]
    assert [(row.id, row.category) for row in data_content] == expected_content


def test_scale_features(spark):
    """
    Test that scale_features scales the numerical column correctly.
    """
    # Create sample data
    data = spark.createDataFrame(
        [(1, 100.0), (2, 200.0)],
        ["id", "Amount"],
    )

    # Call the function
    scaled_data = scale_features(data)

    # Validate the `Amount` column is scaled
    assert "Amount" in scaled_data.columns, "Missing 'Amount' column in scaled data"
    assert scaled_data.filter(scaled_data["Amount"].isNull()).count() == 0


def test_set_features_and_target(spark):
    """
    Test that set_features_and_target correctly sets the features column.
    """
    # Create sample data
    data = spark.createDataFrame(
        [
            (1, 200.0, 1),
            (2, 300.0, 0),
        ],
        ["id", "Amount", "Class"],
    )

    # Call the function
    processed_data = set_features_and_target(data, target_column="Class")

    # Validate the `features` column is created
    assert "features" in processed_data.columns, "Missing 'features' column"

    # Validate the `features` column contains the correct data (excluding target column)
    feature_vectors = processed_data.select("features").collect()
    assert feature_vectors[0]["features"].toArray().tolist() == [
        200.0
    ], f"Incorrect feature vector for first row: {feature_vectors[0]['features'].toArray().tolist()}"
    assert feature_vectors[1]["features"].toArray().tolist() == [
        300.0
    ], f"Incorrect feature vector for second row: {feature_vectors[1]['features'].toArray().tolist()}"

    # Ensure the target column is preserved
    assert "Class" in processed_data.columns, "Target column 'Class' is missing"


def test_split_data(spark):
    """
    Test that split_data splits the dataset correctly.
    """
    # Sample data
    data = spark.createDataFrame(
        [(1, 200.0), (2, 300.0), (3, 400.0), (4, 500.0)], ["id", "Amount"]
    )

    # Call the function
    train_data, test_data, reserve_data = split_data(
        data, test_size=0.3, reserve_size=0.3, seed=42
    )

    # Validate data split
    total_count = train_data.count() + test_data.count() + reserve_data.count()
    assert total_count == data.count(), "Data split total does not match input data"
    assert train_data.count() > 0, "Training set is empty"
    assert test_data.count() > 0, "Test set is empty"
    assert reserve_data.count() > 0, "Reserve set is empty"


def test_save_preprocessed_data(spark, tmpdir):
    """
    Test that save_preprocessed_data writes the preprocessed data correctly.
    """
    # Sample data
    train_data = spark.createDataFrame([(1, 200.0)], ["id", "Amount"])
    test_data = spark.createDataFrame([(2, 300.0)], ["id", "Amount"])
    reserve_data = spark.createDataFrame([(3, 400.0)], ["id", "Amount"])

    # Temporary output path
    output_dir = tmpdir.mkdir("processed_data")

    # Call the function
    save_preprocessed_data(train_data, test_data, reserve_data, str(output_dir))

    # Validate saved files
    train_path = output_dir / "train"
    test_path = output_dir / "test"
    reserve_path = output_dir / "new_data"

    assert os.path.exists(f"{output_dir}/train")
    assert os.path.exists(f"{output_dir}/test")
    assert os.path.exists(f"{output_dir}/new_data")

    # Reload and validate content
    loaded_train_data = spark.read.parquet(str(train_path))
    loaded_test_data = spark.read.parquet(str(test_path))
    loaded_reserve_data = spark.read.parquet(str(reserve_path))

    assert loaded_train_data.count() == train_data.count()
    assert loaded_test_data.count() == test_data.count()
    assert loaded_reserve_data.count() == reserve_data.count()


def test_save_preprocessed_data_with_empty_data(spark, tmpdir):
    """
    Test that save_preprocessed_data handles empty datasets correctly.
    """
    # Define schema explicitly
    schema = StructType(
        [
            StructField("id", DoubleType(), True),
            StructField("Amount", DoubleType(), True),
        ]
    )

    # Empty train and test datasets
    train_data = spark.createDataFrame([], schema)
    test_data = spark.createDataFrame([], schema)
    reserve_data = spark.createDataFrame([], schema)

    # Temporary output path
    output_dir = tmpdir.mkdir("processed_data_empty")

    # Call the function
    save_preprocessed_data(train_data, test_data, reserve_data, str(output_dir))

    # Validate saved files
    train_path = output_dir / "train"
    test_path = output_dir / "test"
    reserve_path = output_dir / "new_data"

    assert train_path.exists()
    assert test_path.exists()
    assert reserve_path.exists()

    # Reload and validate content
    loaded_train_data = spark.read.parquet(str(train_path))
    loaded_test_data = spark.read.parquet(str(test_path))
    loaded_reserve_data = spark.read.parquet(str(reserve_path))

    assert loaded_train_data.count() == 0
    assert loaded_test_data.count() == 0
    assert loaded_reserve_data.count() == 0


def test_save_engineered_data(spark, tmpdir):
    """
    Test that save_engineered_data saves the data to Parquet correctly.
    """
    # Create sample data
    data = spark.createDataFrame(
        [(1, 100.0), (2, 200.0)],
        ["id", "Amount"],
    )

    # Define output path
    output_path = tmpdir.mkdir("engineered_data")

    # Call the function
    save_engineered_data(data, str(output_path))

    # Validate the data is saved
    saved_data = spark.read.parquet(str(output_path))
    assert saved_data.count() == data.count(), "Row count mismatch"
    assert set(saved_data.columns) == set(data.columns), "Column mismatch"
