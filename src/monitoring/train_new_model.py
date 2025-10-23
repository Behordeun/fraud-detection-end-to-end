import mlflow
import mlflow.spark
from mlflow.models.signature import infer_signature
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.feature import VectorAssembler
from pyspark.sql import SparkSession


def train_current_model(train_data_path: str, model_output_path: str):
    """
    Train a machine learning model for the current scenario using PySpark and log it with MLflow.
    """
    # Create a Spark session
    spark = (
        SparkSession.builder.appName("CurrentModelTraining")
        .config("spark.driver.memory", "8g")  # Increase driver memory
        .config("spark.executor.memory", "4g")  # Increase executor memory
        .config("spark.sql.shuffle.partitions", "50")  # Optimize partitions
        .config(
            "spark.serializer", "org.apache.spark.serializer.KryoSerializer"
        )  # Use Kryo serializer
        .getOrCreate()
    )

    print("Loading training data...")
    train_data = spark.read.parquet(train_data_path).limit(10000)

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

    print(f"Saving the current model to {model_output_path}...")
    rf_model.write().overwrite().save(model_output_path)
    print("Current model saved successfully.")

    # Log the current model with MLflow
    print("Logging the current model with MLflow...")
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
        print("Current model logged in MLflow.")


if __name__ == "__main__":
    TRAIN_DATA_PATH = "data/processed/train"
    CURRENT_MODEL_OUTPUT_PATH = "models/current_model"

    train_current_model(TRAIN_DATA_PATH, CURRENT_MODEL_OUTPUT_PATH)
