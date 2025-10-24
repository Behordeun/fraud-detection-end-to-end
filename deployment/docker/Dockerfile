    # Build stage
FROM ubuntu:22.04 AS builder

# Set environment variables for build
ENV DEBIAN_FRONTEND=noninteractive
ENV OPENMETADATA_VERSION=0.13.0

# Install build dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Download and extract Prometheus
RUN wget https://github.com/prometheus/prometheus/releases/download/v2.44.0/prometheus-2.44.0.linux-amd64.tar.gz \
    && tar -xvzf prometheus-2.44.0.linux-amd64.tar.gz \
    && mv prometheus-2.44.0.linux-amd64 /prometheus \
    && rm prometheus-2.44.0.linux-amd64.tar.gz

# Download and extract Grafana
RUN wget https://dl.grafana.com/oss/release/grafana-10.0.4.linux-amd64.tar.gz \
    && tar -xvzf grafana-10.0.4.linux-amd64.tar.gz \
    && mv grafana-10.0.4 /grafana \
    && rm grafana-10.0.4.linux-amd64.tar.gz

# Download MinIO
RUN wget https://dl.min.io/server/minio/release/linux-amd64/minio \
    && chmod +x minio

# Download and extract OpenMetadata
RUN wget https://github.com/open-metadata/OpenMetadata/releases/download/${OPENMETADATA_VERSION}/openmetadata-helm.tar.gz \
    && tar -xvzf openmetadata-helm.tar.gz \
    && mv openmetadata /openmetadata \
    && rm openmetadata-helm.tar.gz

# Final stage
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV AIRFLOW_HOME=/opt/airflow
ENV MINIO_ROOT_USER=minioadmin
ENV MINIO_ROOT_PASSWORD=minioadmin

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    git \
    openjdk-11-jdk-headless \
    python3-pip \
    python3.11-venv \
    supervisor \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --upgrade pip \
    && pip3 install --no-cache-dir \
        dvc[s3] \
        apache-airflow==2.6.2 \
        apache-airflow-providers-docker \
        apache-airflow-providers-http \
        apache-airflow-providers-sqlite \
        prometheus_client \
        openmetadata-ingestion \
        mlflow

# Copy artifacts from builder stage
COPY --from=builder /prometheus /opt/prometheus
COPY --from=builder /grafana /opt/grafana
COPY --from=builder /minio /usr/local/bin/
COPY --from=builder /openmetadata /opt/openmetadata

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