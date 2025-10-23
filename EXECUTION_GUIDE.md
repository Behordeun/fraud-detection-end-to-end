# Complete Execution Guide

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Complete Pipeline
```bash
python scripts/run_pipeline.py
```

### 3. Start Services
```bash
# Start MLflow UI
mlflow ui --host 0.0.0.0 --port 5000 &

# Start API server
python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000 &

# Start Docker services (optional)
docker-compose up -d
```

## 📋 Step-by-Step Execution

### Phase 1: Data Setup and Preprocessing
```bash
# 1. Setup data directories and verify dataset
python scripts/setup_data.py

# 2. Run data preprocessing
python src/data_preprocessing/preprocessing.py

# 3. Run feature engineering
python src/data_preprocessing/feature_engineering.py
```

### Phase 2: Model Training and Evaluation
```bash
# 4. Train the model
python src/models/train.py

# 5. Evaluate the model
python src/models/evaluate.py

# 6. Make predictions on new data
python src/models/predict.py
```

### Phase 3: Services and Monitoring
```bash
# 7. Start MLflow tracking server
mlflow server --host 0.0.0.0 --port 5000

# 8. Start prediction API
python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000

# 9. Start infrastructure services
docker-compose up -d
```

## 🔧 Alternative: DVC Pipeline
```bash
# Initialize DVC (if not done)
dvc init --no-scm

# Run complete DVC pipeline
dvc repro

# Push data to remote (if configured)
dvc push
```

## 📊 Expected Results

After running the pipeline, you should see:

### Data Processing
- **Original dataset**: ~284K transactions
- **Fraud rate**: ~0.17% (highly imbalanced)
- **Features**: 30 columns (Time, V1-V28, Amount, Class)
- **Processed data**: Saved in `data/processed/`

### Model Performance
- **AUC**: > 0.95
- **Precision**: > 0.80
- **Recall**: > 0.75
- **F1 Score**: > 0.77

### Generated Artifacts
- **Models**: Saved in `models/`
- **Predictions**: Saved in `data/predictions/`
- **MLflow runs**: Tracked in `mlruns/`
- **Logs**: Available in `logs/`

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| MLflow UI | http://localhost:5000 | Experiment tracking |
| API Docs | http://localhost:8000/docs | Model serving API |
| Grafana | http://localhost:3000 | Monitoring dashboards |
| MinIO Console | http://localhost:9001 | Data storage |
| Prometheus | http://localhost:9090 | Metrics collection |

## 🧪 Testing the API

### Single Prediction
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "Time": 0,
    "V1": -1.359807134,
    "V2": -0.072781173,
    "V3": 2.536346738,
    "V4": 1.378155224,
    "V5": -0.338320770,
    "V6": 0.462387778,
    "V7": 0.239598554,
    "V8": 0.098697901,
    "V9": 0.363786969,
    "V10": 0.090794172,
    "V11": -0.551599533,
    "V12": -0.617800856,
    "V13": -0.991389847,
    "V14": -0.311169354,
    "V15": 1.468176972,
    "V16": -0.470400525,
    "V17": 0.207971242,
    "V18": 0.025790613,
    "V19": 0.403992960,
    "V20": 0.251412098,
    "V21": -0.018306778,
    "V22": 0.277837576,
    "V23": -0.110473910,
    "V24": 0.066928075,
    "V25": 0.128539358,
    "V26": -0.189114844,
    "V27": 0.133558377,
    "V28": -0.021053053,
    "Amount": 149.62
  }'
```

## 🐛 Troubleshooting

### Common Issues

1. **Java not found for PySpark**
   ```bash
   # Install Java 8 or 11
   brew install openjdk@11  # macOS
   sudo apt install openjdk-11-jdk  # Ubuntu
   ```

2. **Port already in use**
   ```bash
   # Kill process on port
   lsof -ti:5000 | xargs kill -9
   ```

3. **Memory issues**
   ```bash
   # Reduce Spark memory in train.py
   .config("spark.driver.memory", "2g")
   ```

4. **Docker services not starting**
   ```bash
   # Check logs
   docker-compose logs
   
   # Restart services
   docker-compose down && docker-compose up -d
   ```

### Verification Steps

1. **Check data processing**
   ```bash
   ls -la data/processed/
   # Should show train/, test/, new_data/ directories
   ```

2. **Check model training**
   ```bash
   ls -la models/
   # Should show random_forest_model/ directory
   ```

3. **Check MLflow tracking**
   ```bash
   ls -la mlruns/
   # Should show experiment directories
   ```

4. **Check predictions**
   ```bash
   ls -la data/predictions/
   # Should show prediction parquet files
   ```

## 📈 Next Steps

1. **Hyperparameter Tuning**: Modify `src/models/train.py`
2. **Feature Engineering**: Add features in `src/data_preprocessing/feature_engineering.py`
3. **Model Comparison**: Add different algorithms
4. **Real-time Monitoring**: Setup Grafana dashboards
5. **Production Deployment**: Use Kubernetes configs in `k8s/`

## 🔄 Continuous Integration

For automated pipeline execution:
```bash
# Setup cron job for daily retraining
0 2 * * * cd /path/to/project && python scripts/run_pipeline.py
```