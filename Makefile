# Fraud Detection MLOps Makefile
# OS-adaptable commands for cross-platform compatibility

# OS Detection
ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
    PYTHON := python
    PIP := pip
    RM := del /Q
    MKDIR := mkdir
    SHELL_EXEC := cmd /c
else
    DETECTED_OS := $(shell uname -s)
    PYTHON := python3
    PIP := pip3
    RM := rm -rf
    MKDIR := mkdir -p
    SHELL_EXEC := 
endif

# Variables
PROJECT_NAME := fraud-detection-mlops
VENV_NAME := venv
DOCKER_COMPOSE := docker-compose
KAFKA_COMPOSE := docker-compose -f docker-compose-kafka.yml

# Colors for output (Unix-like systems)
ifneq ($(DETECTED_OS),Windows)
    GREEN := \033[0;32m
    YELLOW := \033[1;33m
    RED := \033[0;31m
    NC := \033[0m
    ECHO := echo -e
else
    GREEN := 
    YELLOW := 
    RED := 
    NC := 
    ECHO := echo
endif

.PHONY: help install setup clean test lint format

# Default target
help: ## Show this help message
	@$(ECHO) "$(GREEN)Fraud Detection MLOps Makefile$(NC)"
	@$(ECHO) "$(YELLOW)Available targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# Environment Setup
install: ## Install dependencies
	@$(ECHO) "$(YELLOW)Installing dependencies...$(NC)"
	$(PIP) install -r requirements.txt

setup: ## Setup project environment
	@$(ECHO) "$(YELLOW)Setting up project environment...$(NC)"
	$(MKDIR) data/raw data/processed data/predictions logs models
	$(PYTHON) scripts/setup_data.py

venv: ## Create virtual environment
	@$(ECHO) "$(YELLOW)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV_NAME)
ifeq ($(DETECTED_OS),Windows)
	$(VENV_NAME)\Scripts\activate && $(PIP) install -r requirements.txt
else
	. $(VENV_NAME)/bin/activate && $(PIP) install -r requirements.txt
endif

# Data Pipeline
data-setup: ## Setup and verify data
	$(PYTHON) scripts/setup_data.py

preprocess: ## Run data preprocessing
	cd src && $(PYTHON) -m fraud_detection.data.preprocessing

feature-engineering: ## Run feature engineering
	cd src && $(PYTHON) -m fraud_detection.data.feature_engineering

# Model Training
train: ## Train basic model
	cd src && $(PYTHON) -m fraud_detection.models.train

evaluate: ## Evaluate model
	cd src && $(PYTHON) -m fraud_detection.models.evaluate

predict: ## Generate predictions
	cd src && $(PYTHON) -m fraud_detection.models.predict

# Advanced ML
model-comparison: ## Run model comparison
	cd src && $(PYTHON) -m fraud_detection.models.model_comparison

hyperparameter-tuning: ## Run hyperparameter optimization
	cd src && $(PYTHON) -m fraud_detection.models.hyperparameter_tuning

# Complete Pipelines
pipeline: ## Run basic ML pipeline
	$(PYTHON) deployment/scripts/run_clean_pipeline.py

advanced-pipeline: ## Run advanced ML pipeline with all features
	$(PYTHON) deployment/scripts/run_advanced_pipeline.py

install-package: ## Install package in development mode
	$(PIP) install -e .

# Monitoring
drift-detection: ## Run drift detection
	$(PYTHON) src/monitoring/advanced_drift_detection.py

data-drift: ## Run data drift analysis
	$(PYTHON) src/monitoring/data_drift.py

model-drift: ## Run model drift analysis
	$(PYTHON) src/monitoring/model_drift.py

# Services
mlflow-ui: ## Start MLflow UI
	mlflow ui --host 0.0.0.0 --port 5000

api-server: ## Start API server
	cd src && $(PYTHON) -m uvicorn fraud_detection.api.app:app --host 0.0.0.0 --port 8000

dashboard: ## Start monitoring dashboard
	streamlit run src/fraud_detection/monitoring/dashboard.py

# Infrastructure
docker-up: ## Start Docker services
	docker-compose -f deployment/docker/docker-compose.yml up -d

docker-down: ## Stop Docker services
	docker-compose -f deployment/docker/docker-compose.yml down

kafka-up: ## Start Kafka infrastructure
	docker-compose -f deployment/docker/docker-compose-kafka.yml up -d

kafka-down: ## Stop Kafka infrastructure
	docker-compose -f deployment/docker/docker-compose-kafka.yml down

# Streaming
stream-producer: ## Start Kafka producer
	cd src && $(PYTHON) -m fraud_detection.streaming.kafka_producer

stream-consumer: ## Start Kafka consumer
	cd src && $(PYTHON) -m fraud_detection.streaming.kafka_consumer

# Development
test: ## Run tests
	pytest tests/ -v

test-coverage: ## Run tests with coverage
	pytest tests/ --cov=src --cov-report=html --cov-report=term

lint: ## Run code linting
	flake8 src/ tests/
	black --check src/ tests/

format: ## Format code
	black src/ tests/
	isort src/ tests/

# Cleaning
clean: ## Clean temporary files
	$(RM) __pycache__ .pytest_cache .coverage htmlcov
	$(RM) *.pyc *.pyo *.pyd
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "__pycache__" -type d -exec $(RM) {} + 2>/dev/null || true

clean-data: ## Clean processed data
	$(RM) data/processed data/predictions

clean-models: ## Clean trained models
	$(RM) models mlruns

clean-all: clean clean-data clean-models ## Clean everything

# Quick Start Combinations
dev-setup: venv install setup ## Complete development setup
	@$(ECHO) "$(GREEN)Development environment ready!$(NC)"

quick-start: setup pipeline mlflow-ui ## Quick start with basic pipeline
	@$(ECHO) "$(GREEN)Basic pipeline completed! MLflow UI starting...$(NC)"

full-start: setup advanced-pipeline kafka-up docker-up ## Full production setup
	@$(ECHO) "$(GREEN)Full production environment starting...$(NC)"

# Deployment
deploy-dev: ## Deploy development environment
	$(PYTHON) deployment/scripts/deploy.py --platform docker --environment dev

deploy-prod: ## Deploy production environment
	$(PYTHON) deployment/scripts/deploy.py --platform docker --environment prod

deploy-k8s: ## Deploy to Kubernetes
	$(PYTHON) deployment/scripts/deploy.py --platform kubernetes

build-image: ## Build Docker image
	docker build -f deployment/docker/Dockerfile.prod -t fraud-detection:latest .

# Monitoring Stack
monitoring-stack: docker-up dashboard ## Start complete monitoring stack
	@$(ECHO) "$(GREEN)Monitoring stack started!$(NC)"
	@$(ECHO) "Access points:"
	@$(ECHO) "- MLflow: http://localhost:5000"
	@$(ECHO) "- API: http://localhost:8000/docs"
	@$(ECHO) "- Dashboard: http://localhost:8501"
	@$(ECHO) "- Grafana: http://localhost:3000"

# Real-time Processing
realtime: kafka-up stream-producer stream-consumer ## Start real-time processing
	@$(ECHO) "$(GREEN)Real-time fraud detection started!$(NC)"

# Health Checks
health-check: ## Check system health
	@$(ECHO) "$(YELLOW)Checking system health...$(NC)"
	@curl -f http://localhost:8000/health 2>/dev/null && $(ECHO) "$(GREEN)API: OK$(NC)" || $(ECHO) "$(RED)API: DOWN$(NC)"
	@curl -f http://localhost:5000 2>/dev/null && $(ECHO) "$(GREEN)MLflow: OK$(NC)" || $(ECHO) "$(RED)MLflow: DOWN$(NC)"

# Documentation
docs: ## Generate documentation
	@$(ECHO) "$(YELLOW)Available documentation:$(NC)"
	@$(ECHO) "- README.md: Project overview"
	@$(ECHO) "- EXECUTION_GUIDE.md: Step-by-step execution"
	@$(ECHO) "- ADVANCED_FEATURES.md: Advanced features guide"
	@$(ECHO) "- QUICKSTART.md: Quick start guide"

# Status
status: ## Show project status
	@$(ECHO) "$(GREEN)Project Status:$(NC)"
	@$(ECHO) "OS: $(DETECTED_OS)"
	@$(ECHO) "Python: $(shell $(PYTHON) --version 2>&1)"
	@$(ECHO) "Project: $(PROJECT_NAME)"
	@ls -la data/ 2>/dev/null || dir data\ 2>nul || $(ECHO) "No data directory"
	@ls -la models/ 2>/dev/null || dir models\ 2>nul || $(ECHO) "No models directory"