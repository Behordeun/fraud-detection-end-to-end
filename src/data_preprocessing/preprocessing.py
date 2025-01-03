import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib  # For saving scalers and encoders

def load_data(file_path):
    """
    Load the dataset from a CSV file.
    """
    print(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path)
    print(f"Data loaded with shape: {df.shape}")
    return df


def handle_missing_values(df):
    """
    Handle missing values in the dataset.
    Replace missing numerical values with the median
    and categorical values with the mode.
    """
    print("Handling missing values...")
    for column in df.columns:
        if df[column].isnull().sum() > 0:
            if df[column].dtype in ["float64", "int64"]:
                df[column].fillna(df[column].median(), inplace=True)
            else:
                df[column].fillna(df[column].mode()[0], inplace=True)
    print("Missing values handled.")
    return df


def scale_features(df, feature_columns, scaler_path="scaler.pkl"):
    """
    Scale numerical features using StandardScaler.
    Save the scaler for later use.
    """
    print("Scaling features...")
    scaler = StandardScaler()
    df[feature_columns] = scaler.fit_transform(df[feature_columns])
    joblib.dump(scaler, scaler_path)
    print(f"Scaler saved to {scaler_path}.")
    return df


def encode_labels(df, target_column, encoder_path="label_encoder.pkl"):
    """
    Encode target labels using LabelEncoder.
    Save the encoder for later use.
    """
    print("Encoding labels...")
    encoder = LabelEncoder()
    df[target_column] = encoder.fit_transform(df[target_column])
    joblib.dump(encoder, encoder_path)
    print(f"Label encoder saved to {encoder_path}.")
    return df


def split_data(df, target_column, test_size=0.2, random_state=42):
    """
    Split the dataset into training and testing sets.
    """
    print("Splitting data into training and testing sets...")
    X = df.drop(columns=[target_column])
    y = df[target_column]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    print("Data split complete.")
    return X_train, X_test, y_train, y_test


def save_preprocessed_data(X_train, X_test, y_train, y_test, output_dir="data/processed"):
    """
    Save the preprocessed data to CSV files.
    """
    print(f"Saving preprocessed data to {output_dir}...")
    X_train.to_csv(f"{output_dir}/X_train.csv", index=False)
    X_test.to_csv(f"{output_dir}/X_test.csv", index=False)
    y_train.to_csv(f"{output_dir}/y_train.csv", index=False)
    y_test.to_csv(f"{output_dir}/y_test.csv", index=False)
    print("Preprocessed data saved.")


if __name__ == "__main__":
    # Example workflow
    DATA_PATH = "../data/credit_card_fraud.csv"
    TARGET_COLUMN = "Class"  # Update this with the correct target column name
    PROCESSED_DIR = "../data/processed"

    # Load data
    data = load_data(DATA_PATH)

    # Handle missing values
    data = handle_missing_values(data)

    # Scale numerical features
    numerical_features = data.select_dtypes(include=["float64", "int64"]).columns.drop(TARGET_COLUMN)
    data = scale_features(data, numerical_features)

    # Encode target labels
    data = encode_labels(data, TARGET_COLUMN)

    # Split data into train and test sets
    X_train, X_test, y_train, y_test = split_data(data, TARGET_COLUMN)

    # Save preprocessed data
    save_preprocessed_data(X_train, X_test, y_train, y_test, output_dir=PROCESSED_DIR)