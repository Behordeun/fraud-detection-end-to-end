from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import abs as spark_abs
from pyspark.sql.functions import col, greatest, lit, log, sqrt, when


def create_time_features(df: DataFrame) -> DataFrame:
    """Create time-based features from the Time column."""
    print("Creating time-based features...")

    # Convert seconds to hours
    df = df.withColumn("Hour", (col("Time") / 3600) % 24)

    # Create time periods
    df = df.withColumn(
        "Time_Period",
        when((col("Hour") >= 6) & (col("Hour") < 12), "Morning")
        .when((col("Hour") >= 12) & (col("Hour") < 18), "Afternoon")
        .when((col("Hour") >= 18) & (col("Hour") < 24), "Evening")
        .otherwise("Night"),
    )

    return df


def create_amount_features(df: DataFrame) -> DataFrame:
    """Create amount-based features."""
    print("Creating amount-based features...")

    # Amount is standardized upstream and can be negative, which makes a naive
    # log/sqrt produce NaN and breaks the downstream VectorAssembler. Clamp to a
    # safe domain: log1p on a value floored at 0, sqrt on the magnitude.
    df = df.withColumn("Amount_log", log(greatest(col("Amount"), lit(0.0)) + 1))
    df = df.withColumn("Amount_sqrt", sqrt(spark_abs(col("Amount"))))

    # Amount categories
    df = df.withColumn(
        "Amount_Category",
        when(col("Amount") == 0, "Zero")
        .when(col("Amount") <= 10, "Small")
        .when(col("Amount") <= 100, "Medium")
        .when(col("Amount") <= 1000, "Large")
        .otherwise("Very_Large"),
    )

    return df


def create_pca_features(df: DataFrame) -> DataFrame:
    """Create features based on PCA components."""
    print("Creating PCA-based features...")

    # Get PCA columns (V1 to V28)
    pca_cols = [f"V{i}" for i in range(1, 29)]

    # Create magnitude of PCA vector
    sum_expr = sum([col(c) * col(c) for c in pca_cols])
    df = df.withColumn("PCA_Magnitude", sqrt(sum_expr))

    # Create features based on PCA component ranges
    df = df.withColumn("V1_to_V10_sum", sum([col(f"V{i}") for i in range(1, 11)]))
    df = df.withColumn("V11_to_V20_sum", sum([col(f"V{i}") for i in range(11, 21)]))
    df = df.withColumn("V21_to_V28_sum", sum([col(f"V{i}") for i in range(21, 29)]))

    return df


def create_interaction_features(df: DataFrame) -> DataFrame:
    """Create interaction features."""
    print("Creating interaction features...")

    # Amount and time interactions
    df = df.withColumn("Amount_Hour_Interaction", col("Amount") * col("Hour"))

    # High-impact PCA components with amount
    df = df.withColumn("V1_Amount", col("V1") * col("Amount"))
    df = df.withColumn("V2_Amount", col("V2") * col("Amount"))
    df = df.withColumn("V3_Amount", col("V3") * col("Amount"))

    return df


# Columns excluded from the assembled feature vector: the label, any stale
# vector, and the string categoricals (human-readable labels derived from
# numeric features already present; VectorAssembler cannot consume strings).
_NON_FEATURE_COLUMNS = {"Class", "features"}


def apply_feature_transforms(df: DataFrame) -> DataFrame:
    """Apply every feature-engineering transform to a dataframe.

    This is the single source of truth for the transform chain. Both the
    training pipeline stage and the serving path call it, so the features a
    model is trained on are byte-for-byte the features it scores at inference
    time. It does NOT assemble the vector: the assembler is a stage of the
    persisted PipelineModel so it travels with the model.
    """
    df = create_time_features(df)
    df = create_amount_features(df)
    df = create_pca_features(df)
    df = create_interaction_features(df)

    # Preprocessing may have assembled a `features` vector; drop it so a later
    # assembler can rebuild the vector over the newly engineered columns.
    if "features" in df.columns:
        df = df.drop("features")
    return df


def feature_vector_columns(df: DataFrame) -> list:
    """Return the numeric columns the feature vector is assembled from.

    Order is the dataframe's column order, which the training assembler and the
    serving assembler both consume identically, so no reordering skew arises.
    """
    return [
        name
        for name, dtype in df.dtypes
        if name not in _NON_FEATURE_COLUMNS and dtype not in ("string",)
    ]


def engineer_features(input_path: str, output_path: str):
    """Main feature engineering pipeline.

    Writes the engineered numeric columns (no assembled ``features`` vector):
    the training PipelineModel owns the VectorAssembler stage, so assembly lives
    with the model and is replayed identically at serving time.
    """
    spark = SparkSession.builder.appName("FeatureEngineering").getOrCreate()

    print(f"Loading data from {input_path}...")
    df = spark.read.parquet(f"{input_path}/train")
    test_df = spark.read.parquet(f"{input_path}/test")

    # Apply feature engineering to both datasets
    for dataset_name, dataset in [("train", df), ("test", test_df)]:
        print(f"Engineering features for {dataset_name} dataset...")

        dataset = apply_feature_transforms(dataset)

        # Save engineered columns only; the model's pipeline assembles the
        # vector. Drop string categoricals VectorAssembler cannot consume.
        string_cols = [name for name, dtype in dataset.dtypes if dtype == "string"]
        if string_cols:
            dataset = dataset.drop(*string_cols)

        print(f"Saving engineered {dataset_name} data...")
        dataset.write.mode("overwrite").parquet(f"{output_path}/{dataset_name}")

    print("Feature engineering completed!")


if __name__ == "__main__":
    from fraud_detection.utils.config import PROCESSED_DATA_DIR

    INPUT_PATH = str(PROCESSED_DATA_DIR)
    OUTPUT_PATH = str(PROCESSED_DATA_DIR / "engineered")

    engineer_features(INPUT_PATH, OUTPUT_PATH)
