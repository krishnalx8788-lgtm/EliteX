"""
Synthetic Dataset Generator for AI Triage System

This module generates a synthetic dataset of patient vital signs and symptoms
for training the triage classification model. The dataset includes medically
reasonable ranges and priority labels based on clinical rules.
"""

import pandas as pd
import numpy as np
import os


def generate_triage_dataset(n_samples: int = 2000, random_state: int = 42) -> pd.DataFrame:
    """
    Generate a synthetic triage dataset with patient vital signs and priority labels.
    
    Args:
        n_samples: Number of patient records to generate (default: 2000)
        random_state: Random seed for reproducibility (default: 42)
    
    Returns:
        DataFrame with columns: age, heart_rate, systolic_bp, oxygen, temperature,
                              respiratory_rate, symptom, priority
    """
    np.random.seed(random_state)
    
    # Define medically reasonable ranges
    data = {
        'age': np.random.randint(18, 91, n_samples),
        'heart_rate': np.random.randint(60, 151, n_samples),
        'systolic_bp': np.random.randint(90, 181, n_samples),
        'oxygen': np.random.randint(80, 101, n_samples),
        'temperature': np.round(np.random.uniform(36.0, 40.0, n_samples), 1),
        'respiratory_rate': np.random.randint(12, 31, n_samples),
        'symptom': np.random.randint(1, 8, n_samples)  # 1-7 symptom categories
    }
    
    df = pd.DataFrame(data)
    
    # Assign priority labels based on clinical rules
    df['priority'] = df.apply(assign_priority, axis=1)
    
    return df


def assign_priority(row) -> str:
    """
    Assign priority level based on clinical vital sign thresholds.
    
    Priority Rules:
    - Critical: oxygen < 88 OR heart_rate > 130 OR systolic_bp > 170
    - High: oxygen between 88-92 OR heart_rate 110-130
    - Medium: temperature > 38 OR respiratory_rate > 22
    - Low: otherwise
    
    Args:
        row: DataFrame row containing patient vital signs
    
    Returns:
        Priority level as string: 'Critical', 'High', 'Medium', or 'Low'
    """
    # Critical conditions - immediate attention required
    if (row['oxygen'] < 88 or 
        row['heart_rate'] > 130 or 
        row['systolic_bp'] > 170):
        return 'Critical'
    
    # High priority conditions - very urgent
    elif (88 <= row['oxygen'] <= 92 or 
          110 <= row['heart_rate'] <= 130):
        return 'High'
    
    # Medium priority conditions - needs treatment soon
    elif (row['temperature'] > 38 or 
          row['respiratory_rate'] > 22):
        return 'Medium'
    
    # Low priority - non-urgent
    else:
        return 'Low'


def save_dataset(df: pd.DataFrame, filepath: str) -> None:
    """
    Save the dataset to a CSV file.
    
    Args:
        df: DataFrame to save
        filepath: Path to save the CSV file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    df.to_csv(filepath, index=False)
    print(f"Dataset saved to: {filepath}")
    print(f"Total samples: {len(df)}")
    print(f"Priority distribution:")
    print(df['priority'].value_counts())


def main():
    """Main function to generate and save the triage dataset."""
    print("=" * 60)
    print("AI TRIAGE SYSTEM - Synthetic Dataset Generator")
    print("=" * 60)
    
    # Generate dataset with 2000 samples
    dataset = generate_triage_dataset(n_samples=2000, random_state=42)
    
    # Save to CSV
    output_path = os.path.join(os.path.dirname(__file__), 'triage_dataset.csv')
    save_dataset(dataset, output_path)
    
    print("\nDataset generation complete!")
    print(f"File location: {output_path}")
    print("\nSample data:")
    print(dataset.head(10))


if __name__ == "__main__":
    main()
