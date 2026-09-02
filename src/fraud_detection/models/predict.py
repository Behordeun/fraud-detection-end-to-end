import logging
from typing import Optional

import mlflow
from pyspark.ml.classification import RandomForestClassificationModel
from pyspark.ml.linalg import VectorUDT
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, udf
from pyspark.sql.types import DoubleType

REQUIRED_COLUMNS = ["features"]


def _fraud_probability_column(predictions):
    """Extract the class-1 (fraud) probability as a scalar column.

    The classifier emits a ``probability`` vector [P(legit), P(fraud)]; the
    monitoring dashboard consumes the fraud side as a scalar. When a model emits
    no probability vector, default the scalar to 0.0 so the column always exists.
    """
    if "probability" not in predictions.columns:
        return predictions.withColumn("fraud_probability", lit(0.0))

    extract_fraud_prob = udf(
        lambda v: float(v[1]) if v is not None and len(v) > 1 else 0.0,
        DoubleType(),
    )
    return predictions.withColumn(
        "fraud_probability", extract_fraud_prob(col("probability"))
    )


def make_predictions(
    model_path: str,
    new_data_path: str,
    output_path: str,
    partition_by: Optional[str] = None,
):
    """Score new data with a trained model and write the predictions.

    The input data must carry a ``features`` vector column. Pass ``partition_by``
    to write the parquet output partitioned by a column (e.g. ``prediction``).
    """
    logger = logging.getLogger(__name__)
    spark = SparkSession.builder.appName("FraudPrediction").getOrCreate()

    logger.info("Starting predictions process...")

    logger.info("Loading new data...")
    new_data = spark.read.parquet(new_data_path)

    missing = [c for c in REQUIRED_COLUMNS if c not in new_data.columns]
    if missing:
        raise ValueError(f"Missing required columns in input data: {missing}")

    if not isinstance(new_data.schema["features"].dataType, VectorUDT):
        actual = dict(new_data.dtypes).get("features")
        raise ValueError(f"Column 'features' must be of type VectorUDT, got {actual}")

    if new_data.rdd.isEmpty():
        raise ValueError("Input data is empty. Cannot proceed with predictions.")

    logger.info("Loading trained model...")
    model = RandomForestClassificationModel.load(model_path)

    logger.info("Making predictions...")
    predictions = model.transform(new_data)

    # A model that emits no prediction column defaults every row to 0.0 so
    # downstream consumers always see the column.
    if "prediction" not in predictions.columns:
        predictions = predictions.withColumn("prediction", lit(0.0))

    # The monitoring dashboard consumes a scalar fraud_probability column.
    predictions = _fraud_probability_column(predictions)

    result = predictions.select(
        "*",
        col("prediction").alias("fraud_prediction"),
    )

    logger.info("Saving predictions to %s...", output_path)
    writer = result.write.mode("overwrite")
    if partition_by:
        writer = writer.partitionBy(partition_by)
    writer.parquet(output_path)

    total_predictions = result.count()
    fraud_predictions = result.filter(col("prediction") == 1).count()
    fraud_rate = fraud_predictions / total_predictions if total_predictions > 0 else 0

    logger.info("Total transactions: %s", total_predictions)
    logger.info("Predicted fraudulent: %s", fraud_predictions)
    logger.info("Fraud rate: %.4f", fraud_rate)

    with mlflow.start_run():
        mlflow.log_metric("total_predictions", total_predictions)
        mlflow.log_metric("fraud_predictions", fraud_predictions)
        mlflow.log_metric("fraud_rate", fraud_rate)

    return result


if __name__ == "__main__":
    from fraud_detection.utils.config import (
        CURRENT_MODEL_DIR,
        PREDICTIONS_DIR,
        PROCESSED_DATA_DIR,
    )

    MODEL_PATH = str(CURRENT_MODEL_DIR)
    NEW_DATA_PATH = str(PROCESSED_DATA_DIR / "new_data")
    OUTPUT_PATH = str(PREDICTIONS_DIR)

    make_predictions(MODEL_PATH, NEW_DATA_PATH, OUTPUT_PATH)
