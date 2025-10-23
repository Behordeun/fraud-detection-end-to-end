import mlflow
from pyspark.ml.classification import RandomForestClassificationModel
from pyspark.sql import SparkSession
from pyspark.sql.functions import col


def make_predictions(model_path: str, new_data_path: str, output_path: str):
    """Make predictions on new data using the trained model."""
    spark = SparkSession.builder.appName("FraudPrediction").getOrCreate()
    
    print("Loading new data...")
    new_data = spark.read.parquet(new_data_path)
    
    print("Loading trained model...")
    model = RandomForestClassificationModel.load(model_path)
    
    print("Making predictions...")
    predictions = model.transform(new_data)
    
    # Select relevant columns for output
    result = predictions.select(
        "*",
        col("prediction").alias("fraud_prediction"),
        col("probability").alias("fraud_probability")
    )
    
    print(f"Saving predictions to {output_path}...")
    result.write.mode("overwrite").parquet(output_path)
    
    # Log prediction summary
    total_predictions = result.count()
    fraud_predictions = result.filter(col("prediction") == 1).count()
    fraud_rate = fraud_predictions / total_predictions if total_predictions > 0 else 0
    
    print(f"Prediction Summary:")
    print(f"Total transactions: {total_predictions}")
    print(f"Predicted fraudulent: {fraud_predictions}")
    print(f"Fraud rate: {fraud_rate:.4f}")
    
    # Log to MLflow
    with mlflow.start_run():
        mlflow.log_metric("total_predictions", total_predictions)
        mlflow.log_metric("fraud_predictions", fraud_predictions)
        mlflow.log_metric("fraud_rate", fraud_rate)
    
    return result


if __name__ == "__main__":
    MODEL_PATH = "models/random_forest_model"
    NEW_DATA_PATH = "data/processed/new_data"
    OUTPUT_PATH = "data/predictions"
    
    make_predictions(MODEL_PATH, NEW_DATA_PATH, OUTPUT_PATH)