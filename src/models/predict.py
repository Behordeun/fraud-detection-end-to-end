from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel


def make_predictions(new_data_path: str, model_path: str, output_path: str):
    """
    Make predictions on new data using the trained model.
    """
    spark = SparkSession.builder \
        .appName("CreditCardFraudPrediction") \
        .getOrCreate()

    print("Loading new data...")
    new_data = spark.read.parquet(new_data_path)

    print("Loading the trained model...")
    model = PipelineModel.load(model_path)

    print("Making predictions on new data...")
    predictions = model.transform(new_data)

    print(f"Saving predictions to {output_path}...")
    predictions.select("engineered_features", "prediction").write.mode("overwrite").parquet(output_path)
    print("Predictions saved successfully.")


if __name__ == "__main__":
    NEW_DATA_PATH = "data/new_data"
    MODEL_PATH = "models/random_forest_model"
    OUTPUT_PATH = "data/predictions"

    make_predictions(NEW_DATA_PATH, MODEL_PATH, OUTPUT_PATH)
