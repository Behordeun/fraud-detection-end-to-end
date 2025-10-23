#!/usr/bin/env python3
"""
Script to download and setup the Credit Card Fraud Detection dataset.
"""
import os
import pandas as pd
import requests
from pathlib import Path

def download_sample_data():
    """Create a sample dataset for testing if real data is not available."""
    print("Creating sample fraud detection dataset...")
    
    # Create sample data with similar structure to credit card fraud dataset
    import numpy as np
    np.random.seed(42)
    
    n_samples = 10000
    n_fraud = int(n_samples * 0.002)  # 0.2% fraud rate
    
    # Generate PCA features (V1-V28)
    data = {}
    for i in range(1, 29):
        data[f'V{i}'] = np.random.normal(0, 1, n_samples)
    
    # Generate Time (seconds from first transaction)
    data['Time'] = np.random.uniform(0, 172800, n_samples)  # 48 hours
    
    # Generate Amount
    data['Amount'] = np.random.lognormal(3, 1.5, n_samples)
    
    # Generate Class (0 = normal, 1 = fraud)
    data['Class'] = np.zeros(n_samples)
    fraud_indices = np.random.choice(n_samples, n_fraud, replace=False)
    data['Class'][fraud_indices] = 1
    
    # Make fraud transactions more extreme
    for idx in fraud_indices:
        # Modify some V features for fraud cases
        for v in ['V1', 'V2', 'V3', 'V4', 'V14']:
            if v in data:
                data[v][idx] *= np.random.uniform(2, 5)
        # Fraud transactions tend to have different amounts
        data['Amount'][idx] *= np.random.uniform(0.1, 3)
    
    df = pd.DataFrame(data)
    return df

def setup_data_directory():
    """Setup data directory structure and download/create dataset."""
    
    # Create directories
    data_dir = Path("data")
    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"
    
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    predictions_dir = data_dir / "predictions"
    predictions_dir.mkdir(parents=True, exist_ok=True)
    
    dataset_path = raw_dir / "creditcard_2023.csv"
    
    if dataset_path.exists():
        print(f"Real dataset found at {dataset_path}")
        # Load and display basic info about the real dataset
        df = pd.read_csv(dataset_path)
        print(f"Dataset shape: {df.shape}")
        print(f"Fraud rate: {df['Class'].mean():.4f}")
        print(f"Columns: {list(df.columns)}")
    else:
        print("Dataset not found. Creating sample dataset...")
        df = download_sample_data()
        df.to_csv(dataset_path, index=False)
        print(f"Sample dataset created at {dataset_path}")
        print(f"Dataset shape: {df.shape}")
        print(f"Fraud rate: {df['Class'].mean():.4f}")
    
    return dataset_path

if __name__ == "__main__":
    setup_data_directory()