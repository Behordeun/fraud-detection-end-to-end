from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pyspark.sql import SparkSession

app = FastAPI(title="Fraud Detection API", version="1.0.0")

# Initialize Spark session
spark = SparkSession.builder.appName("FraudDetectionAPI").getOrCreate()

from fraud_detection.models.loader import load_model  # noqa: E402
from fraud_detection.models.serving import (  # noqa: E402
    build_serving_features,
    load_amount_scaler,
)
from fraud_detection.utils.config import (  # noqa: E402
    AMOUNT_SCALER_DIR,
    CURRENT_MODEL_DIR,
)

# Load model + fitted scaler at startup
MODEL_PATH = str(CURRENT_MODEL_DIR)
SCALER_PATH = str(AMOUNT_SCALER_DIR)
model = None
amount_scaler = None


@app.on_event("startup")
async def load_artifacts():
    global model, amount_scaler
    try:
        model = load_model(MODEL_PATH)
        amount_scaler = load_amount_scaler(SCALER_PATH)
        print("Model and Amount scaler loaded successfully")
    except Exception as e:
        print(f"Error loading serving artifacts: {e}")


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
    return {
        "status": "healthy",
        "model_loaded": model is not None and amount_scaler is not None,
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict_fraud(transaction: TransactionData):
    if model is None or amount_scaler is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Reproduce the training features from the raw request: scale Amount with
        # the fitted scaler, apply the shared feature-engineering transforms,
        # then let the PipelineModel's assembler build the vector. This is the
        # same code path training used, so there is no training/serving skew.
        data_dict = transaction.dict()
        raw_df = spark.createDataFrame([data_dict])
        features_df = build_serving_features(raw_df, amount_scaler)

        prediction = model.transform(features_df)

        result = prediction.select("prediction", "probability").collect()[0]
        is_fraud = bool(result["prediction"])
        prob_array = result["probability"].toArray()
        # A single-class model emits a length-1 probability vector; there is no
        # class-1 probability to report, so fail clearly instead of IndexError.
        if len(prob_array) < 2:
            raise HTTPException(
                status_code=500,
                detail="Model returned a single-class probability vector",
            )
        fraud_prob = float(prob_array[1])  # Probability of fraud (class 1)

        if fraud_prob > 0.8:
            confidence = "high"
        elif fraud_prob > 0.6:
            confidence = "medium"
        else:
            confidence = "low"

        return PredictionResponse(
            is_fraud=is_fraud, fraud_probability=fraud_prob, confidence=confidence
        )

    except HTTPException:
        # Already a well-formed HTTP error (e.g. single-class vector); propagate
        # it rather than masking it as a generic 500.
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
