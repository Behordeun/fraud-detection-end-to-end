# Base image
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV AIRFLOW_HOME=/opt/airflow
ENV MINIO_ROOT_USER=minioadmin
ENV MINIO_ROOT_PASSWORD=minioadmin
ENV OPENMETADATA_VERSION=0.13.0

# Update and install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    openjdk-11-jdk-headless \
    unzip \
    git \
    python3-pip \
    python3.11-venv \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --upgrade pip
RUN pip3 install \
    dvc[s3] \
    apache-airflow==2.6.2 \
    apache-airflow-providers-docker \
    apache-airflow-providers-http \
    apache-airflow-providers-sqlite \
    prometheus_client \
    openmetadata-ingestion \
    mlflow

# Install Prometheus
RUN wget https://github.com/prometheus/prometheus/releases/download/v2.44.0/prometheus-2.44.0.linux-amd64.tar.gz \
    && tar -xvzf prometheus-2.44.0.linux-amd64.tar.gz \
    && mv prometheus-2.44.0.linux-amd64 /opt/prometheus \
    && rm prometheus-2.44.0.linux-amd64.tar.gz

# Install Grafana
RUN wget https://dl.grafana.com/oss/release/grafana-10.0.4.linux-amd64.tar.gz \
    && tar -xvzf grafana-10.0.4.linux-amd64.tar.gz \
    && mv grafana-10.0.4 /opt/grafana \
    && rm grafana-10.0.4.linux-amd64.tar.gz

# Install MinIO
RUN wget https://dl.min.io/server/minio/release/linux-amd64/minio \
    && chmod +x minio \
    && mv minio /usr/local/bin/

# Install OpenMetadata
RUN wget https://github.com/open-metadata/OpenMetadata/releases/download/${OPENMETADATA_VERSION}/openmetadata-helm.tar.gz \
    && tar -xvzf openmetadata-helm.tar.gz \
    && mv openmetadata /opt/openmetadata \
    && rm openmetadata-helm.tar.gz

# Copy configuration files
COPY prometheus.yml /opt/prometheus/prometheus.yml
COPY airflow/airflow.cfg $AIRFLOW_HOME/airflow.cfg
COPY openmetadata/config.yaml /opt/openmetadata/config.yaml
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY alert-rules.yml /opt/prometheus/alert-rules.yml

# Create directories for services
RUN mkdir -p /data /logs /opt/airflow/dags /opt/airflow/plugins /opt/grafana/provisioning

# Expose ports for all services
EXPOSE 8080 9000 9001 9090 3000 8585

# Set Supervisor as the entry point to manage all services
CMD ["/usr/bin/supervisord"]
