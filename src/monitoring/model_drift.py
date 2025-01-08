import pandas as pd
from pyspark.ml import PipelineModel
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.sql import SparkSession


def evaluate_model(model, data, label_col="label"):
    """
    Evaluate the model on the provided data.
    """
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

    print("Loading baseline and current models...")
    baseline_model = PipelineModel.load(baseline_model_path)
    current_model = PipelineModel.load(current_model_path)

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
    BASELINE_MODEL_PATH = "models/baseline_model"
    CURRENT_MODEL_PATH = "models/current_model"
    TEST_DATA_PATH = "data/processed/engineered/test"
    OUTPUT_PATH = "monitoring_reports/model_drift_report.csv"

    monitor_model_drift(
        BASELINE_MODEL_PATH, CURRENT_MODEL_PATH, TEST_DATA_PATH, OUTPUT_PATH
    )
