"""
Machine Learning Model Training for AI Triage System

This module trains a RandomForestClassifier to predict patient priority levels
based on vital signs and symptoms. The trained model is saved using joblib.
"""

import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder


def load_dataset(filepath: str) -> pd.DataFrame:
    """
    Load the triage dataset from CSV file.
    
    Args:
        filepath: Path to the CSV file
    
    Returns:
        DataFrame containing the dataset
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at {filepath}. Please run generate_dataset.py first.")
    
    df = pd.read_csv(filepath)
    print(f"Dataset loaded: {len(df)} samples")
    return df


def prepare_data(df: pd.DataFrame) -> tuple:
    """
    Prepare features and target for model training.
    
    Args:
        df: DataFrame containing the dataset
    
    Returns:
        Tuple of (X_train, X_test, y_train, y_test, feature_names, label_encoder)
    """
    # Define feature columns
    feature_columns = ['age', 'heart_rate', 'systolic_bp', 'oxygen', 
                       'temperature', 'respiratory_rate', 'symptom']
    
    X = df[feature_columns]
    y = df['priority']
    
    # Encode target labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Split into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    
    return X_train, X_test, y_train, y_test, feature_columns, label_encoder


def train_model(X_train: pd.DataFrame, y_train: np.ndarray) -> RandomForestClassifier:
    """
    Train a RandomForestClassifier on the training data.
    
    Args:
        X_train: Training features
        y_train: Training labels (encoded)
    
    Returns:
        Trained RandomForestClassifier model
    """
    # Initialize RandomForest with optimized parameters
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced'
    )
    
    print("\nTraining RandomForestClassifier...")
    model.fit(X_train, y_train)
    print("Training complete!")
    
    return model


def evaluate_model(model: RandomForestClassifier, X_test: pd.DataFrame, 
                   y_test: np.ndarray, label_encoder: LabelEncoder) -> dict:
    """
    Evaluate the trained model on test data.
    
    Args:
        model: Trained RandomForestClassifier
        X_test: Test features
        y_test: Test labels (encoded)
        label_encoder: LabelEncoder for decoding predictions
    
    Returns:
        Dictionary containing evaluation metrics
    """
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)
    
    # Get class names
    class_names = label_encoder.classes_
    
    print("\n" + "=" * 60)
    print("MODEL EVALUATION RESULTS")
    print("=" * 60)
    print(f"\nAccuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=class_names))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    cm_df = pd.DataFrame(cm, index=class_names, columns=[f'Pred_{c}' for c in class_names])
    print(cm_df)
    
    # Feature importance
    print("\nFeature Importance:")
    feature_importance = model.feature_importances_
    for i, importance in enumerate(feature_importance):
        print(f"  {X_test.columns[i]}: {importance:.4f}")
    
    return {
        'accuracy': accuracy,
        'predictions': y_pred,
        'confusion_matrix': cm
    }


def save_model(model: RandomForestClassifier, label_encoder: LabelEncoder, 
               feature_names: list, filepath: str) -> None:
    """
    Save the trained model and associated objects using joblib.
    
    Args:
        model: Trained RandomForestClassifier
        label_encoder: LabelEncoder for priority labels
        feature_names: List of feature column names
        filepath: Path to save the model
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Save model, encoder, and feature names together
    model_data = {
        'model': model,
        'label_encoder': label_encoder,
        'feature_names': feature_names
    }
    
    joblib.dump(model_data, filepath)
    print(f"\nModel saved to: {filepath}")


def main():
    """Main function to train and save the triage model."""
    print("=" * 60)
    print("AI TRIAGE SYSTEM - Model Training")
    print("=" * 60)
    
    # Load dataset
    dataset_path = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'triage_dataset.csv')
    df = load_dataset(dataset_path)
    
    # Prepare data
    X_train, X_test, y_train, y_test, feature_names, label_encoder = prepare_data(df)
    
    # Train model
    model = train_model(X_train, y_train)
    
    # Evaluate model
    metrics = evaluate_model(model, X_test, y_test, label_encoder)
    
    # Save model
    model_path = os.path.join(os.path.dirname(__file__), 'triage_model.pkl')
    save_model(model, label_encoder, feature_names, model_path)
    
    print("\n" + "=" * 60)
    print("Training pipeline completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
