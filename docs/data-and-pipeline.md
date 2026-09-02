# Data and the reproducible pipeline

The training pipeline is defined as a DVC pipeline in `dvc.yaml` with parameters
in `params.yaml`. It has four stages that run in order:

1. `preprocess`: load the raw CSV, handle missing values, scale `Amount`, and
   split into train/test/reserve parquet sets.
2. `feature_engineering`: add time, amount, PCA, and interaction features and
   assemble the model feature vector.
3. `train`: fit the RandomForest classifier and save it to `models/current_model`.
4. `evaluate`: score the held-out test set and write `metrics.json`.

## Getting the data

The real dataset is the Kaggle "Credit Card Fraud Detection 2023" set. It is
large and license-restricted, so it is not committed; DVC tracks it instead.

```bash
# Real dataset (needs Kaggle credentials in the environment or ~/.kaggle/kaggle.json)
python scripts/setup_data.py
```

If Kaggle credentials are absent, the script generates a deterministic synthetic
dataset with the same schema so the pipeline still runs.

A small synthetic sample (`data/raw/creditcard_sample.csv`, 2000 rows) is
committed so CI can reproduce the whole pipeline without the large download.
Regenerate it with:

```bash
python scripts/setup_data.py --sample
```

## Running the pipeline

```bash
# Reproduce every stage whose inputs changed
dvc repro

# Inspect the tracked evaluation metrics
dvc metrics show
```

Change a value in `params.yaml` (for example `model.n_trees`) and `dvc repro`
re-runs only the affected stages.

## Tracking the real dataset with DVC

The committed sample lets CI run without any external data. The full Kaggle
dataset is acquired and then tracked with DVC on your own machine:

```bash
python scripts/setup_data.py          # fetch data/raw/creditcard_2023.csv
dvc add data/raw/creditcard_2023.csv  # start tracking it (creates the .dvc pointer)
git add data/raw/creditcard_2023.csv.dvc && git commit -m "track dataset"
dvc push                              # upload it to the remote
```

Commit the generated `.dvc` pointer so a teammate's `dvc pull` fetches the same
data. The dataset itself is never committed to git.

## The DVC remote

`.dvc/config` points at a MinIO S3 remote (`s3://dvc-bucket` on
`http://localhost:9000`). The compose stack provisions that bucket
automatically via the `createbuckets` service, so `dvc push` / `dvc pull` work
once `docker compose up` has run:

```bash
dvc push   # upload tracked data/models to the remote
dvc pull   # fetch them on a fresh checkout
```

Credentials are read from the environment (`AWS_ACCESS_KEY_ID` /
`AWS_SECRET_ACCESS_KEY`); see `.env.example`.

## Serving and training/serving parity

Training fits and persists a Spark `PipelineModel` (a feature assembler plus the
classifier). Serving loads that same model through `models/loader.py` and
applies the identical feature transforms via `models/serving.py`, so a request
to `/predict` is scored exactly the way the model was trained. The Amount
scaler fitted during preprocessing is persisted and reused at inference, rather
than refitted, which keeps the scaling consistent between training and serving.

Run the API:

```bash
PYTHONPATH=src MLFLOW_TRACKING_URI=file:./mlruns \
  uvicorn fraud_detection.api.app:app --host 0.0.0.0 --port 8000
```

Endpoints: `/health`, `/predict` (Time, V1-V28, Amount), and `/metrics`.

## The metric gate and model registry

`evaluate` scores the held-out test set and promotes the model in the MLflow
registry only when the held-out AUC clears the floor. CI enforces the same floor
through `scripts/check_metrics_gate.py`, reading `gate.min_auc` from
`params.yaml` (default 0.90):

```bash
python scripts/check_metrics_gate.py --metrics metrics.json --min 0.90
```

The gate fails closed: a missing, non-numeric, NaN, or infinite metric is a
failure, never a pass. Registry promotion is a no-op on a file-based tracking
store, so a real tracking server is required for it to take effect.

## Observability and drift-triggered retraining

The API exposes Prometheus metrics at `/metrics` (request counts, prediction
latency histogram, and a model-loaded gauge). `advanced_drift_detection`
computes feature drift (PSI and Jensen-Shannon distance) and sets a
`retrain_recommended` flag when the drifted-feature percentage crosses
`DRIFT_RETRAIN_PCT` (default 30). The scheduled `model-monitoring` workflow runs
the drift check and dispatches `retrain.yml` when drift crosses the threshold;
`retrain.yml` retrains on real data and promotes through the registry against a
real tracking server, failing loud when neither a tracked dataset nor Kaggle
credentials are available.

MinIO credentials are read from the environment with no default baked into the
code, so `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` must be set (see `.env.example`)
for any environment that talks to MinIO.

## Local observability with docker compose

Bring up the core observability services:

```bash
docker compose --env-file .env -f deployment/docker/docker-compose.yml \
  up -d minio createbuckets prometheus grafana
```

Two things are specific to the compose stack and differ from the Kubernetes
manifests:

- Grafana is provisioned from `deployment/docker/grafana/` (a Prometheus
  datasource pointing at the `prometheus` compose service and the Fraud
  Detection API dashboard), so the dashboard loads automatically. The
  Kubernetes Grafana uses its own manifests under `deployment/kubernetes/`.
- The compose Prometheus reads `deployment/docker/prometheus/prometheus.yml`,
  whose `fraud-api` target is `host.docker.internal:8000`. Run the API on the
  host (the uvicorn command above) for that target to report up. The Kubernetes
  `prometheus.yml` instead targets the in-cluster service name and is left
  unchanged for in-cluster use.
