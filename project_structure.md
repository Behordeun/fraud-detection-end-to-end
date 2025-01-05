.

0 directories, 0 files
.
├── Dockerfile
├── README.md
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
├── notebooks
│   ├── baseline_model.ipynb
│   ├── credit-card-fraud-detection-achieving-99-acc.ipynb
│   ├── eda.ipynb
│   └── feature_engineering.ipynb
├── openmetadata
│   ├── config.yaml
│   ├── metadata_pipeline.py
│   └── schemas
│       ├── data_schema.yaml
│       └── model_schema.yaml
├── plugins
├── project_structure.md
├── requirements.txt
├── src
│   ├── data_preprocessing
│   │   ├── feature_engineering.py
│   │   └── preprocessing.py
│   ├── models
│   │   ├── evaluate.py
│   │   ├── predict.py
│   │   └── train.py
│   ├── monitoring
│   │   ├── data_drift.py
│   │   └── model_drift.py
│   ├── pipelines
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

24 directories, 43 files
