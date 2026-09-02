# Quick Start Guide

## Get started in a few minutes

### 1. Set up the environment

```bash
# Install pinned dependencies
pip install -r requirements.txt

# Install the package (provides the fraud-detection CLI and the fraud_detection import)
pip install -e .

# Initialize DVC (once)
dvc init --no-scm
```

PySpark needs a JRE. Java 17 or 21 works. On macOS: `brew install openjdk@17` and point `JAVA_HOME` at it.

### 2. Configure environment variables

```bash
cp .env.example .env
```

MinIO credentials are read from the environment (no defaults are baked into the code), so set `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` in `.env` before starting any service that talks to MinIO. `.env` is gitignored.

### 3. Get the data

```bash
# Generate the committed 2000-row sample (no credentials needed)
python scripts/setup_data.py --sample

# Or download the real Kaggle dataset (needs KAGGLE_USERNAME and KAGGLE_KEY, or ~/.kaggle/kaggle.json)
python scripts/setup_data.py
```

### 4. Run the pipeline

```bash
# Reproduce the full DVC pipeline: preprocess -> feature_engineering -> train -> evaluate
dvc repro
```

Each stage can also run directly:

```bash
PYTHONPATH=src MLFLOW_TRACKING_URI=file:./mlruns python -m fraud_detection.pipelines.stages preprocess
PYTHONPATH=src MLFLOW_TRACKING_URI=file:./mlruns python -m fraud_detection.pipelines.stages feature_engineering
PYTHONPATH=src MLFLOW_TRACKING_URI=file:./mlruns python -m fraud_detection.pipelines.stages train
PYTHONPATH=src MLFLOW_TRACKING_URI=file:./mlruns python -m fraud_detection.pipelines.stages evaluate
```

### 5. Serve the model

```bash
PYTHONPATH=src MLFLOW_TRACKING_URI=file:./mlruns \
  uvicorn fraud_detection.api.app:app --host 0.0.0.0 --port 8000
```

Then:

- Health: `GET http://localhost:8000/health` returns `{"status":"healthy","model_loaded":true}`
- Docs: http://localhost:8000/docs
- Predict: `POST http://localhost:8000/predict` with a transaction body (Time, V1-V28, Amount)
- Metrics: `GET http://localhost:8000/metrics` (Prometheus exposition)

### 6. Bring up the observability stack (optional)

```bash
docker compose --env-file .env -f deployment/docker/docker-compose.yml up -d minio createbuckets prometheus grafana
```

- MinIO console: http://localhost:9001
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (the Fraud Detection API dashboard is auto-provisioned)

The compose Prometheus scrapes the API at `host.docker.internal:8000`, so run the API on the host (step 5) for its target to report up.

## What the pipeline does

1. Generates or loads the fraud dataset (the sample is 2000 transactions at a 2% fraud rate).
2. Preprocesses: handles missing values, splits into train/test/reserve, then scales the Amount column and persists the fitted scaler so serving uses the exact training scaler.
3. Engineers features: time-based, amount-based, PCA, and interaction features.
4. Trains a Spark `PipelineModel` (assembler + RandomForest classifier) with MLflow tracking.
5. Evaluates on the held-out test set (AUC, precision, recall, F1) and promotes the model in the MLflow registry only when the held-out AUC clears the floor.
6. Serves the model through the REST API, applying the same feature transforms at inference time.

## Metric gate

The pipeline fails if the held-out AUC drops below the floor in `params.yaml` (`gate.min_auc`, default 0.90):

```bash
python scripts/check_metrics_gate.py --metrics metrics.json --min 0.90
```

The gate fails closed: a missing, non-numeric, NaN, or infinite metric is treated as a failure, not a pass.

## Drift and retraining

```bash
# Report feature drift for a new-data set against the training reference
PYTHONPATH=src python -m fraud_detection.monitoring.advanced_drift_detection data/processed/new_data
```

The report includes a `retrain_recommended` flag, set when the drifted-feature percentage crosses `DRIFT_RETRAIN_PCT` (default 30). The scheduled `model-monitoring` workflow runs this check and dispatches `retrain.yml` when drift crosses the threshold.

## Expected results

- Held-out AUC above the 0.90 gate floor (the sample run reaches AUC around 0.99).
- Trained `PipelineModel` and the persisted Amount scaler under `models/`.
- Metrics in `metrics.json`; experiment runs under `mlruns/`.

## Troubleshooting

- **Java not found**: install a JRE (Java 17 or 21) for PySpark and set `JAVA_HOME`.
- **Port conflicts**: change the published ports in `deployment/docker/docker-compose.yml`.
- **Memory pressure**: reduce the sample size with `python scripts/setup_data.py --sample --sample-rows N`.

```bash
# Check compose services
docker compose -f deployment/docker/docker-compose.yml ps

# Service logs
docker compose -f deployment/docker/docker-compose.yml logs <service>
```

## Next steps

1. Replace the sample with the real Kaggle dataset (`python scripts/setup_data.py`).
2. Tune hyperparameters in `src/fraud_detection/models/train.py`.
3. Add features in `src/fraud_detection/data/feature_engineering.py`.
4. Deploy with the manifests in `deployment/kubernetes/`.
