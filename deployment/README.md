# 🚀 Deployment Guide

## 📁 Directory Structure

```
deployment/
├── docker/                   # Docker configurations
│   ├── docker-compose.yml    # Development environment
│   ├── docker-compose-kafka.yml  # Kafka infrastructure
│   ├── docker-compose.prod.yml   # Production environment
│   ├── Dockerfile            # Development image
│   └── Dockerfile.prod       # Production image
├── kubernetes/               # Kubernetes manifests
│   ├── namespace.yaml        # K8s namespace
│   ├── api-deployment.yaml   # API deployment
│   ├── mlflow/              # MLflow deployment
│   ├── kafka/               # Kafka deployment
│   └── monitoring/          # Monitoring stack
└── scripts/                 # Deployment scripts
    ├── deploy.py            # Main deployment script
    ├── run_clean_pipeline.py
    └── run_advanced_pipeline.py
```

## 🐳 Docker Deployment

### Development
```bash
# Using Makefile
make docker-up

# Or directly
docker-compose -f deployment/docker/docker-compose.yml up -d
```

### Production
```bash
# Build production image
make build-image

# Deploy production stack
make deploy-prod

# Or using script
python deployment/scripts/deploy.py --platform docker --environment prod
```

### Kafka Infrastructure
```bash
# Start Kafka
make kafka-up

# Or directly
docker-compose -f deployment/docker/docker-compose-kafka.yml up -d
```

## ☸️ Kubernetes Deployment

### Prerequisites
```bash
# Ensure kubectl is configured
kubectl cluster-info

# Create namespace
kubectl apply -f deployment/kubernetes/namespace.yaml
```

### Deploy to Kubernetes
```bash
# Using Makefile
make deploy-k8s

# Or using script
python deployment/scripts/deploy.py --platform kubernetes

# Or manually
kubectl apply -f deployment/kubernetes/
```

### Check Deployment
```bash
# Check pods
kubectl get pods -n fraud-detection

# Check services
kubectl get services -n fraud-detection

# Get API URL
kubectl get service fraud-detection-api-service -n fraud-detection
```

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
export API_HOST=0.0.0.0
export API_PORT=8000

# MLflow Configuration
export MLFLOW_TRACKING_URI=http://localhost:5000

# Kafka Configuration
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
export KAFKA_TOPIC=fraud-transactions
```

### Docker Environment Files
Create `.env` file in deployment/docker/:
```bash
# MLflow
MLFLOW_TRACKING_URI=http://mlflow:5000

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# Database (if using)
DATABASE_URL=postgresql://user:pass@db:5432/fraud_detection
```

## 🎯 Quick Deployment Commands

### Complete Development Setup
```bash
make install-package
make docker-up
make pipeline
```

### Production Deployment
```bash
make build-image
make deploy-prod
```

### Kubernetes Production
```bash
make build-image
docker tag fraud-detection:latest your-registry/fraud-detection:latest
docker push your-registry/fraud-detection:latest
make deploy-k8s
```

## 📊 Service Access

### Development
- **API**: http://localhost:8000
- **MLflow**: http://localhost:5000
- **Grafana**: http://localhost:3000
- **Kafka UI**: http://localhost:8090

### Production
- **API**: Load balancer IP:8000
- **MLflow**: Load balancer IP:5000
- **Monitoring**: Load balancer IP:3000

## 🔍 Monitoring

### Health Checks
```bash
# API health
curl http://localhost:8000/health

# MLflow health
curl http://localhost:5000

# Kubernetes health
kubectl get pods -n fraud-detection
```

### Logs
```bash
# Docker logs
docker-compose -f deployment/docker/docker-compose.yml logs -f

# Kubernetes logs
kubectl logs -f deployment/fraud-detection-api -n fraud-detection
```

## 🛠️ Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Check port usage
   lsof -i :8000
   
   # Kill process
   kill -9 $(lsof -t -i:8000)
   ```

2. **Docker build issues**
   ```bash
   # Clean build
   docker system prune -a
   make build-image
   ```

3. **Kubernetes deployment issues**
   ```bash
   # Check events
   kubectl get events -n fraud-detection
   
   # Describe pod
   kubectl describe pod <pod-name> -n fraud-detection
   ```

## 🔄 CI/CD Integration

### GitHub Actions
The deployment scripts integrate with GitHub Actions:
```yaml
- name: Deploy to production
  run: python deployment/scripts/deploy.py --platform docker --environment prod
```

### Jenkins
```groovy
stage('Deploy') {
    steps {
        sh 'python deployment/scripts/deploy.py --platform kubernetes'
    }
}
```