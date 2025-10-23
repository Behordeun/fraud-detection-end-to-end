import mlflow
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator
from pyspark.ml.classification import RandomForestClassificationModel
from pyspark.sql import SparkSession
from pyspark.sql.functions import col


def evaluate_model(model_path: str, test_data_path: str):
    """Evaluate the trained model and log metrics to MLflow."""
    spark = SparkSession.builder.appName("ModelEvaluation").getOrCreate()
    
    print("Loading test data...")
    test_data = spark.read.parquet(test_data_path)
    
    print("Loading trained model...")
    model = RandomForestClassificationModel.load(model_path)
    
    print("Making predictions...")
    predictions = model.transform(test_data)
    
    # Binary classification metrics
    binary_evaluator = BinaryClassificationEvaluator(
        labelCol="Class", rawPredictionCol="rawPrediction"
    )
    
    # Multiclass classification metrics
    multiclass_evaluator = MulticlassClassificationEvaluator(
        labelCol="Class", predictionCol="prediction"
    )
    
    # Calculate metrics
    auc = binary_evaluator.evaluate(predictions, {binary_evaluator.metricName: "areaUnderROC"})
    precision = multiclass_evaluator.evaluate(predictions, {multiclass_evaluator.metricName: "weightedPrecision"})
    recall = multiclass_evaluator.evaluate(predictions, {multiclass_evaluator.metricName: "weightedRecall"})
    f1 = multiclass_evaluator.evaluate(predictions, {multiclass_evaluator.metricName: "f1"})
    accuracy = multiclass_evaluator.evaluate(predictions, {multiclass_evaluator.metricName: "accuracy"})
    
    # Calculate confusion matrix components
    tp = predictions.filter((col("Class") == 1) & (col("prediction") == 1)).count()
    tn = predictions.filter((col("Class") == 0) & (col("prediction") == 0)).count()
    fp = predictions.filter((col("Class") == 0) & (col("prediction") == 1)).count()
    fn = predictions.filter((col("Class") == 1) & (col("prediction") == 0)).count()
    
    # Log metrics to MLflow
    with mlflow.start_run():
        mlflow.log_metric("auc", auc)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1_score", f1)
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("true_positives", tp)
        mlflow.log_metric("true_negatives", tn)
        mlflow.log_metric("false_positives", fp)
        mlflow.log_metric("false_negatives", fn)
    
    print(f"Model Evaluation Results:")
    print(f"AUC: {auc:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Confusion Matrix - TP: {tp}, TN: {tn}, FP: {fp}, FN: {fn}")
    
    return {
        "auc": auc,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "accuracy": accuracy
    }


if __name__ == "__main__":
    MODEL_PATH = "models/random_forest_model"
    TEST_DATA_PATH = "data/processed/engineered/test"
    
    evaluate_model(MODEL_PATH, TEST_DATA_PATH)