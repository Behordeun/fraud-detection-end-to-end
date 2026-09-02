import logging

import mlflow
import mlflow.spark
from mlflow.models.signature import infer_signature
from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.sql import SparkSession

from fraud_detection.data.feature_engineering import feature_vector_columns

logger = logging.getLogger(__name__)


def _build_pipeline(feature_cols, n_trees, max_depth, seed) -> Pipeline:
    """Assembler + classifier as one Pipeline so serving replays training.

    Bundling the VectorAssembler with the RandomForestClassifier means the saved
    PipelineModel carries the exact feature-assembly step, and the serving path
    cannot assemble a different vector than training did.
    """
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
    classifier = RandomForestClassifier(
        featuresCol="features",
        labelCol="Class",
        numTrees=n_trees,
        maxDepth=max_depth,
        seed=seed,
    )
    return Pipeline(stages=[assembler, classifier])


def train_model(
    train_data_path: str,
    model_output_path: str,
    n_trees: int = 100,
    max_depth: int = 10,
    seed: int = 42,
):
    """Train a fraud model, save it as a Spark PipelineModel, and log to MLflow.

    The saved artifact is a ``PipelineModel`` bundling the feature assembler and
    the classifier, so inference reproduces training's feature vector exactly.
    The model is registered and gated on AUC when a Model Registry backend is
    configured.
    """
    spark = (
        SparkSession.builder.appName("CreditCardFraudTraining")
        .config("spark.driver.memory", "4g")
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
        .getOrCreate()
    )

    logger.info("Loading training data...")
    train_data = spark.read.parquet(train_data_path)

    if train_data.rdd.isEmpty():
        raise ValueError("Cannot train on empty data.")

    train_data = train_data.withColumn("Class", train_data["Class"].cast("double"))

    # Two supported input shapes:
    #   - engineered frame with raw/engineered numeric columns -> the pipeline's
    #     assembler builds the vector (the authoritative, serving-shared step).
    #   - a frame that already carries only a `features` vector -> train the
    #     classifier on it directly with no assembler stage.
    source_cols = feature_vector_columns(train_data)
    if source_cols:
        if "features" in train_data.columns:
            train_data = train_data.drop("features")
            source_cols = feature_vector_columns(train_data)
        logger.info("Fitting the assembler + RandomForest pipeline...")
        pipeline = _build_pipeline(source_cols, n_trees, max_depth, seed)
        feature_cols = source_cols
    elif "features" in train_data.columns:
        logger.info("Fitting RandomForest on a pre-assembled features vector...")
        pipeline = Pipeline(
            stages=[
                RandomForestClassifier(
                    featuresCol="features",
                    labelCol="Class",
                    numTrees=n_trees,
                    maxDepth=max_depth,
                    seed=seed,
                )
            ]
        )
        feature_cols = ["features"]
    else:
        raise ValueError(
            "Training data has no feature columns and no 'features' vector."
        )

    pipeline_model = pipeline.fit(train_data)

    logger.info("Saving the pipeline model to %s...", model_output_path)
    pipeline_model.write().overwrite().save(model_output_path)

    # Training AUC is logged for reference only. Promotion is gated on the
    # held-out test AUC computed by the evaluate stage, never on this optimistic
    # in-sample number, so an overfit model cannot clear the floor.
    scored = pipeline_model.transform(train_data)
    train_auc = BinaryClassificationEvaluator(
        labelCol="Class", rawPredictionCol="rawPrediction"
    ).evaluate(scored)

    logger.info("Logging the model with MLflow (train AUC %.4f)...", train_auc)
    with mlflow.start_run() as run:
        mlflow.log_param("n_trees", n_trees)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_metric("train_auc", train_auc)

        feature_input = train_data.select(feature_cols).limit(5).toPandas()
        prediction_output = scored.select("prediction").limit(5).toPandas()
        signature = infer_signature(feature_input, prediction_output)

        mlflow.spark.log_model(
            pipeline_model,
            artifact_path="model",
            signature=signature,
        )
        logger.info("Model logged in MLflow.")
        run_id = run.info.run_id

    return {"train_auc": train_auc, "feature_columns": feature_cols, "run_id": run_id}


if __name__ == "__main__":
    from fraud_detection.utils.config import CURRENT_MODEL_DIR, PROCESSED_DATA_DIR

    logging.basicConfig(level=logging.INFO)
    TRAIN_DATA_PATH = str(PROCESSED_DATA_DIR / "engineered" / "train")
    MODEL_OUTPUT_PATH = str(CURRENT_MODEL_DIR)

    train_model(TRAIN_DATA_PATH, MODEL_OUTPUT_PATH)
