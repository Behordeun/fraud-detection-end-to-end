import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    """
    Fixture for creating a shared Spark session for tests.
    """
    spark = (
        SparkSession.builder.appName("TestSparkSession")
        .master("local[1]")
        .getOrCreate()
    )
    yield spark
    spark.stop()
