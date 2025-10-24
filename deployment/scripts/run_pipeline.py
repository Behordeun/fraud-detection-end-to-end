#!/usr/bin/env python3
"""
Complete pipeline runner script.
"""
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*50}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: {description} failed!")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        return False
    else:
        print(f"SUCCESS: {description} completed!")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True

def main():
    """Run the complete ML pipeline."""
    
    print("🚀 Starting Fraud Detection Pipeline...")
    
    # Step 1: Setup data
    if not run_command("python scripts/setup_data.py", "Data Setup"):
        sys.exit(1)
    
    # Step 2: Run individual pipeline steps
    steps = [
        ("python src/data_preprocessing/preprocessing.py", "Data Preprocessing"),
        ("python src/data_preprocessing/feature_engineering.py", "Feature Engineering"),
        ("python src/models/train.py", "Model Training"),
        ("python src/models/evaluate.py", "Model Evaluation"),
        ("python src/models/predict.py", "Prediction Generation")
    ]
    
    for cmd, desc in steps:
        if not run_command(cmd, desc):
            print(f"❌ Pipeline failed at: {desc}")
            sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*60)
    
    print("\n🌐 Available Services:")
    print("- MLflow UI: http://localhost:5000")
    print("- API Documentation: http://localhost:8000/docs")
    print("- Monitoring Dashboard: streamlit run src/monitoring/dashboard.py")
    
    print("\n🚀 Quick Start Commands:")
    print("# Start MLflow UI")
    print("mlflow ui --host 0.0.0.0 --port 5000")
    print("\n# Start API server")
    print("python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000")
    print("\n# Start monitoring dashboard")
    print("streamlit run src/monitoring/dashboard.py")
    print("\n# Start all infrastructure")
    print("docker-compose up -d")

if __name__ == "__main__":
    main()