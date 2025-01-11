import subprocess

from src.utils import (
    check_data_quality,
    generate_drift_report,
    get_spark_session,
    handle_error,
    load_config,
)


def run_dvc_pipeline(config_path: str):
    """
    Executes the DVC pipeline with parameterized configuration.
    """
    try:
        config = load_config(config_path)
        dvc_config = config["dvc_pipeline"]

        print("Initializing DVC pipeline...")

        # Step 1: Add raw data to DVC
        subprocess.run(["dvc", "add", dvc_config["raw_data_path"]], check=True)

        # Step 2: Data preprocessing
        subprocess.run(
            [
                "dvc",
                "run",
                "-n",
                "preprocess",
                "-d",
                "src/data_processing/preprocess.py",
                "-d",
                dvc_config["raw_data_path"],
                "-o",
                dvc_config["processed_data_path"],
                "python src/data_processing/preprocess.py",
            ],
            check=True,
        )

        # Step 3: Perform data quality checks on preprocessed data
        print("Performing data quality checks...")
        spark = get_spark_session()
        df = spark.read.parquet(f"{dvc_config['processed_data_path']}/train")
        check_data_quality(df)

        # Step 4: Feature engineering
        subprocess.run(
            [
                "dvc",
                "run",
                "-n",
                "feature_engineering",
                "-d",
                "src/data_processing/feature_engineering.py",
                "-d",
                f"{dvc_config['processed_data_path']}/train",
                "-o",
                dvc_config["engineered_data_path"],
                "python src/data_processing/feature_engineering.py",
            ],
            check=True,
        )

        # Step 5: Generate a drift report (if applicable)
        print("Generating drift report...")
        drift_data = {
            "feature1": {
                "baseline_mean": 0.5,
                "current_mean": 0.7,
                "drift_detected": True,
            }
        }
        generate_drift_report(drift_data, dvc_config["drift_report_path"])

        print("DVC pipeline successfully executed.")
    except Exception as e:
        handle_error(f"Error in DVC pipeline: {str(e)}")


if __name__ == "__main__":
    CONFIG_PATH = "pipeline_config.yaml"
    run_dvc_pipeline(CONFIG_PATH)
