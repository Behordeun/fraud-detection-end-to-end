import numpy as np
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, when, log, sqrt, abs as spark_abs
from pyspark.ml.feature import VectorAssembler


def create_time_features(df: DataFrame) -> DataFrame:
    """Create time-based features from the Time column."""
    print("Creating time-based features...")
    
    # Convert seconds to hours
    df = df.withColumn("Hour", (col("Time") / 3600) % 24)
    
    # Create time periods
    df = df.withColumn("Time_Period", 
        when((col("Hour") >= 6) & (col("Hour") < 12), "Morning")
        .when((col("Hour") >= 12) & (col("Hour") < 18), "Afternoon")
        .when((col("Hour") >= 18) & (col("Hour") < 24), "Evening")
        .otherwise("Night")
    )
    
    return df


def create_amount_features(df: DataFrame) -> DataFrame:
    """Create amount-based features."""
    print("Creating amount-based features...")
    
    # Log transformation of amount (add 1 to handle zero values)
    df = df.withColumn("Amount_log", log(col("Amount") + 1))
    
    # Square root transformation
    df = df.withColumn("Amount_sqrt", sqrt(col("Amount")))
    
    # Amount categories
    df = df.withColumn("Amount_Category",
        when(col("Amount") == 0, "Zero")
        .when(col("Amount") <= 10, "Small")
        .when(col("Amount") <= 100, "Medium")
        .when(col("Amount") <= 1000, "Large")
        .otherwise("Very_Large")
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
        
        # Update feature vector
        feature_cols = [c for c in dataset.columns if c not in ["Class", "features"]]
        assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
        dataset = assembler.transform(dataset)
        
        # Save engineered dataset
        print(f"Saving engineered {dataset_name} data...")
        dataset.write.mode("overwrite").parquet(f"{output_path}/{dataset_name}")
    
    print("Feature engineering completed!")


if __name__ == "__main__":
    INPUT_PATH = "data/processed"
    OUTPUT_PATH = "data/processed/engineered"
    
    engineer_features(INPUT_PATH, OUTPUT_PATH)