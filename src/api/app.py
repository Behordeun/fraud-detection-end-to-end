from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
from pyspark.ml.classification import RandomForestClassificationModel
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
import mlflow
from typing import List

app = FastAPI(title="Fraud Detection API", version="1.0.0")

# Initialize Spark session
spark = SparkSession.builder.appName("FraudDetectionAPI").getOrCreate()

# Load model at startup
MODEL_PATH = "models/random_forest_model"
model = None

@app.on_event("startup")
async def load_model():
    global model
    try:
        model = RandomForestClassificationModel.load(MODEL_PATH)
        print("Model loaded successfully")
    except Exception as e:
        print(f"Error loading model: {e}")

class TransactionData(BaseModel):
    Time: float
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    Amount: float

class PredictionResponse(BaseModel):
    is_fraud: bool
    fraud_probability: float
    confidence: str

@app.get("/")
async def root():
    return {"message": "Fraud Detection API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict", response_model=PredictionResponse)
async def predict_fraud(transaction: TransactionData):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Convert to DataFrame
        data_dict = transaction.dict()
        df = spark.createDataFrame([data_dict])
        
        # Create features vector
        feature_cols = list(data_dict.keys())
        assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
        df_with_features = assembler.transform(df)
        
        # Make prediction
        prediction = model.transform(df_with_features)
        
        # Extract results
        result = prediction.select("prediction", "probability").collect()[0]
        is_fraud = bool(result["prediction"])
        prob_array = result["probability"].toArray()
        fraud_prob = float(prob_array[1])  # Probability of fraud (class 1)
        
        # Determine confidence level
        if fraud_prob > 0.8:
            confidence = "high"
        elif fraud_prob > 0.6:
            confidence = "medium"
        else:
            confidence = "low"
        
        return PredictionResponse(
            is_fraud=is_fraud,
            fraud_probability=fraud_prob,
            confidence=confidence
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)