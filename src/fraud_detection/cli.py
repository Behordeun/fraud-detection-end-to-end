"""Command line interface for fraud detection system."""

import click
from pathlib import Path
import sys

@click.group()
def main():
    """Fraud Detection MLOps CLI."""
    pass

@main.command()
def setup():
    """Setup project environment."""
    from fraud_detection.utils.config import DATA_DIR, MODELS_DIR, LOGS_DIR
    
    # Create directories
    for dir_path in [DATA_DIR, MODELS_DIR, LOGS_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    click.echo("✅ Project environment setup complete!")

@main.command()
def preprocess():
    """Run data preprocessing."""
    from fraud_detection.data.preprocessing import main as preprocess_main
    preprocess_main()

@main.command()
def train():
    """Train the model."""
    from fraud_detection.models.train import main as train_main
    train_main()

@main.command()
def evaluate():
    """Evaluate the model."""
    from fraud_detection.models.evaluate import main as evaluate_main
    evaluate_main()

@main.command()
def predict():
    """Generate predictions."""
    from fraud_detection.models.predict import main as predict_main
    predict_main()

@main.command()
@click.option('--host', default='0.0.0.0', help='API host')
@click.option('--port', default=8000, help='API port')
def serve(host, port):
    """Start the API server."""
    import uvicorn
    uvicorn.run("fraud_detection.api.app:app", host=host, port=port)

if __name__ == "__main__":
    main()