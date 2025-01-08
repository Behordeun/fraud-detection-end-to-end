from pyspark.ml.feature import VectorAssembler
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, lit, log, pow, sqrt, when


def load_data(input_path: str) -> DataFrame:
    """
    Load the preprocessed data from Parquet files.
    """
    spark = SparkSession.builder.appName(
        "CreditCardFraudFeatureEngineering"
    ).getOrCreate()

    print(f"Loading data from {input_path}...")
    df = spark.read.parquet(input_path)
    print(f"Data loaded with schema: {df.printSchema()}")
    return df


def add_derived_features(df: DataFrame) -> DataFrame:
    """
    Add new derived features to the dataset.
    Examples:
    - Log transformation for skewed features
    - Interaction terms
    - Polynomial features
    """
    print("Adding derived features...")

    # Example: Log transformation (to reduce skewness for features > 0)
    numerical_cols = [
        field
        for field, dtype in df.dtypes
        if dtype in ["int", "double"] and field != "label"
    ]
    for col_name in numerical_cols:
        if col_name not in [
            "features",
            "scaled_features",
        ]:  # Avoid columns already in vectorized form
            df = df.withColumn(
                f"log_{col_name}",
                when(df[col_name] > 0, log(df[col_name])).otherwise(lit(0)),
            )

    # Example: Interaction terms (multiplication of selected features)
    df = df.withColumn("interaction", col("feature1") * col("feature2"))

    # Example: Polynomial features
    for col_name in numerical_cols:
        df = df.withColumn(f"{col_name}_squared", pow(col(col_name), 2))
        df = df.withColumn(f"{col_name}_sqrt", sqrt(col(col_name)))

    print("Derived features added.")
    return df


def select_features(df: DataFrame, selected_columns: list) -> DataFrame:
    """
    Select the subset of features to keep for model training.
    """
    print("Selecting features...")
    # Use a VectorAssembler to create a feature vector for selected columns
    assembler = VectorAssembler(
        inputCols=selected_columns, outputCol="engineered_features"
    )
    df = assembler.transform(df)
    print(f"Selected features: {selected_columns}")
    return df


def save_engineered_data(df: DataFrame, output_path: str):
    """
    Save the dataset with engineered features.
    """
    print(f"Saving engineered data to {output_path}...")
    df.write.mode("overwrite").parquet(output_path)
    print("Engineered data saved.")


if __name__ == "__main__":
    # Paths
    INPUT_PATH = "data/processed/train"  # Path to preprocessed training data
    OUTPUT_PATH = "data/processed/engineered"

    # Load preprocessed data
    data = load_data(INPUT_PATH)

    # Add derived features
    data = add_derived_features(data)

    # Select features for training
    # Assuming we use all numerical columns and the new engineered features
    selected_features = [
        col
        for col in data.columns
        if "log_" in col or "_squared" in col or "_sqrt" in col
    ]
    data = select_features(data, selected_features)

    # Save engineered data
    save_engineered_data(data, OUTPUT_PATH)
