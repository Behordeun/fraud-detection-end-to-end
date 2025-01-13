import os
import subprocess
import sys

# Add the 'src' directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
        # Load the pipeline configuration
        config = load_config(config_path)
        dvc_config = config["dvc_pipeline"]

        print("Initializing DVC pipeline...")

        # Step 1: Add raw data to DVC
        print(f"Adding raw data at {dvc_config['raw_data_path']} to DVC...")
        subprocess.run(["dvc", "add", dvc_config["raw_data_path"]], check=True)

        # Step 2: Data preprocessing
        print("Running data preprocessing...")
        subprocess.run(
            [
                "dvc",
                "run",
                "-n",
                "preprocess",
                "-d",
                "src/data_preprocessing/preprocessing.py",
                "-d",
                dvc_config["raw_data_path"],
                "-o",
                dvc_config["processed_data_path"],
                "python src/data_preprocessing/preprocessing.py",
            ],
            check=True,
        )

        # Step 3: Perform data quality checks
        print("Performing data quality checks on processed data...")
        spark = get_spark_session("DataQualityCheck")
        processed_data_path = dvc_config["processed_data_path"]
        if not os.path.exists(processed_data_path):
            raise FileNotFoundError(
                f"Processed data path {processed_data_path} does not exist."
            )

        processed_data = spark.read.parquet(processed_data_path)
        check_data_quality(processed_data)

        # Step 4: Generate drift report
        print("Generating data drift report...")
        generate_drift_report(processed_data)

        print("DVC pipeline completed successfully.")

    except Exception as e:
        handle_error(f"Error in DVC pipeline: {str(e)}")


if __name__ == "__main__":
    # Use the local pipeline_config.yml directly
    CONFIG_PATH = "pipeline_config.yml"
    run_dvc_pipeline(CONFIG_PATH)
