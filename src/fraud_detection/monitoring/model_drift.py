import pandas as pd
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.sql import SparkSession

from fraud_detection.data.feature_engineering import apply_feature_transforms
from fraud_detection.models.loader import load_model, pipeline_assembles_features


def _prepare_drift_input(model, test_data):
    """Shape the drift input to match how the model was trained.

    A PipelineModel that assembles its own vector needs the engineered source
    columns, not a stale raw ``features`` vector, so it does not score on a
    different feature set than training (the same skew fixed in serving). Apply
    the shared feature-engineering transforms and drop any stale vector so the
    pipeline's assembler builds the features.
    """
    if pipeline_assembles_features(model):
        if "features" in test_data.columns:
            test_data = test_data.drop("features")
        test_data = apply_feature_transforms(test_data)
        string_cols = [n for n, d in test_data.dtypes if d == "string"]
        if string_cols:
            test_data = test_data.drop(*string_cols)
    return test_data


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

    print("Loading baseline model...")
    baseline_model = load_model(baseline_model_path)

    print("Loading current model...")
    current_model = load_model(current_model_path)

    # Shape the input to match each model: a PipelineModel assembles its own
    # vector from engineered columns, so a stale raw features vector would make
    # it score a different feature set than it was trained on.
    baseline_data = _prepare_drift_input(baseline_model, test_data)
    current_data = _prepare_drift_input(current_model, test_data)

    print("Evaluating baseline model...")
    baseline_auc = evaluate_model(baseline_model, baseline_data)

    print("Evaluating current model...")
    current_auc = evaluate_model(current_model, current_data)

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
