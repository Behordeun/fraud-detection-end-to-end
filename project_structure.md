# Project Structure

The tree below lists the tracked source layout. Generated data, model artifacts, and MLflow runs (`data/processed/`, `data/predictions/`, `models/`, `mlruns/`) are produced at runtime and are gitignored, so they are not shown.

```plaintext
.
├── .dvc/                          # DVC config
├── .env.example                   # Environment template (copy to .env)
├── .flake8, .isort.cfg            # Lint config read by CI from the repo root
├── .github/workflows/             # CI: lint, test, coverage, pipeline, monitoring, retrain
│   ├── codecov.yml
│   ├── lint.yml
│   ├── ml-pipeline.yml            # Reproduce pipeline, metric gate, build+push serving image
│   ├── model-monitoring.yml       # Scheduled drift check, dispatches retrain on drift
│   ├── retrain.yml                # Drift-triggered retrain on real data + registry promotion
│   ├── static.yml
│   └── test.yml
├── ADVANCED_FEATURES.md
├── CLEAN_STRUCTURE.md
├── Dockerfile.api                 # Minimal FastAPI serving image (non-root)
├── EXECUTION_GUIDE.md
├── Makefile
├── QUICKSTART.md
├── README.md
├── SECURITY.md
├── airflow/                       # Airflow DAG (optional orchestration)
│   ├── airflow.cfg
│   └── dags/airflow_dvc_mlflow_dag.py
├── config/global_config.yml
├── deployment/
│   ├── docker/                    # Compose stacks + serving/infra Dockerfiles
│   │   ├── Dockerfile
│   │   ├── Dockerfile.prod
│   │   ├── docker-compose.yml
│   │   ├── docker-compose.prod.yml
│   │   ├── docker-compose-kafka.yml
│   │   ├── grafana/               # Compose Grafana provisioning + dashboard
│   │   └── prometheus/            # Compose-local Prometheus scrape config
│   ├── kubernetes/
│   │   ├── namespace.yaml
│   │   ├── api-deployment.yaml
│   │   ├── grafana/               # grafana-deployment.yaml + fraud-api-dashboard.json
│   │   ├── minio/                 # minio-deployment.yaml + minio-credentials.example.yaml
│   │   ├── prometheus/            # prometheus.yml (in-cluster) + alert-rules.yml
│   │   ├── airflow/
│   │   └── openmetadata/
│   └── scripts/                   # deploy.py + pipeline runners
├── docs/
│   └── data-and-pipeline.md
├── dvc.yaml                       # preprocess -> feature_engineering -> train -> evaluate
├── openmetadata/                  # Metadata pipeline config + schemas
├── params.yaml                    # Data, split, model, path, and CI gate params
├── project_structure.md
├── pytest.ini
├── requirements.txt               # Pinned dependencies (single file)
├── scripts/
│   ├── check_metrics_gate.py      # CI metric gate: fail-closed on below-floor/NaN/non-numeric
│   ├── run_pipeline.py
│   ├── run_advanced_pipeline.py
│   └── setup_data.py              # Acquire real dataset or generate the sample
├── setup.py                       # Installable package + fraud-detection CLI entry point
├── src/
│   ├── __init__.py
│   └── fraud_detection/           # Package installed as `fraud_detection`
│       ├── __init__.py
│       ├── cli.py                 # `fraud-detection` command line interface
│       ├── api/
│       │   ├── app.py             # FastAPI service (/health, /predict, /metrics)
│       │   └── metrics.py         # Prometheus collectors
│       ├── data/
│       │   ├── preprocessing.py   # Split-then-scale, persists the Amount scaler
│       │   └── feature_engineering.py
│       ├── models/
│       │   ├── train.py           # Fits + persists a Spark PipelineModel
│       │   ├── evaluate.py        # Held-out AUC, gates registry promotion
│       │   ├── predict.py
│       │   ├── loader.py          # Format-detecting model loader
│       │   ├── serving.py         # build_serving_features (train/serve parity)
│       │   ├── registry.py        # Metric-gated MLflow Model Registry promotion
│       │   ├── model_comparison.py
│       │   └── hyperparameter_tuning.py
│       ├── monitoring/
│       │   ├── data_drift.py
│       │   ├── model_drift.py
│       │   ├── advanced_drift_detection.py  # PSI/JS drift + retrain_recommended flag
│       │   ├── dashboard.py
│       │   ├── simulate_data_drift.py
│       │   └── train_new_model.py
│       ├── pipelines/
│       │   ├── stages.py          # DVC stage entry point (python -m ... stages <stage>)
│       │   ├── dvc_pipeline.py
│       │   ├── mlflow_pipeline.py
│       │   └── pipeline_config.yml
│       ├── streaming/
│       │   ├── kafka_producer.py
│       │   └── kafka_consumer.py
│       └── utils/
│           ├── config.py          # Central config: paths, scaler, registry, gate, secrets
│           └── utils.py
└── tests/
    ├── conftest.py
    ├── test_data_preprocessing.py
    ├── test_feature_engineering.py
    ├── test_models.py
    ├── test_predictions.py
    ├── test_serving_parity.py     # Training/serving parity
    ├── test_api.py                # /health, /predict, /metrics
    ├── test_metrics_gate.py       # Metric-gate pass/fail-closed
    ├── test_drift_detection.py
    ├── test_drift_retrain.py
    ├── test_simulate_data_drift.py
    ├── test_train_new_model.py
    ├── test_dvc_pipelines.py
    ├── test_mlflow_pipelines.py
    └── test_utils.py
```

## Notes

- Source lives under `src/fraud_detection/` and installs as the `fraud_detection` package. Internal imports use bare `fraud_detection.*`; tests import `src.fraud_detection.*`.
- The DVC pipeline runs the four stages through one entry point: `python -m fraud_detection.pipelines.stages <stage>`.
- Deployment configs are split into `deployment/docker/` (compose stacks) and `deployment/kubernetes/` (manifests), replacing the earlier top-level `k8s/` directory.
- Dependencies are pinned in a single `requirements.txt`.
