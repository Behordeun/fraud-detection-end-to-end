#!/usr/bin/env python3
"""
Advanced pipeline runner with all new features.
"""
import subprocess
import sys
from pathlib import Path
import time

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ {description} failed!")
        print(f"Error: {result.stderr}")
        return False
    else:
        print(f"✅ {description} completed!")
        return True

def main():
    """Run the advanced ML pipeline with all features."""
    
    print("🚀 Starting Advanced Fraud Detection Pipeline...")
    
    # Phase 1: Basic Pipeline
    basic_steps = [
        ("python scripts/setup_data.py", "Data Setup"),
        ("python src/data_preprocessing/preprocessing.py", "Data Preprocessing"),
        ("python src/data_preprocessing/feature_engineering.py", "Feature Engineering")
    ]
    
    for cmd, desc in basic_steps:
        if not run_command(cmd, desc):
            sys.exit(1)
    
    # Phase 2: Advanced Model Training
    print("\n🧠 Phase 2: Advanced Model Training")
    
    advanced_steps = [
        ("python src/models/model_comparison.py", "Model Comparison"),
        ("python src/models/hyperparameter_tuning.py", "Hyperparameter Tuning"),
        ("python src/models/train.py", "Final Model Training"),
        ("python src/models/evaluate.py", "Model Evaluation"),
        ("python src/models/predict.py", "Prediction Generation")
    ]
    
    for cmd, desc in advanced_steps:
        if not run_command(cmd, desc):
            print(f"⚠️ {desc} failed, continuing with pipeline...")
    
    # Phase 3: Advanced Monitoring
    print("\n📊 Phase 3: Advanced Monitoring")
    
    monitoring_steps = [
        ("python src/monitoring/advanced_drift_detection.py", "Drift Detection"),
        ("python src/monitoring/data_drift.py", "Data Drift Analysis"),
        ("python src/monitoring/model_drift.py", "Model Drift Analysis")
    ]
    
    for cmd, desc in monitoring_steps:
        if not run_command(cmd, desc):
            print(f"⚠️ {desc} failed, continuing...")
    
    print("\n" + "="*70)
    print("🎉 ADVANCED PIPELINE COMPLETED!")
    print("="*70)
    
    print("\n🌟 New Advanced Features Available:")
    print("1. 🔧 Hyperparameter Tuning: Automated optimization with Optuna")
    print("2. 🏆 Model Comparison: RandomForest vs GBT vs LogisticRegression")
    print("3. 🌊 Real-time Streaming: Kafka producer/consumer")
    print("4. 📈 Advanced Drift Detection: PSI, KS tests, JS distance")
    print("5. 🔄 CI/CD Pipeline: GitHub Actions automation")
    
    print("\n🚀 Quick Start Commands:")
    print("# Start Kafka infrastructure")
    print("docker-compose -f docker-compose-kafka.yml up -d")
    print("\n# Start real-time streaming")
    print("python -m fraud_detection.streaming.kafka_producer &")
    print("python -m fraud_detection.streaming.kafka_consumer &")
    print("\n# Start monitoring dashboard")
    print("streamlit run src/monitoring/dashboard.py")
    print("\n# Start MLflow and API")
    print("mlflow ui --host 0.0.0.0 --port 5000 &")
    print("python -m uvicorn fraud_detection.api.app:app --host 0.0.0.0 --port 8000 &")
    
    print("\n📊 Access Points:")
    print("- MLflow UI: http://localhost:5000")
    print("- API Docs: http://localhost:8000/docs")
    print("- Kafka UI: http://localhost:8090")
    print("- Monitoring Dashboard: http://localhost:8501")

if __name__ == "__main__":
    main()