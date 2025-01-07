from pyspark.sql import SparkSession
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml import PipelineModel


def evaluate_model(test_data_path: str, model_path: str):
    """
    Evaluate a trained machine learning model on test data.
    """
    spark = SparkSession.builder \
        .appName("CreditCardFraudEvaluation") \
        .getOrCreate()

    print("Loading test data...")
    test_data = spark.read.parquet(test_data_path)

    print("Loading the trained model...")
    model = PipelineModel.load(model_path)

    print("Making predictions on test data...")
    predictions = model.transform(test_data)

    evaluator = BinaryClassificationEvaluator(labelCol="label", rawPredictionCol="rawPrediction", metricName="areaUnderROC")
    auc = evaluator.evaluate(predictions)
    print(f"Model AUC: {auc:.4f}")

    return auc


if __name__ == "__main__":
    TEST_DATA_PATH = "data/processed/engineered/test"
    MODEL_PATH = "models/random_forest_model"

    auc = evaluate_model(TEST_DATA_PATH, MODEL_PATH)
    print(f"Evaluation complete. AUC: {auc:.4f}")
