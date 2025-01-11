import sys
from pathlib import Path

import pytest

# Dynamically add `src` to sys.path for test imports
project_root = Path(__file__).resolve().parent.parent  # Points to the project root
sys.path.insert(0, str(project_root / "src"))  # Add `src` to Python's search path

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
