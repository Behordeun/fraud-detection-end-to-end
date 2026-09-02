# README.md

## Credit Card Fraud Detection with MLOps

This project demonstrates an end-to-end Machine Learning pipeline for Credit Card Fraud Detection, leveraging MLOps tools and best practices. It incorporates DVC, MLflow, Airflow, OpenMetadata, Prometheus, Grafana, and MinIO to manage the entire lifecycle of data, models, and infrastructure.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#Features)
3. [Architecture](#Architecture)
4. [Setup Instructions](#Setup_Instructions)
5. [Usage](#Usage)
6. [Project Structure](#Project_Structure)
7. [Monitoring and Alerts](#Monitoring_and_Alerts)
8. [Troubleshooting](#Troubleshooting)
9. [Contributing](#Contributing)

---

## Project Overview

Credit card fraud detection is a critical task in the financial domain. This project demonstrates a production-ready pipeline that:

- Processes raw transactional data.
- Performs feature engineering and model training.
- Tracks experiments and metadata.
- Monitors data and model drift.

The system is built with scalability and reproducibility in mind, using tools such as DVC for data versioning, MLflow for experiment tracking, and Airflow for pipeline orchestration.

---

## Features

- Data Versioning: Manage raw and processed datasets using DVC.
- Pipeline Orchestration: Automate workflows with Airflow and DVC - pipelines.
- Experiment Tracking: Log model training runs, metrics, and artifacts - with MLflow.
- Metadata Management: Track dataset and model lineage using - OpenMetadata.
- Monitoring: Visualize metrics in Grafana and monitor health with - Prometheus.
- Cloud Storage: Store datasets in MinIO, an S3-compatible storage - solution.
- Deployment-Ready: Supports deployment via Docker and Kubernetes.

---

### Architecture

The architecture consists of the following components:

![Architectural Diagram](Architecture.png)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FBehordeun%2Ffraud-detection-end-to-end.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2FBehordeun%2Ffraud-detection-end-to-end?ref=badge_shield)

## Setup Instructions

### 1. Prerequisites

- Docker and Docker Compose installed.
- Kubernetes (optional) for cluster deployment.

### 2. Clone the Repository

```bash
git clone https://github.com/Behordeun/fraud-detection-end-to-end.git
cd fraud-detection-end-to-end
```

### 3. Build and Run Docker Compose

Build and start all services using Docker Compose:

```bash
docker compose --env-file .env -f deployment/docker/docker-compose.yml up -d
```

### 4. Access Services

| Service       | URL                   | Notes                          |
| ------------- | --------------------- | ------------------------------ |
| MinIO Console | http://localhost:9001 | Manage raw and processed data. |
| Prometheus    | http://localhost:9090 | Monitor metrics and alerts.    |
| Grafana       | http://localhost:3000 | Visualize dashboards.          |
| Airflow       | http://localhost:8080 | Orchestrate workflows.         |
| OpenMetadata  | http://localhost:8585 | Manage metadata.               |

---

## Usage

### 1. Data Versioning with DVC

Add, version, and push raw data:

```bash
dvc init
dvc add data/raw/creditcard_2023.csv
dvc remote add -d minio s3://dvc-bucket
dvc push
```

### 2. Run Pipelines

- DVC Pipeline:

```bash
dvc repro
```

- Airflow DAG:
  Enable and trigger the fraud_detection_dag from the Airflow UI.

### 3. Monitor Metrics

- Open Grafana and import dashboards for MinIO, MLflow, and custom model metrics.
- Use Prometheus to query raw metrics.

---

## Project Structure

```text
.
├── Dockerfile.api              # Minimal FastAPI serving image (non-root)
├── README.md
├── SECURITY.md
├── requirements.txt            # Pinned dependencies (single file)
├── setup.py                    # Installable package + fraud-detection CLI
├── params.yaml                 # Data, split, model, path, and CI gate params
├── dvc.yaml                    # preprocess -> feature_engineering -> train -> evaluate
├── .github/workflows/          # lint, test, coverage, ml-pipeline, model-monitoring, retrain
├── airflow/                    # Optional Airflow DAG
├── config/                     # global_config.yml
├── deployment/
│   ├── docker/                 # Compose stacks + serving/infra Dockerfiles
│   └── kubernetes/             # Manifests (api, grafana, minio, prometheus, ...)
├── docs/                       # data-and-pipeline.md
├── openmetadata/               # Metadata pipeline config + schemas
├── scripts/                    # setup_data.py, check_metrics_gate.py, pipeline runners
├── src/
│   └── fraud_detection/        # Package installed as `fraud_detection`
│       ├── api/                # app.py (/health, /predict, /metrics) + metrics.py
│       ├── data/               # preprocessing.py, feature_engineering.py
│       ├── models/             # train, evaluate, predict, loader, serving, registry
│       ├── monitoring/         # data_drift, model_drift, advanced_drift_detection
│       ├── pipelines/          # stages.py (DVC entry point) + dvc/mlflow pipelines
│       ├── streaming/          # kafka_producer.py, kafka_consumer.py
│       └── utils/              # config.py, utils.py
└── tests/
```

See [project_structure.md](project_structure.md) for the full annotated tree.

## Monitoring and Alerts

### 1. Prometheus

- Scrape metrics from MinIO, OpenMetadata, and application components.
- Alert Rules:
- MinIO Down: Triggered if MinIO is unreachable for over 1 minute.

### 2. Grafana Dashboards

- Import pre-built dashboards:
- MinIO: Grafana Dashboard for MinIO
- MLflow and custom metrics.

## Troubleshooting

### 1.  Service Not Starting:

- Check logs:

```bash
docker logs <container_name>
```

### 2. Data Not Found in MinIO:

- Verify dvc remote settings and MinIO credentials.

### 3.  Prometheus Target Down:

- Ensure the service is accessible from Prometheus.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch:

```bash
git checkout -b feature/new-feature
```

3. Commit your changes and create a pull request.


## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FBehordeun%2Ffraud-detection-end-to-end.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2FBehordeun%2Ffraud-detection-end-to-end?ref=badge_large)