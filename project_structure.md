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
│   ├── predictions
│   │   ├── _SUCCESS
│   │   ├── _temporary
│   │   │   └── 0
│   │   │       └── _temporary
│   │   ├── prediction=0.0
│   │   │   ├── part-00000-b1ecbf3f-296d-4943-aaf2-c0f47e956adc.c000.snappy.parquet
│   │   │   ├── part-00001-b1ecbf3f-296d-4943-aaf2-c0f47e956adc.c000.snappy.parquet
│   │   │   ├── part-00002-b1ecbf3f-296d-4943-aaf2-c0f47e956adc.c000.snappy.parquet
│   │   │   ├── part-00003-b1ecbf3f-296d-4943-aaf2-c0f47e956adc.c000.snappy.parquet
│   │   │   ├── part-00004-b1ecbf3f-296d-4943-aaf2-c0f47e956adc.c000.snappy.parquet
│   │   │   ├── part-00005-b1ecbf3f-296d-4943-aaf2-c0f47e956adc.c000.snappy.parquet
│   │   │   ├── part-00006-b1ecbf3f-296d-4943-aaf2-c0f47e956adc.c000.snappy.parquet
│   │   │   └── part-00007-b1ecbf3f-296d-4943-aaf2-c0f47e956adc.c000.snappy.parquet
│   │   └── prediction=1.0
│   │       ├── part-00000-b1ecbf3f-296d-4943-aaf2-c0f47e956adc.c000.snappy.parquet
│   │       ├── part-00001-b1ecbf3f-296d-4943-aaf2-c0f47e956adc.c000.snappy.parquet
│   │       ├── part-00002-b1ecbf3f-296d-4943-aaf2-c0f47e956adc.c000.snappy.parquet
│   │       ├── part-00003-b1ecbf3f-296d-4943-aaf2-c0f47e956adc.c000.snappy.parquet
│   │       ├── part-00004-b1ecbf3f-296d-4943-aaf2-c0f47e956adc.c000.snappy.parquet
│   │       ├── part-00005-b1ecbf3f-296d-4943-aaf2-c0f47e956adc.c000.snappy.parquet
│   │       ├── part-00006-b1ecbf3f-296d-4943-aaf2-c0f47e956adc.c000.snappy.parquet
│   │       └── part-00007-b1ecbf3f-296d-4943-aaf2-c0f47e956adc.c000.snappy.parquet
│   ├── processed
│   │   ├── engineered
│   │   ├── new_data
│   │   │   ├── _SUCCESS
│   │   │   ├── _temporary
│   │   │   │   └── 0
│   │   │   │       ├── _temporary
│   │   │   │       └── task_202501121957298570952781955853845_0074_m_000000
│   │   │   ├── part-00000-37e1d605-4e53-431a-9755-3749adca8870-c000.snappy.parquet
│   │   │   ├── part-00001-37e1d605-4e53-431a-9755-3749adca8870-c000.snappy.parquet
│   │   │   ├── part-00002-37e1d605-4e53-431a-9755-3749adca8870-c000.snappy.parquet
│   │   │   ├── part-00003-37e1d605-4e53-431a-9755-3749adca8870-c000.snappy.parquet
│   │   │   ├── part-00004-37e1d605-4e53-431a-9755-3749adca8870-c000.snappy.parquet
│   │   │   ├── part-00005-37e1d605-4e53-431a-9755-3749adca8870-c000.snappy.parquet
│   │   │   ├── part-00006-37e1d605-4e53-431a-9755-3749adca8870-c000.snappy.parquet
│   │   │   └── part-00007-37e1d605-4e53-431a-9755-3749adca8870-c000.snappy.parquet
│   │   ├── test
│   │   │   ├── _SUCCESS
│   │   │   ├── part-00000-671153f5-20e1-40a3-b4d8-2031208b95ec-c000.snappy.parquet
│   │   │   ├── part-00001-671153f5-20e1-40a3-b4d8-2031208b95ec-c000.snappy.parquet
│   │   │   ├── part-00002-671153f5-20e1-40a3-b4d8-2031208b95ec-c000.snappy.parquet
│   │   │   ├── part-00003-671153f5-20e1-40a3-b4d8-2031208b95ec-c000.snappy.parquet
│   │   │   ├── part-00004-671153f5-20e1-40a3-b4d8-2031208b95ec-c000.snappy.parquet
│   │   │   ├── part-00005-671153f5-20e1-40a3-b4d8-2031208b95ec-c000.snappy.parquet
│   │   │   ├── part-00006-671153f5-20e1-40a3-b4d8-2031208b95ec-c000.snappy.parquet
│   │   │   └── part-00007-671153f5-20e1-40a3-b4d8-2031208b95ec-c000.snappy.parquet
│   │   └── train
│   │       ├── _SUCCESS
│   │       ├── part-00000-f8ed716c-f8fa-4770-ba70-3f6fde1a5ac8-c000.snappy.parquet
│   │       ├── part-00001-f8ed716c-f8fa-4770-ba70-3f6fde1a5ac8-c000.snappy.parquet
│   │       ├── part-00002-f8ed716c-f8fa-4770-ba70-3f6fde1a5ac8-c000.snappy.parquet
│   │       ├── part-00003-f8ed716c-f8fa-4770-ba70-3f6fde1a5ac8-c000.snappy.parquet
│   │       ├── part-00004-f8ed716c-f8fa-4770-ba70-3f6fde1a5ac8-c000.snappy.parquet
│   │       ├── part-00005-f8ed716c-f8fa-4770-ba70-3f6fde1a5ac8-c000.snappy.parquet
│   │       ├── part-00006-f8ed716c-f8fa-4770-ba70-3f6fde1a5ac8-c000.snappy.parquet
│   │       └── part-00007-f8ed716c-f8fa-4770-ba70-3f6fde1a5ac8-c000.snappy.parquet
│   └── raw
│       ├── creditcard_2023.csv
│       └── creditcard_2023.csv.dvc
├── docker-compose.yml
├── generate_tree.sh
├── get-pip.py
├── hs_err_pid46183.log
├── hs_err_pid48468.log
├── hs_err_pid63211.log
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
├── mlruns
│   ├── 0
│   │   ├── 03ae43e6b69e43eb9d6476fc3bebfafc
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_6c6429d0b428
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-3a8f3de0-79dc-4ebc-bbfe-154372b90694-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-bcb3b13e-f720-4f1a-b5a4-d3e15a06f715-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 0c67683510ad4c4c9e02e0d903aab63c
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_73972aa5cb71
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-066004c9-a9e6-43ce-9ff9-1decdf58bd1b-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-418a85b0-c064-4311-b023-063decad7397-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 0ce2aa5b5c9d4d9a9141bb294198c63a
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_e6d3827af30f
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-268ae6a9-6244-4fa3-92f2-a2a0806fd9b9-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-9738b696-d7c5-4569-90f6-a405d02e3291-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 0def05686d0447fa9666a48c8e195646
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_74f887ebfbfb
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-5d85f621-4b72-4da6-8a68-89f20b4f466c-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-201cd258-f8a5-406e-8de7-6467e5d21931-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 1a90e4fff91144c4871f9321b341d18b
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_14f2d6e6b810
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-a1306069-6f0e-4d0a-8ab3-83629416ebf6-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-2066bf85-5c34-47fe-89f1-322030f72fed-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 24f329b003214ae4aaecf97c7ee3318e
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_4391c9b0db42
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-8f4698d9-1128-431a-93c2-894ad014b82f-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-ab5b94a3-1adb-40c1-9718-e26455a5cebe-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.git.commit
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 2b1fd40774bb4f2f82331ab6f23dfdd6
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_c5103d22830d
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-6aea35fe-4e8c-4940-b7d2-ebc6fdfcd134-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-3b15a056-0979-476e-984c-6b1f98d49892-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 2f07c105f76f4357a5c1a7caf45c8b5e
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_6f14493c27af
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-51b663ea-9a7b-4c47-a635-67e3a9259c32-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-46a8933d-38a8-4359-a720-e6935a240951-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 35612ee984c34feaa2a985a2873bd0b2
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_b92f06331fb0
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-db7f637e-58fd-4a60-b109-40387b48fbac-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-ee4a20d3-3bbb-4346-8f46-bf5852cd7de2-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 3ba50269f813490c8fcd97c261b7eb6a
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_6eba11d8a38b
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-7a6a8378-d8e6-4d41-8773-f4c8dd1671cc-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-9e51c759-4a34-48ab-84a3-ec3a67aa44b9-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 4280e55fb92b43869e820d37944c21d6
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_f1bae95255bf
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-097e17fd-ade1-42e8-96cd-bb14636f6877-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-293950a1-2e6c-4b90-a405-06a5bfa83848-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 4374b9734db241cda9b921f63e7c71e8
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_b0a14577266e
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-61c0950c-f4fe-4d23-af53-6884a4d0f804-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-73f93078-c08d-42b0-a415-d1f1120a03d6-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 4557e59629824a29b83216cbe64a22e3
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_4e0744743b29
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-bd5f93a3-669a-40f2-931d-4844f2cb7a66-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-e803b797-42f0-4f56-b048-405200a7db33-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 45718882d87b49f4b7709a5281ea68eb
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_47118ecf3b0a
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-22b85270-cdf1-4cd2-96b6-365314f6b2f3-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-cc8830c1-0b5b-4f5e-a31d-1b0fedadd421-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 49c1689d195c4b5dbc6198d0aa2a0a0e
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_d73dff53a410
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-8f3644cc-b36f-40f6-90a2-942263cfa8e0-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-c80bc948-e3a3-4858-a099-8ffd76ba3920-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 4aa1ddbfed8a4420bb69a0c38293f749
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_31c886f50d6e
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-6904289a-0bae-43aa-8e24-43a7608aac5c-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-8a19abab-8bbd-4d1d-acca-5d9b9078f5fe-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 4d175aa2a4994334b5aa2fa63abeecea
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_832a2327b4f5
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-993d8177-f1c7-41ca-8df6-dd90553e1030-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-2280d94f-5ab9-442e-9f51-e7fc2714c60c-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.git.commit
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 55ee80b2fceb4f9eb096d70b669de5e2
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_6293e8cb7282
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-a9d65d76-25ab-4139-846e-c643a953e6b3-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-e530e4a9-bc69-4aa1-a1a5-f86011b24872-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 57c62f8fd0944cb28bdb21d45e5ac4d0
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_596df904978a
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-45645c3c-751e-4876-9c37-ea7501edb89f-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-79d5287c-5dcd-48f9-9be8-682cf1c58d95-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 5cdba36eb6a54c03be80fea7a80a0847
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_74fa18af174b
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-e1e3c3ae-4ed4-4b85-99e5-f10f65de8fd3-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-844c08a0-2b15-4585-8855-71239beb4a89-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 5e82e455fcb94cb0a3a6e44de0e6cbdd
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_70ecea5f6e1d
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-3b4b9a09-c8e1-41b5-a157-8e67ac8cf206-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-8c485fbd-d03b-45a0-890e-9382f76a43d3-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 62ddf69818424115a6bf122bf5f6b3f2
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_637ff504e9d1
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-79efc338-0040-4ad0-96a8-c8b4f9d5a73f-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-994c6c24-56ce-46df-8546-6c997ebcdc86-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 6396405238eb4edaa9c152bfdabf04c9
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_e74b86431902
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-60173063-1f66-428e-a0ed-52795c4d2ce0-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-550e99bf-d48c-4963-87cb-f8af4d3d58e9-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 6b1ec5135d7544af9cb6731f9a9b9bb0
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── input_example.json
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       ├── serving_input_example.json
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_167ba8c432d6
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-bf854e0f-95ab-44b2-8035-1e8025171b97-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-eabf089b-cb72-46bd-bc4b-a68c4c6e17fe-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.git.commit
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 6e6d7ab2ba2b463fb96fb5b6638bb686
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── input_example.json
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       ├── serving_input_example.json
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_62069166c856
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-3baf2440-38e8-4f76-b61c-c4491c436925-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-22aec847-6fab-4ce9-8dcf-68f63e5a8042-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.git.commit
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 6f45787ea6c449e6b9507129e78f97a3
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_2eb733d9107b
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-28366be0-7200-464f-bcc0-ff185912e5c4-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-2d7fff8e-8b81-4e4c-a2a5-4537f6f2382a-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 71e04f4b55894546a023fadb4a114611
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_909e4af4e7f1
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-bd36f28a-2c80-40fd-873a-7134391ffff7-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-c32758d4-f070-42e1-83d5-79d8ef18d514-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 75648fca03d443b4884d581462890d42
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_b8d43bd255f0
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-aa23e2f5-8ca9-4b8f-88b5-30b40ed18746-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-eccfcd1f-14ab-49d0-8f44-40f646c4059e-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 779cdf36073a4b06b02e30556242abd7
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_94f8e6f75f85
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-d0f1b8a2-1457-4b26-a6d0-0b91bcab5a83-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-9b039c5e-d8e8-4f78-affc-523054711795-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 814848b41d1d4270a51cfec9f0d19b61
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_fe5d0291bc9c
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-cc04a371-ffdd-4c05-a90b-e9677641a1ea-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-7d279174-ea20-469d-b125-2f0d983eb300-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.git.commit
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 824cf2096a4a4b2d8de32c5bb172307c
│   │   │   ├── artifacts
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.git.commit
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 8c43aae7aae64f66bbf728a7d25b60fa
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_94fd7b18206f
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-96bd9fb1-08a6-46b0-8fff-581e7f439e16-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-1d250e9c-6127-4645-8111-3a5101425723-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 934b5f2c2cd5479dbeddde2f9eecdb23
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_545baeca0567
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-00fdee7a-f1df-425f-8e99-13ccbb3385c0-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-999b4d38-7776-4f3c-9eb5-28ba8b11b511-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── 9a599cd0e97d42929baf8feec8ff1b82
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_f96e5e03b7c3
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-6b1cbd67-aab5-4ced-ac2d-a1601c911b3e-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-03f0c73a-ea31-46f9-b648-d369db059588-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── a48c3713cab5441d9bf9f39f2e808baf
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_322865dfeab8
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-125f9de0-7907-497d-b978-6079784b12eb-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-f4594cea-74e5-415f-a962-12726c76b8e6-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── a9d8284a3c3e43499f87b391d1019174
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_dcfca345bdf4
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-ca9dad8a-a677-450d-84b0-5de9905c92f2-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-0c78fa1b-db7a-41a2-9144-22c1655bf2c0-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── a9f37acbc5f84ac085adbfe11d5754c1
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_c3e597aa5e58
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-f4e181dc-df94-4cb8-a6c8-427f12d0bb7c-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-482ab825-9364-4db5-9779-7eb9f9785dd7-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── aaa02a2ccd664d24918237ab5c369088
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_5b0f0ab2d4d7
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-00afc7a5-c95d-4d35-8ec9-ef82519faf0d-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-95cbb61b-0ecd-420a-a00c-37a5082c8fcd-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── ad452e7546c44cc88130b1b516f8afaa
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_503656bb3ebb
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-7a0c03fa-53d8-478d-9f91-31985f3dcfad-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-b9e5302d-7b61-450a-914a-f0a1cd23eca2-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── b0b9e67b9dff4438af109f4bbc673119
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── input_example.json
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       ├── serving_input_example.json
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_dfee2f450a16
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-7c1cb5f8-ae07-47db-88c2-84e0f6d7fb74-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-a0dadc72-8f76-40a5-ab04-6f1a43747ab0-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.git.commit
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── b81169ee3a7a4e0891a852b7560eedb2
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_49834fa292d9
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-fe58e29a-5f43-4f53-9d02-2e6132a48851-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-5d4732bf-5e45-4971-b717-47aa53f6b1ee-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── b9f3ab2d116646448a367df7ddc7e5ff
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_f7b01b47ee0e
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-badd0db1-6933-4e75-ab62-f9eee8e52aa0-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-001260ea-86b5-4e0f-aac7-6f34de82da86-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── c14c6797d05647ff841eeaa57b521977
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_d0a8ccdbe96f
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-206bf4b2-ec70-47ad-8428-07cdc2707163-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-4284d727-69b4-4cd5-9dd3-52eb9db8f68c-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── d5081653806f40ecae2c4e0b777b488a
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_34c049202888
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-119b87fe-a7a0-4e0e-acde-8d154e6977e6-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-cfc4ae6f-c733-47a9-b7d6-28677f10dedd-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── d767f5f082b14987907f24e2282fe1d6
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_66b3eb3a98f9
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-1384f179-7c0a-4a31-b01e-b65e37a58d1a-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-445dae01-4c35-4f18-80a8-6559c649c374-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── d7a4d98453494dbf82f9dc4a6e4506be
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_fc0845debb6e
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-9e421817-abad-4193-90c0-451bb68e38d6-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-4476a24b-a4ba-4758-af9b-824787d9f6ca-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.git.commit
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── dd5c40510d074d7db79d68caa70b7ebf
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_2820c80d110b
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-4d45bb96-ccb7-4716-8aff-0210bdf0a5ad-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-2028db61-4fc1-420b-811e-ad8664fd81ea-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── e488fd30a57d45dcaeb80271b47119c1
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_b5c4d4bdc255
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-7be5212b-78a2-4361-bbbd-47147820a945-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-fceccc8c-bfc8-4e98-9685-7982d3c179d2-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── e6bafeb7fdf34cbdae423d91dd3d912f
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_5c8be08cccbf
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-6b9f929b-e8bd-4f67-8770-8caf8374ed99-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-9dd7b47b-9dff-4bfa-bff7-1af96dd9c266-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── e8468196014c40f5a4c05b5382bcade1
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_986916f6f351
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-3f04f972-4cdc-4bf4-87dc-d8c043370175-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-af6bf7a6-503b-4e5f-8419-ba225f3fbcd7-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── e9446d833dda4a038412a2f73df64841
│   │   │   ├── artifacts
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   │   ├── Class_0_Count
│   │   │   │   └── Class_1_Count
│   │   │   ├── params
│   │   │   │   ├── Model_Path
│   │   │   │   ├── New_Data_Path
│   │   │   │   └── Output_Path
│   │   │   └── tags
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.git.commit
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── f3d57ee8b36b4d71b2726761b4c496d2
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_c2da4156bcf4
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-0c26e74f-fb4d-4893-bc72-776de48cb8a9-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-91348661-473a-400d-b15f-7439b009f743-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── f6cb23aaf44f44babb91b0b84fa6209a
│   │   │   ├── artifacts
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   │   ├── AUC
│   │   │   │   ├── F1-Score
│   │   │   │   ├── Precision
│   │   │   │   └── Recall
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.git.commit
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   ├── fe765c22eeb1415aa57b83efe87a9189
│   │   │   ├── artifacts
│   │   │   │   └── model
│   │   │   │       ├── MLmodel
│   │   │   │       ├── conda.yaml
│   │   │   │       ├── python_env.yaml
│   │   │   │       ├── requirements.txt
│   │   │   │       └── sparkml
│   │   │   │           ├── metadata
│   │   │   │           │   ├── _SUCCESS
│   │   │   │           │   └── part-00000
│   │   │   │           └── stages
│   │   │   │               └── 0_RandomForestClassifier_5d5f7fac724c
│   │   │   │                   ├── data
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000-bfc00104-3326-4da4-bacc-1011db60c60f-c000.snappy.parquet
│   │   │   │                   ├── metadata
│   │   │   │                   │   ├── _SUCCESS
│   │   │   │                   │   └── part-00000
│   │   │   │                   └── treesMetadata
│   │   │   │                       ├── _SUCCESS
│   │   │   │                       └── part-00000-439896b0-0207-4493-8a99-42e1921e6230-c000.snappy.parquet
│   │   │   ├── meta.yaml
│   │   │   ├── metrics
│   │   │   ├── params
│   │   │   └── tags
│   │   │       ├── mlflow.log-model.history
│   │   │       ├── mlflow.runName
│   │   │       ├── mlflow.source.name
│   │   │       ├── mlflow.source.type
│   │   │       └── mlflow.user
│   │   └── meta.yaml
│   └── models
├── models
│   └── random_forest_model
│       ├── data
│       │   ├── _SUCCESS
│       │   └── part-00000-d5a621a1-492a-4f8b-bf1e-e2ec01eed6e7-c000.snappy.parquet
│       ├── metadata
│       │   ├── _SUCCESS
│       │   └── part-00000
│       └── treesMetadata
│           ├── _SUCCESS
│           └── part-00000-e28f2c4f-f9f5-4fb4-80ae-4e10d61f5e2a-c000.snappy.parquet
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
├── setup.py
├── src
│   ├── __init__.py
│   ├── data_preprocessing
│   │   ├── __init__.py
│   │   ├── feature_engineering.py
│   │   └── preprocessing.py
│   ├── fraud_detection.egg-info
│   │   ├── PKG-INFO
│   │   ├── SOURCES.txt
│   │   ├── dependency_links.txt
│   │   └── top_level.txt
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
│   └── utils
│       ├── __init__.py
│       └── utils.py
├── supervisord.conf
└── tests
    ├── __init__.py
    ├── conftest.py
    ├── test_data_preprocessing.py
    ├── test_drift_detection.py
    ├── test_dvc_pipelines.py
    ├── test_feature_engineering.py
    ├── test_mlflow_pipelines.py
    ├── test_models.py
    ├── test_predictions.py
    └── test_utils.py

725 directories, 1074 files
```
