import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, mean, stddev


def calculate_statistics(df, columns):
    """
    Calculate mean and standard deviation for specified columns.
    """
    stats = {}
    for col_name in columns:
        stats[col_name] = df.select(
            mean(col(col_name)).alias("mean"), stddev(col(col_name)).alias("stddev")
        ).collect()[0]
    return stats


def compare_distributions(baseline_stats, current_stats):
    """
    Compare baseline and current statistics to detect drift.
    """
    drift_report = {}
    for column in baseline_stats.keys():
        baseline_mean = baseline_stats[column]["mean"]
        baseline_stddev = baseline_stats[column]["stddev"]
        current_mean = current_stats[column]["mean"]
        drift = abs(current_mean - baseline_mean) > 2 * baseline_stddev
        drift_report[column] = {
            "baseline_mean": baseline_mean,
            "current_mean": current_mean,
            "drift_detected": drift,
        }
    return drift_report


def monitor_data_drift(baseline_data_path, current_data_path, output_path):
    """
    Monitor data drift by comparing current data to baseline data.
    """
    spark = SparkSession.builder.appName("DataDriftMonitoring").getOrCreate()

    print("Loading baseline and current datasets...")
    baseline_data = spark.read.parquet(baseline_data_path)
    current_data = spark.read.parquet(current_data_path)

    # Identify numerical columns
    numerical_columns = [
        field for field, dtype in baseline_data.dtypes if dtype in ["int", "double"]
    ]

    print("Calculating statistics for baseline and current datasets...")
    baseline_stats = calculate_statistics(baseline_data, numerical_columns)
    current_stats = calculate_statistics(current_data, numerical_columns)

    print("Comparing distributions...")
    drift_report = compare_distributions(baseline_stats, current_stats)

    print(f"Drift Report: {drift_report}")
    pd.DataFrame(drift_report).to_csv(output_path)
    print(f"Drift report saved to {output_path}")


if __name__ == "__main__":
    BASELINE_DATA_PATH = "data/processed/engineered/baseline"
    CURRENT_DATA_PATH = "data/processed/engineered/current"
    OUTPUT_PATH = "monitoring_reports/data_drift_report.csv"

    monitor_data_drift(BASELINE_DATA_PATH, CURRENT_DATA_PATH, OUTPUT_PATH)
