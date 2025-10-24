# 🧹 Clean Codebase Structure

## 📁 New Directory Structure

```
src/fraud_detection/
├── __init__.py
├── cli.py                    # Command line interface
├── data/                     # Data processing modules
│   ├── __init__.py
│   ├── preprocessing.py
│   └── feature_engineering.py
├── models/                   # ML model modules
│   ├── __init__.py
│   ├── train.py
│   ├── evaluate.py
│   ├── predict.py
│   ├── model_comparison.py
│   └── hyperparameter_tuning.py
├── monitoring/               # Monitoring and drift detection
│   ├── __init__.py
│   ├── dashboard.py
│   ├── data_drift.py
│   ├── model_drift.py
│   └── advanced_drift_detection.py
├── api/                      # REST API
│   ├── __init__.py
│   └── app.py
├── streaming/                # Real-time streaming
│   ├── __init__.py
│   ├── kafka_producer.py
│   └── kafka_consumer.py
├── pipelines/                # Pipeline orchestration
│   ├── __init__.py
│   ├── dvc_pipeline.py
│   └── mlflow_pipeline.py
└── utils/                    # Utilities and configuration
    ├── __init__.py
    └── config.py
```

## 🚀 Usage with New Structure

### Package Installation
```bash
# Install in development mode
pip install -e .

# Or use Makefile
make install-package
```

### CLI Interface
```bash
# Setup environment
fraud-detection setup

# Run individual components
fraud-detection preprocess
fraud-detection train
fraud-detection evaluate

# Start API server
fraud-detection serve --host 0.0.0.0 --port 8000
```

### Module Imports
```bash
# Run as modules
python -m fraud_detection.data.preprocessing
python -m fraud_detection.models.train
python -m fraud_detection.api.app
```

### Makefile Commands (Updated)
```bash
# Install package
make install-package

# Run pipeline
make pipeline

# Start services
make api-server
make dashboard

# Advanced features
make model-comparison
make hyperparameter-tuning
```

## 🔧 Key Improvements

### 1. **Proper Package Structure**
- All code under `src/fraud_detection/`
- Proper `__init__.py` files
- Installable package with `setup.py`

### 2. **Centralized Configuration**
- `utils/config.py` manages all paths and settings
- Environment variable support
- Consistent configuration across modules

### 3. **Module-based Execution**
- Run components as Python modules
- Proper import resolution
- No more path manipulation

### 4. **CLI Interface**
- `fraud-detection` command line tool
- Consistent interface for all operations
- Easy integration with CI/CD

### 5. **Clean Imports**
- No relative imports
- Consistent module structure
- Easy to test and maintain

## 🎯 Migration Benefits

### Before (Old Structure)
```bash
python src/models/train.py  # Path issues
python src/api/app.py       # Import errors
```

### After (Clean Structure)
```bash
fraud-detection train       # CLI interface
python -m fraud_detection.models.train  # Module execution
```

## 🔄 Updated Workflows

### Development Workflow
```bash
# 1. Install package
make install-package

# 2. Run pipeline
make pipeline

# 3. Start services
make api-server &
make dashboard &
```

### Production Deployment
```bash
# 1. Install package
pip install -e .

# 2. Use CLI
fraud-detection setup
fraud-detection train
fraud-detection serve
```

## 📊 Import Examples

### In Python Code
```python
# Import modules
from fraud_detection.data.preprocessing import load_data
from fraud_detection.models.train import train_model
from fraud_detection.utils.config import MODELS_DIR

# Use configuration
model_path = MODELS_DIR / "my_model"
```

### In Scripts
```python
# Add to sys.path (if needed)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Then import normally
from fraud_detection.utils.config import PROJECT_ROOT
```

This clean structure eliminates import errors, provides consistent interfaces, and makes the codebase production-ready! 🎉