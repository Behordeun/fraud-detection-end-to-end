import mlflow
from pyspark.ml.classification import RandomForestClassifier, GBTClassifier, LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator
from pyspark.sql import SparkSession
import pandas as pd

class ModelComparison:
    def __init__(self):
        self.spark = SparkSession.builder.appName("ModelComparison").getOrCreate()
        self.models = {
            "RandomForest": RandomForestClassifier(featuresCol="features", labelCol="Class", numTrees=100),
            "GradientBoosting": GBTClassifier(featuresCol="features", labelCol="Class", maxIter=20),
            "LogisticRegression": LogisticRegression(featuresCol="features", labelCol="Class", maxIter=100)
        }
        self.results = []
    
    def evaluate_model(self, name, model, train_data, test_data):
        """Evaluate a single model."""
        with mlflow.start_run(run_name=f"model_comparison_{name}"):
            # Train model
            fitted_model = model.fit(train_data)
            predictions = fitted_model.transform(test_data)
            
            # Calculate metrics
            binary_eval = BinaryClassificationEvaluator(labelCol="Class", rawPredictionCol="rawPrediction")
            multi_eval = MulticlassClassificationEvaluator(labelCol="Class", predictionCol="prediction")
            
            auc = binary_eval.evaluate(predictions)
            precision = multi_eval.evaluate(predictions, {multi_eval.metricName: "weightedPrecision"})
            recall = multi_eval.evaluate(predictions, {multi_eval.metricName: "weightedRecall"})
            f1 = multi_eval.evaluate(predictions, {multi_eval.metricName: "f1"})
            
            # Log metrics
            metrics = {"auc": auc, "precision": precision, "recall": recall, "f1": f1}
            mlflow.log_metrics(metrics)
            mlflow.log_param("model_type", name)
            
            # Save model
            mlflow.spark.log_model(fitted_model, "model")
            
            self.results.append({"model": name, **metrics})
            return metrics
    
    def run_comparison(self):
        """Run comparison across all models."""
        train_data = self.spark.read.parquet("data/processed/engineered/train")
        test_data = self.spark.read.parquet("data/processed/engineered/test")
        
        with mlflow.start_run(run_name="model_comparison_suite"):
            for name, model in self.models.items():
                print(f"Training {name}...")
                self.evaluate_model(name, model, train_data, test_data)
            
            # Find best model
            best_model = max(self.results, key=lambda x: x["auc"])
            mlflow.log_param("best_model", best_model["model"])
            mlflow.log_metric("best_auc", best_model["auc"])
            
            # Save comparison results
            results_df = pd.DataFrame(self.results)
            results_df.to_csv("model_comparison_results.csv", index=False)
            mlflow.log_artifact("model_comparison_results.csv")
            
            print("\nModel Comparison Results:")
            print(results_df.round(4))
            print(f"\nBest Model: {best_model['model']} (AUC: {best_model['auc']:.4f})")
            
            return best_model

if __name__ == "__main__":
    comparison = ModelComparison()
    comparison.run_comparison()