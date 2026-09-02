from pyspark.ml.feature import VectorAssembler
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


def engineer_features(input_path: str, output_path: str):
    """Main feature engineering pipeline."""
    spark = SparkSession.builder.appName("FeatureEngineering").getOrCreate()

    print(f"Loading data from {input_path}...")
    df = spark.read.parquet(f"{input_path}/train")
    test_df = spark.read.parquet(f"{input_path}/test")

    # Apply feature engineering to both datasets
    for dataset_name, dataset in [("train", df), ("test", test_df)]:
        print(f"Engineering features for {dataset_name} dataset...")

        # Apply all feature engineering steps
        dataset = create_time_features(dataset)
        dataset = create_amount_features(dataset)
        dataset = create_pca_features(dataset)
        dataset = create_interaction_features(dataset)

        # Preprocessing already assembled a `features` vector; drop it so this
        # stage can rebuild the vector over the newly engineered columns.
        if "features" in dataset.columns:
            dataset = dataset.drop("features")

        # Assemble the feature vector from numeric columns only. The string
        # categoricals (Time_Period, Amount_Category) are human-readable labels
        # derived from numeric features already in the vector, and VectorAssembler
        # cannot consume string columns, so they are excluded.
        excluded = {"Class", "features"}
        feature_cols = [
            name
            for name, dtype in dataset.dtypes
            if name not in excluded and dtype not in ("string",)
        ]
        assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
        dataset = assembler.transform(dataset)

        # Save engineered dataset
        print(f"Saving engineered {dataset_name} data...")
        dataset.write.mode("overwrite").parquet(f"{output_path}/{dataset_name}")

    print("Feature engineering completed!")


if __name__ == "__main__":
    from fraud_detection.utils.config import PROCESSED_DATA_DIR

    INPUT_PATH = str(PROCESSED_DATA_DIR)
    OUTPUT_PATH = str(PROCESSED_DATA_DIR / "engineered")

    engineer_features(INPUT_PATH, OUTPUT_PATH)
