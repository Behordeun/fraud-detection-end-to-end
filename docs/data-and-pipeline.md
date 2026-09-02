# Data and the reproducible pipeline

The training pipeline is defined as a DVC pipeline in `dvc.yaml` with parameters
in `params.yaml`. It has four stages that run in order:

1. `preprocess` — load the raw CSV, handle missing values, scale `Amount`, and
   split into train/test/reserve parquet sets.
2. `feature_engineering` — add time, amount, PCA, and interaction features and
   assemble the model feature vector.
3. `train` — fit the RandomForest classifier and save it to `models/current_model`.
4. `evaluate` — score the held-out test set and write `metrics.json`.

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
