import mlflow
import mlflow.spark
from pyspark.ml.classification import RandomForestClassifier
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from mlflow.models.signature import infer_signature


def train_model(train_data_path: str, model_output_path: str):
    """
    Train a machine learning model using PySpark and log it with MLflow.
    """
    # Create a Spark session
    spark = SparkSession.builder \
        .appName("CreditCardFraudTraining") \
        .config("spark.driver.memory", "4g") \
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .getOrCreate()

    print("Loading training data...")
    train_data = spark.read.parquet(train_data_path)

    # Ensure the 'features' column is set up correctly
    if "features" not in train_data.columns:
        print("Assembling feature columns into a single 'features' column...")
        feature_columns = [col for col in train_data.columns if col != "Class"]
        assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
        train_data = assembler.transform(train_data).select("features", "Class")

    # Convert integer columns to double to prevent MLflow warnings
    train_data = train_data.withColumn("Class", train_data["Class"].cast("double"))

    print("Defining the RandomForestClassifier...")
    rf = RandomForestClassifier(
        featuresCol="features", labelCol="Class", numTrees=100, maxDepth=10
    )

    print("Training the model...")
    rf_model = rf.fit(train_data)

    print(f"Saving the model to {model_output_path}...")
    rf_model.write().overwrite().save(model_output_path)
    print("Model saved successfully.")

    # Log the model with MLflow
    print("Logging the model with MLflow...")
    with mlflow.start_run():
        # Create an input example for MLflow
        input_example = train_data.limit(1).toPandas()
        input_example["features"] = input_example["features"].apply(lambda x: list(x))

        # Infer the model's input and output signature
        signature = infer_signature(train_data.toPandas(), input_example)

        # Log the model to MLflow
        mlflow.spark.log_model(
            rf_model,
            artifact_path="model",
            signature=signature,
        )
        print("Model logged in MLflow.")


if __name__ == "__main__":
    TRAIN_DATA_PATH = "data/processed/train"
    MODEL_OUTPUT_PATH = "models/random_forest_model"

    train_model(TRAIN_DATA_PATH, MODEL_OUTPUT_PATH)
