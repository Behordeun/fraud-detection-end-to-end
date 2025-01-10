# Project Structure

```plaintext
.
├── Architecture.png
├── Dockerfile
├── README.md
├── SECURITY.md
├── Untitled Diagram.drawio
├── airflow
│   ├── airflow.cfg
│   └── dags
│       └── airflow_dvc_mlflow_dag.py
├── config
│   └── global_config.yml
├── data
│   ├── dvc.yml
│   ├── processed
│   └── raw
│       └── creditcard_2023.csv
├── docker-compose.yml
├── generate_tree.sh
├── get-pip.py
├── k8s
│   ├── airflow
│   │   └── airflow-deployment.yaml
│   ├── grafana
│   │   └── grafana-deployment.yaml
│   ├── minio
│   │   └── minio-deployment.yaml
│   ├── openmetadata
│   │   └── openmetadata-deployment.yaml
│   └── prometheus
│       ├── prometheus-deployment.yaml
│       └── prometheus.yml
├── logs
├── openmetadata
│   ├── __init__.py
│   ├── config.yaml
│   ├── metadata_pipeline.py
│   └── schemas
│       ├── data_schema.yaml
│       └── model_schema.yaml
├── plugins
├── project_structure.md
├── pytest.ini
├── requirements-2.txt
├── requirements.txt
├── src
│   ├── __init__.py
│   ├── data_preprocessing
│   │   ├── __init__.py
│   │   ├── feature_engineering.py
│   │   └── preprocessing.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── evaluate.py
│   │   ├── predict.py
│   │   └── train.py
│   ├── monitoring
│   │   ├── __init__.py
│   │   ├── data_drift.py
│   │   └── model_drift.py
│   ├── pipelines
│   │   ├── __init__.py
│   │   ├── dvc_pipeline.py
│   │   ├── mlflow_pipeline.py
│   │   └── pipeline_config.yml
│   └── utils.py
├── supervisord.conf
└── tests
    ├── conftest.py
    ├── test_data_preprocessing.py
    ├── test_drift_detection.py
    ├── test_models.py
    └── test_pipelines.py

23 directories, 50 files
```
