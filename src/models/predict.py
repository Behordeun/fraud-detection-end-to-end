import os
import logging
from pyspark.ml import PipelineModel
from pyspark.sql import SparkSession, functions as F
from pyspark.ml.linalg import VectorUDT


def configure_logger():
    """
    Configure logging for the predictions process.
    """
    logging_level = os.getenv("LOGGING_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=logging_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger("CreditCardFraudPrediction")
    return logger


def make_predictions(
    new_data_path: str,
    model_path: str,
    output_path: str,
    partition_by=None,  # Partitioning disabled temporarily
    required_columns: list = ["engineered_features"],
    output_columns: list = ["engineered_features", "prediction"],
):
    """
    Make predictions on new data using the trained model.

    Args:
        new_data_path (str): Path to the new data in Parquet format.
        model_path (str): Path to the trained model.
        output_path (str): Path to save the predictions in Parquet format.
        partition_by (str): Column to partition the predictions file. Default is None.
        required_columns (list): List of required input columns for validation.
        output_columns (list): List of required output columns for validation.
    """
    logger = configure_logger()
    logger.info("Starting predictions process...")

    # Retrieve or create Spark session
    spark = (
        SparkSession.getActiveSession()
        or SparkSession.builder.appName("CreditCardFraudPrediction").getOrCreate()
    )

    try:
        logger.info("Loading new data...")
        new_data = spark.read.parquet(new_data_path)

        # Validate input row count
        row_count = new_data.count()
        logger.info(f"New data schema: {new_data.schema}")
        logger.info(f"New data row count: {row_count}")
        if row_count == 0:
            raise ValueError("Input data is empty. Cannot proceed with predictions.")

        # Validate schema
        logger.info("Validating input data schema...")
        missing_input_columns = [
            col for col in required_columns if col not in new_data.columns
        ]
        if missing_input_columns:
            raise ValueError(
                f"Missing required columns in input data: {missing_input_columns}"
            )

        # Validate column types
        for field in new_data.schema.fields:
            if field.name == "engineered_features" and not isinstance(
                field.dataType, VectorUDT
            ):
                raise ValueError(
                    f"Column 'engineered_features' must be of type VectorUDT, got {field.dataType}"
                )
        logger.info("Input data schema validation passed.")

        logger.info("Loading the trained model...")
        model = PipelineModel.load(model_path)

        logger.info("Making predictions on new data...")
        predictions = model.transform(new_data)

        # **Enforce prediction column inclusion and handle missing column**
        if "prediction" not in predictions.columns:
            # Create a column of zeros (or appropriate default) if missing
            logger.warning(
                "Prediction column not found in model output. Creating a placeholder column."
            )
            predictions = predictions.withColumn("prediction", F.lit(0.0))

        # Debugging: Validate predictions schema and content (optional)
        logger.info(f"Predictions schema before saving: {predictions.schema}")
        # logger.info(f"Sample rows in predictions: {predictions.limit(5).collect()}")  # Optional for debugging

        # Validate and log schema before saving
        missing_output_columns = [
            col for col in output_columns if col not in predictions.columns
        ]
        if missing_output_columns:
            logger.error(
                f"Missing required columns in predictions: {missing_output_columns}"
            )
            raise ValueError(
                f"Missing required columns in predictions: {missing_output_columns}"
            )

        logger.info(f"Predictions row count: {predictions.count()}")

        logger.info("Saving predictions to output path...")
        if partition_by and partition_by in predictions.columns:
            logger.info(f"Partitioning predictions by column: {partition_by}")
            predictions.write.mode("overwrite").partitionBy(partition_by).parquet(
                output_path
            )
        else:
            logger.warning(
                f"Partition column '{partition_by}' not found or disabled. Saving without partitioning."
            )
            predictions.write.mode("overwrite").parquet(output_path)

        logger.info(f"Predictions saved successfully to {output_path}")

    except Exception as e:
        logger.error(f"Error during predictions: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # Default paths with fallbacks
    NEW_DATA_PATH = os.getenv("NEW_DATA_PATH", "data/processed/new_data")
    MODEL_PATH = os.getenv("MODEL_PATH", "models/random_forest_model")
    OUTPUT_PATH = os.getenv("OUTPUT_PATH", "data/predictions")

    try:
        # Call the make_predictions function
        make_predictions(
            NEW_DATA_PATH, MODEL_PATH, OUTPUT_PATH, partition_by="prediction"
        )
    except Exception as e:
        logging.error(f"Failed to execute predictions: {e}")
