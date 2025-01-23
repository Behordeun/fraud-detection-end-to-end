import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, mean, stddev
import os
import glob
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data(spark, path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path does not exist: {path}")

    # Check if the path is a directory
    if os.path.isdir(path):
        files = glob.glob(os.path.join(path, "*"))
        if not files:
            raise ValueError(f"No files found in directory: {path}")
        path = files[0]  # Use the first file
        logger.info(f"Using file: {path}")

    ext = os.path.splitext(path)[1].lower()

    if ext == ".csv":
        return spark.read.csv(path, header=True, inferSchema=True)
    elif ext == ".parquet":
        return spark.read.parquet(path)
    elif ext == ".orc":
        return spark.read.orc(path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def calculate_statistics(df, columns):
    stats_df = df.select(
        *[mean(col(c)).alias(f"{c}_mean") for c in columns],
        *[stddev(col(c)).alias(f"{c}_stddev") for c in columns],
    )
    stats = stats_df.collect()[0]
    return {
        c: {"mean": stats[f"{c}_mean"], "stddev": stats[f"{c}_stddev"]} for c in columns
    }


def compare_distributions(baseline_stats, current_stats, threshold=2):
    drift_report = {}
    for column in baseline_stats.keys():
        baseline_mean = baseline_stats[column]["mean"]
        baseline_stddev = baseline_stats[column]["stddev"]
        current_mean = current_stats[column]["mean"]
        drift = abs(current_mean - baseline_mean) > threshold * baseline_stddev
        drift_report[column] = {
            "baseline_mean": baseline_mean,
            "current_mean": current_mean,
            "drift_detected": drift,
        }
    return drift_report


def monitor_data_drift(baseline_data_path, current_data_path, output_path, threshold=2):
    spark = SparkSession.builder \
        .appName("DataDriftMonitoring") \
        .config("spark.driver.memory", "8g") \
        .config("spark.executor.memory", "4g") \
        .config("spark.executor.cores", "2") \
        .config("spark.sql.shuffle.partitions", "50") \
        .config("spark.eventLog.enabled", "true") \
        .config("spark.eventLog.dir", "/tmp/spark-events") \
        .getOrCreate()

    logger.info(f"Baseline data path: {baseline_data_path}")
    logger.info(f"Current data path: {current_data_path}")

    logger.info("Loading baseline and current datasets...")
    baseline_data = load_data(spark, baseline_data_path).limit(1000)
    current_data = load_data(spark, current_data_path).limit(1000)

    numerical_columns = [
        field for field, dtype in baseline_data.dtypes if dtype in ["int", "double"]
    ]
    if not numerical_columns:
        raise ValueError("No numerical columns found in the baseline dataset.")

    logger.info(f"Baseline dataset contains {baseline_data.count()} rows.")
    logger.info(f"Current dataset contains {current_data.count()} rows.")

    logger.info("Calculating statistics for baseline and current datasets...")
    baseline_stats = calculate_statistics(baseline_data, numerical_columns)
    current_stats = calculate_statistics(current_data, numerical_columns)

    logger.info("Comparing distributions...")
    drift_report = compare_distributions(baseline_stats, current_stats, threshold)

    logger.info(f"Drift Report: {drift_report}")
    pd.DataFrame(drift_report).T.to_csv(output_path)
    logger.info(f"Drift report saved to {output_path}")


if __name__ == "__main__":
    BASELINE_DATA_PATH = "data/processed/train"
    CURRENT_DATA_PATH = "data/drifted_data"
    OUTPUT_PATH = "monitoring_reports/data_drift_report.csv"

    monitor_data_drift(BASELINE_DATA_PATH, CURRENT_DATA_PATH, OUTPUT_PATH)
