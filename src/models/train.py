from pyspark.sql import SparkSession
from pyspark.ml.classification import RandomForestClassifier
import mlflow
import mlflow.spark


def train_model(train_data_path: str, model_output_path: str):
    """
    Train a machine learning model using PySpark.
    """
    spark = SparkSession.builder \
        .appName("CreditCardFraudTraining") \
        .getOrCreate()

    print("Loading training data...")
    train_data = spark.read.parquet(train_data_path)

    print("Defining the RandomForestClassifier...")
    rf = RandomForestClassifier(featuresCol="engineered_features", labelCol="label", numTrees=100, maxDepth=10)

    print("Training the model...")
    rf_model = rf.fit(train_data)

    print(f"Saving the model to {model_output_path}...")
    rf_model.write().overwrite().save(model_output_path)
    print("Model saved successfully.")

    # Log the model with MLflow
    with mlflow.start_run():
        mlflow.spark.log_model(rf_model, "model")
        print("Model logged in MLflow.")


if __name__ == "__main__":
    TRAIN_DATA_PATH = "data/processed/engineered/train"
    MODEL_OUTPUT_PATH = "models/random_forest_model"

    train_model(TRAIN_DATA_PATH, MODEL_OUTPUT_PATH)
