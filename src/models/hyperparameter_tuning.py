import optuna
import mlflow
from pyspark.ml.classification import RandomForestClassifier, GBTClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.sql import SparkSession
import mlflow.spark

def objective(trial):
    """Optuna objective function for hyperparameter optimization."""
    spark = SparkSession.builder.appName("HyperparameterTuning").getOrCreate()
    
    # Load training data
    train_data = spark.read.parquet("data/processed/engineered/train")
    
    # Suggest hyperparameters
    model_type = trial.suggest_categorical("model_type", ["rf", "gbt"])
    
    if model_type == "rf":
        num_trees = trial.suggest_int("num_trees", 50, 200)
        max_depth = trial.suggest_int("max_depth", 5, 20)
        model = RandomForestClassifier(
            featuresCol="features", 
            labelCol="Class",
            numTrees=num_trees,
            maxDepth=max_depth
        )
    else:
        max_iter = trial.suggest_int("max_iter", 10, 50)
        max_depth = trial.suggest_int("max_depth", 3, 10)
        model = GBTClassifier(
            featuresCol="features",
            labelCol="Class", 
            maxIter=max_iter,
            maxDepth=max_depth
        )
    
    # Train and evaluate
    fitted_model = model.fit(train_data)
    predictions = fitted_model.transform(train_data)
    
    evaluator = BinaryClassificationEvaluator(labelCol="Class", rawPredictionCol="rawPrediction")
    auc = evaluator.evaluate(predictions)
    
    # Log to MLflow
    with mlflow.start_run(nested=True):
        mlflow.log_params(trial.params)
        mlflow.log_metric("auc", auc)
        if model_type == "rf":
            mlflow.spark.log_model(fitted_model, "model")
    
    return auc

def run_hyperparameter_tuning():
    """Run hyperparameter optimization."""
    with mlflow.start_run(run_name="hyperparameter_tuning"):
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=20)
        
        # Log best parameters
        mlflow.log_params(study.best_params)
        mlflow.log_metric("best_auc", study.best_value)
        
        print(f"Best AUC: {study.best_value:.4f}")
        print(f"Best params: {study.best_params}")
        
        return study.best_params

if __name__ == "__main__":
    run_hyperparameter_tuning()