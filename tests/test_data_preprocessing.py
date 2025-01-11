import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import DoubleType, StructField, StructType

from src.data_preprocessing.preprocessing import (
    handle_missing_values,
    load_data,
    save_preprocessed_data,
    scale_features,
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
    Test that scale_features scales numerical columns correctly.
    """
    # Sample data
    data = spark.createDataFrame(
        [(1, 100.0, 200.0), (2, 150.0, 300.0)], ["id", "feature1", "feature2"]
    )

    # Call the function
    scaled_data = scale_features(data, numerical_columns=["feature1", "feature2"])

    # Validate scaled features
    assert "scaled_features" in scaled_data.columns
    assert scaled_data.select("scaled_features").count() == data.count()

    # Validate content
    scaled_values = scaled_data.select("scaled_features").collect()
    assert len(scaled_values) == 2
    for row in scaled_values:
        assert len(row["scaled_features"].toArray()) == 2  # Check array size


def test_split_data(spark):
    """
    Test that split_data splits the dataset correctly.
    """
    # Sample data
    data = spark.createDataFrame(
        [(1, 200.0), (2, 300.0), (3, 400.0), (4, 500.0)], ["id", "amount"]
    )

    # Call the function
    train_data, test_data = split_data(data, test_size=0.5, seed=42)

    # Validate data split
    assert train_data.count() + test_data.count() == data.count()
    assert train_data.count() > 0
    assert test_data.count() > 0


def test_save_preprocessed_data(spark, tmpdir):
    """
    Test that save_preprocessed_data writes the preprocessed data correctly.
    """
    # Sample data
    train_data = spark.createDataFrame([(1, 200.0), (2, 300.0)], ["id", "amount"])
    test_data = spark.createDataFrame([(3, 400.0), (4, 500.0)], ["id", "amount"])

    # Temporary output path
    output_dir = tmpdir.mkdir("processed_data")

    # Call the function
    save_preprocessed_data(train_data, test_data, str(output_dir))

    # Validate saved files
    train_path = output_dir / "train"
    test_path = output_dir / "test"

    assert train_path.exists()
    assert test_path.exists()

    # Reload and validate content
    loaded_train_data = spark.read.parquet(str(train_path))
    loaded_test_data = spark.read.parquet(str(test_path))

    assert loaded_train_data.count() == train_data.count()
    assert loaded_test_data.count() == test_data.count()


def test_save_preprocessed_data_with_empty_data(spark, tmpdir):
    """
    Test that save_preprocessed_data handles empty datasets correctly.
    """
    # Define schema explicitly
    schema = StructType(
        [
            StructField("id", DoubleType(), True),
            StructField("amount", DoubleType(), True),
        ]
    )

    # Empty train and test datasets
    train_data = spark.createDataFrame([], schema)
    test_data = spark.createDataFrame([], schema)

    # Temporary output path
    output_dir = tmpdir.mkdir("processed_data_empty")

    # Call the function
    save_preprocessed_data(train_data, test_data, str(output_dir))

    # Validate saved files
    train_path = output_dir / "train"
    test_path = output_dir / "test"

    assert train_path.exists()
    assert test_path.exists()

    # Reload and validate content
    loaded_train_data = spark.read.parquet(str(train_path))
    loaded_test_data = spark.read.parquet(str(test_path))

    assert loaded_train_data.count() == 0
    assert loaded_test_data.count() == 0
