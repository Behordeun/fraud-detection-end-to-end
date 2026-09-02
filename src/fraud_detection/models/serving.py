"""Serving-time feature reproduction.

The model is trained on features produced by two steps the raw request does not
carry: the Amount ``StandardScaler`` fit during preprocessing, and the
feature-engineering transform chain. Scoring a raw transaction with only a
VectorAssembler over the 31 input columns feeds the model a different vector
than it was trained on (training/serving skew), so predictions are silently
wrong.

This module rebuilds the training features at inference time from the same
code: it applies the persisted, already-fitted Amount scaler, then the shared
``apply_feature_transforms`` chain, then hands the frame to the persisted
``PipelineModel`` (whose first stage is the assembler). The scaler is loaded,
never re-fit, so no held-out statistics leak and every request is scaled with
the training distribution.
"""

import os

from pyspark.ml.feature import StandardScalerModel, VectorAssembler
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, udf
from pyspark.sql.types import DoubleType

from fraud_detection.data.feature_engineering import apply_feature_transforms

_AMOUNT_ASSEMBLED = "Amount_feature"
_AMOUNT_SCALED = "scaled_Amount"


def _apply_amount_scaler(df: DataFrame, scaler_model: StandardScalerModel) -> DataFrame:
    """Apply the persisted Amount scaler, matching preprocessing exactly.

    Mirrors ``preprocessing.apply_amount_scaler``: assemble Amount into a single
    vector, transform with the fitted scaler, then collapse the scaled vector
    back to a scalar Amount column so downstream feature engineering sees the
    same scaled Amount the model trained on.
    """
    assembler = VectorAssembler(inputCols=["Amount"], outputCol=_AMOUNT_ASSEMBLED)
    df = assembler.transform(df)
    df = scaler_model.transform(df)

    to_scalar = udf(lambda v: float(v[0]), DoubleType())
    df = df.withColumn("Amount", to_scalar(col(_AMOUNT_SCALED)))
    return df.drop(_AMOUNT_ASSEMBLED, _AMOUNT_SCALED)


def build_serving_features(
    df: DataFrame, scaler_model: StandardScalerModel
) -> DataFrame:
    """Turn a raw-transaction frame into the frame the PipelineModel expects.

    Same chain as training: scale Amount with the fitted scaler, then apply the
    shared feature-engineering transforms. The assembler is a stage of the
    PipelineModel, so it is deliberately NOT applied here.
    """
    df = _apply_amount_scaler(df, scaler_model)
    return apply_feature_transforms(df)


def load_amount_scaler(scaler_path: str) -> StandardScalerModel:
    """Load the persisted Amount StandardScaler fit during training."""
    if not os.path.isdir(scaler_path):
        raise FileNotFoundError(
            f"Amount scaler not found at {scaler_path}; train the model first "
            f"so the fitted scaler is persisted alongside it."
        )
    return StandardScalerModel.load(scaler_path)
