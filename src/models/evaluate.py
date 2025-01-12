import mlflow
from pyspark.ml.classification import RandomForestClassificationModel
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.sql import SparkSession
from pyspark.sql.functions import col


def evaluate_model(test_data_path: str, model_path: str):
    """
    Evaluate a trained machine learning model on test data and log metrics to MLflow.
    """
    # Create a Spark session
    spark = SparkSession.builder.appName("CreditCardFraudEvaluation").getOrCreate()

    print("Loading test data...")
    test_data = spark.read.parquet(test_data_path)

    # Ensure the 'features' column is set up correctly
    if "features" not in test_data.columns:
        print("Assembling feature columns into a single 'features' column...")
        feature_columns = [col for col in test_data.columns if col != "Class"]
        assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
        test_data = assembler.transform(test_data)

    # Convert integer columns to double to prevent MLflow warnings
    test_data = test_data.withColumn("Class", test_data["Class"].cast("double"))

    print("Loading the trained model...")
    model = RandomForestClassificationModel.load(model_path)

    print("Making predictions on test data...")
    predictions = model.transform(test_data)

    # Evaluate the model using BinaryClassificationEvaluator
    evaluator = BinaryClassificationEvaluator(
        labelCol="Class",
        rawPredictionCol="rawPrediction",
        metricName="areaUnderROC",
    )
    auc = evaluator.evaluate(predictions)
    print(f"Model AUC: {auc:.4f}")

    # Log evaluation metrics to MLflow
    with mlflow.start_run():
        # Log AUC
        mlflow.log_metric("AUC", auc)

        # Calculate and log additional metrics
        tp = predictions.filter((col("Class") == 1) & (col("prediction") == 1)).count()
        fp = predictions.filter((col("Class") == 0) & (col("prediction") == 1)).count()
        fn = predictions.filter((col("Class") == 1) & (col("prediction") == 0)).count()
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        mlflow.log_metric("Precision", precision)
        mlflow.log_metric("Recall", recall)
        mlflow.log_metric("F1-Score", f1_score)

        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1-Score: {f1_score:.4f}")
        print("Evaluation metrics logged to MLflow.")

    return auc


if __name__ == "__main__":
    TEST_DATA_PATH = "data/processed/test"
    MODEL_PATH = "models/random_forest_model"

    auc = evaluate_model(TEST_DATA_PATH, MODEL_PATH)
    print(f"Evaluation complete. AUC: {auc:.4f}")
