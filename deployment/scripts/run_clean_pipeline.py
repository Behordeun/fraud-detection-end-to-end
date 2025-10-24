#!/usr/bin/env python3
"""
Clean pipeline runner with proper imports.
"""
import sys
import subprocess
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

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
    """Run the complete ML pipeline."""
    
    print("🚀 Starting Clean Fraud Detection Pipeline...")
    
    # Step 1: Setup data
    if not run_command("python scripts/setup_data.py", "Data Setup"):
        sys.exit(1)
    
    # Step 2: Run pipeline steps with proper module paths
    steps = [
        ("python -m fraud_detection.data.preprocessing", "Data Preprocessing"),
        ("python -m fraud_detection.data.feature_engineering", "Feature Engineering"),
        ("python -m fraud_detection.models.train", "Model Training"),
        ("python -m fraud_detection.models.evaluate", "Model Evaluation"),
        ("python -m fraud_detection.models.predict", "Prediction Generation")
    ]
    
    for cmd, desc in steps:
        if not run_command(f"cd src && {cmd}", desc):
            print(f"⚠️ {desc} failed, continuing with pipeline...")
    
    print("\n" + "="*60)
    print("✅ CLEAN PIPELINE COMPLETED!")
    print("="*60)
    
    print("\n🌐 Available Services:")
    print("- MLflow UI: mlflow ui --host 0.0.0.0 --port 5000")
    print("- API Server: python -m fraud_detection.api.app")
    print("- Dashboard: streamlit run src/fraud_detection/monitoring/dashboard.py")

if __name__ == "__main__":
    main()