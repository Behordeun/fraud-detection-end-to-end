import json
import os

import pandas as pd
from pyspark.ml import PipelineModel
from pyspark.ml.classification import RandomForestClassificationModel
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.sql import SparkSession


def load_model(model_path):
    """
    Load the model from the given path, detecting whether it is a PipelineModel
    or a single stage model like RandomForestClassificationModel.
    """
    metadata_path = os.path.join(model_path, "metadata")
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(
            f"Metadata not found in the model path: {metadata_path}"
        )

    # Metadata for the saved model
    metadata_file = os.path.join(metadata_path, "part-00000")
    if os.path.isfile(metadata_file):
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
            model_class = metadata.get("class")
            if model_class == "org.apache.spark.ml.PipelineModel":
                return PipelineModel.load(model_path)
            elif (
                model_class
                == "org.apache.spark.ml.classification.RandomForestClassificationModel"
            ):
                return RandomForestClassificationModel.load(model_path)
            else:
                raise ValueError(f"Unsupported model class: {model_class}")
    else:
        raise ValueError(f"Metadata file not found in path: {metadata_path}")


def evaluate_model(model, data, label_col="label"):
    """
    Evaluate the model on the provided data.
    """
    if label_col not in data.columns:
        print(
            f"Warning: '{label_col}' column not found. Aliasing 'Class' to '{label_col}'."
        )
        data = data.withColumnRenamed("Class", label_col)

    evaluator = BinaryClassificationEvaluator(
        labelCol=label_col, metricName="areaUnderROC"
    )
    auc = evaluator.evaluate(model.transform(data))
    return auc


def monitor_model_drift(
    baseline_model_path, current_model_path, test_data_path, output_path
):
    """
    Monitor model drift by comparing the performance of baseline and current models.
    """
    spark = SparkSession.builder.appName("ModelDriftMonitoring").getOrCreate()

    print("Loading test data...")
    test_data = spark.read.parquet(test_data_path)

    # Ensure features column exists if missing
    if "features" not in test_data.columns:
        print("Creating features column using VectorAssembler...")
        from pyspark.ml.feature import VectorAssembler

        assembler = VectorAssembler(
            inputCols=[f"V{i}" for i in range(1, 29)] + ["Amount"], outputCol="features"
        )
        test_data = assembler.transform(test_data)

    print("Loading baseline model...")
    baseline_model = load_model(baseline_model_path)

    print("Loading current model...")
    current_model = load_model(current_model_path)

    print("Evaluating baseline model...")
    baseline_auc = evaluate_model(baseline_model, test_data)

    print("Evaluating current model...")
    current_auc = evaluate_model(current_model, test_data)

    drift_detected = abs(current_auc - baseline_auc) > 0.05

    print(f"Baseline AUC: {baseline_auc:.4f}, Current AUC: {current_auc:.4f}")
    print(f"Drift Detected: {drift_detected}")

    report = {
        "baseline_auc": baseline_auc,
        "current_auc": current_auc,
        "drift_detected": drift_detected,
    }

    pd.DataFrame([report]).to_csv(output_path)
    print(f"Model drift report saved to {output_path}")


if __name__ == "__main__":
    BASELINE_MODEL_PATH = "models/random_forest_model/"
    CURRENT_MODEL_PATH = "models/current_model/"
    TEST_DATA_PATH = "data/processed/test/"
    OUTPUT_PATH = "monitoring_reports/model_drift_report.csv"

    try:
        monitor_model_drift(
            BASELINE_MODEL_PATH, CURRENT_MODEL_PATH, TEST_DATA_PATH, OUTPUT_PATH
        )
    except Exception as e:
        print(f"Error: {e}")
