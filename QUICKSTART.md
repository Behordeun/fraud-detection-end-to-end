# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Setup Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize DVC
dvc init --no-scm
```

### 2. Run Complete Pipeline
```bash
# Run everything with one command
python scripts/run_pipeline.py
```

### 3. Access Services
- **MLflow UI**: http://localhost:5000
- **API Documentation**: http://localhost:8000/docs

## 📋 What This Does

1. **Creates sample fraud detection dataset** (10K transactions, 0.2% fraud rate)
2. **Preprocesses data** (scaling, missing values, train/test split)
3. **Engineers features** (time-based, amount-based, PCA interactions)
4. **Trains RandomForest model** with MLflow tracking
5. **Evaluates model** (AUC, precision, recall, F1)
6. **Makes predictions** on new data
7. **Serves model** via REST API

## 🔧 Manual Steps

### Run Individual Components
```bash
# 1. Setup data
python scripts/setup_data.py

# 2. Run preprocessing
python src/data_preprocessing/preprocessing.py

# 3. Run feature engineering
python src/data_preprocessing/feature_engineering.py

# 4. Train model
python src/models/train.py

# 5. Evaluate model
python src/models/evaluate.py

# 6. Make predictions
python src/models/predict.py
```

### Start Services
```bash
# MLflow server
mlflow server --host 0.0.0.0 --port 5000

# API server
python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000

# Docker services
docker-compose up -d
```

## 📊 Expected Results

- **Model Performance**: AUC > 0.95, F1 > 0.80
- **Data**: 10K transactions processed
- **Predictions**: Available in `data/predictions/`
- **Experiments**: Tracked in MLflow

## 🐛 Troubleshooting

### Common Issues
1. **Java not found**: Install Java 8+ for PySpark
2. **Port conflicts**: Change ports in docker-compose.yml
3. **Memory issues**: Reduce dataset size in setup_data.py

### Check Status
```bash
# Check if services are running
docker-compose ps

# Check logs
docker-compose logs [service_name]
```

## 🎯 Next Steps

1. **Replace sample data** with real credit card fraud dataset
2. **Tune hyperparameters** in src/models/train.py
3. **Add more features** in src/data_preprocessing/feature_engineering.py
4. **Setup monitoring** with Grafana dashboards
5. **Deploy to production** using Kubernetes configs in k8s/