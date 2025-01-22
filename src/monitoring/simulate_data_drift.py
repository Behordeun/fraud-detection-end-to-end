from pyspark.sql import SparkSession
from pyspark.sql.functions import col, mean, lit, expr
import numpy as np
import os


def read_data(spark, file_path):
    """
    Dynamically read data based on the file format.

    Parameters:
    - spark (SparkSession): Spark session object.
    - file_path (str): Path to the dataset.

    Returns:
    - DataFrame: Spark DataFrame containing the dataset.
    """
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext == ".csv":
        return spark.read.csv(file_path, header=True, inferSchema=True)
    elif file_ext == ".parquet":
        return spark.read.parquet(file_path)
    elif file_ext == ".orc":
        return spark.read.orc(file_path)
    elif file_ext == ".json":
        return spark.read.json(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")


def simulate_data_drift(
    spark,
    original_data_path,
    drift_columns,
    drift_type="mean",
    drift_factor=0.2,
    n_samples=1000,
    random_state=None,
):
    """
    Simulate data drift by altering specific columns of a dataset.

    Parameters:
    - spark (SparkSession): Spark session object.
    - original_data_path (str): Path to the original dataset.
    - drift_columns (list): List of column names where drift should be introduced.
    - drift_type (str): Type of drift to introduce ("mean", "variance").
    - drift_factor (float): Factor by which to introduce drift.
    - n_samples (int): Number of samples to generate for the drifted dataset.
    - random_state (int): Random state for reproducibility.

    Returns:
    - drifted_data (DataFrame): Drifted dataset as a PySpark DataFrame.
    """
    if random_state is not None:
        np.random.seed(random_state)

    # Read the original dataset dynamically based on file format
    original_data = read_data(spark, original_data_path)

    # Ensure drift_columns exist in the dataset
    original_columns = original_data.columns
    for col_name in drift_columns:
        if col_name not in original_columns:
            raise ValueError(f"Column '{col_name}' not found in the dataset.")

    # Introduce drift in the specified columns
    for col_name in drift_columns:
        if drift_type == "mean":
            # Compute the mean of the column
            col_mean = original_data.select(mean(col(col_name))).collect()[0][0]
            # Add a fraction of the mean to introduce drift
            original_data = original_data.withColumn(
                col_name, col(col_name) + lit(drift_factor * col_mean)
            )
        elif drift_type == "variance":
            # Multiply the column values to increase variance
            original_data = original_data.withColumn(
                col_name, col(col_name) * lit(1 + drift_factor)
            )
        else:
            raise ValueError("Unsupported drift_type. Choose 'mean' or 'variance'.")

    # Sample `n_samples` rows to match the desired size of the drifted dataset
    drifted_data = original_data.sample(withReplacement=True, fraction=1.0).limit(
        n_samples
    )

    return drifted_data


# Example usage
if __name__ == "__main__":
    # Initialize Spark session
    spark = (
        SparkSession.builder.appName("SimulateDataDrift")
        .config("spark.master", "local[*]")
        .getOrCreate()
    )

    # Path to the original dataset
    original_data_path = (
        "data/raw/creditcard_2023.csv"  # Adjust file path and format as needed
    )

    # Simulate data drift
    drifted_data = simulate_data_drift(
        spark,
        original_data_path=original_data_path,
        drift_columns=["V1", "V11", "Amount", "Class"],
        drift_type="mean",
        drift_factor=0.3,
        n_samples=1000,
        random_state=42,
    )

    # Save the drifted dataset
    drifted_data_path = "data/drifted_data"
    drifted_data.write.mode("overwrite").parquet(drifted_data_path)

    print(f"Drifted data saved to {drifted_data_path}")
