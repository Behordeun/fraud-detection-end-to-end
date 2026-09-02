"""Configuration management for fraud detection system."""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Data paths
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
PREDICTIONS_DIR = DATA_DIR / "predictions"

# Model paths
CURRENT_MODEL_DIR = MODELS_DIR / "current_model"
MODEL_REGISTRY_DIR = MODELS_DIR / "registry"
# Fitted Amount StandardScaler persisted at preprocess time and reloaded for
# serving so inference scales with the training distribution (no leakage).
AMOUNT_SCALER_DIR = MODELS_DIR / "amount_scaler"

# MLflow Model Registry
MLFLOW_REGISTERED_MODEL = os.getenv("MLFLOW_REGISTERED_MODEL", "fraud-detection-rf")
# A newly trained model is promoted in the registry only if its AUC clears this
# floor. Keeps a regression from silently becoming the served model.
MODEL_PROMOTION_MIN_AUC = float(os.getenv("MODEL_PROMOTION_MIN_AUC", "0.90"))

# API configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# MLflow configuration
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "fraud-transactions")

# MinIO / S3 object store. Credentials come from the environment; there is no
# hardcoded default so a missing value fails loudly instead of silently using a
# well-known dev credential in a real deployment.
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

# Model configuration
DEFAULT_MODEL_PARAMS = {
    "random_forest": {"n_estimators": 100, "max_depth": 10, "random_state": 42}
}

# Drift detection thresholds
DRIFT_THRESHOLDS = {
    "psi_threshold": 0.1,
    "ks_p_value_threshold": 0.05,
    "js_distance_threshold": 0.1,
}

# Retraining is recommended when the share of drifted features exceeds this
# percentage. The drift job flags it; a human or the scheduled workflow acts.
DRIFT_RETRAIN_PCT = float(os.getenv("DRIFT_RETRAIN_PCT", "30.0"))
