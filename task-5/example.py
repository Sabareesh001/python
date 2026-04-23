"""
End-to-end ML Pipeline example.
Demonstrates data preprocessing, feature engineering, model training, and evaluation.
"""

import numpy as np
import pandas as pd
from pipeline import DataPreprocessor, FeatureEngineer, ModelTrainer
from sklearn.model_selection import train_test_split
import pickle
from datetime import datetime


def generate_synthetic_data(n_samples: int = 1000) -> pd.DataFrame:
    """Generate synthetic customer churn prediction dataset."""
    np.random.seed(42)
    
    print("=" * 70)
    print("MACHINE LEARNING PIPELINE")
    print("=" * 70)
    print()
    
    print("=== Data Generation ===")
    
    data = {
        'customer_id': range(n_samples),
        'tenure_months': np.random.randint(1, 60, n_samples),
        'monthly_charge': np.random.exponential(50, n_samples) + 20,
        'total_charges': np.random.exponential(1000, n_samples) + 100,
        'contract_type': np.random.choice(['monthly', 'yearly', 'two_year'], n_samples),
        'support_tickets': np.random.poisson(2, n_samples),
        'internet_service': np.random.choice(['fiber', 'dsl', 'none'], n_samples),
        'last_login_days_ago': np.random.randint(0, 365, n_samples),
        'billing_amount': np.random.exponential(100, n_samples) + 50,
    }
    
    df = pd.DataFrame(data)
    
    # Add missing values intentionally
    df.loc[np.random.choice(df.index, size=int(0.021 * len(df)), replace=False), 'billing_amount'] = np.nan
    df.loc[np.random.choice(df.index, size=int(0.054 * len(df)), replace=False), 'last_login_days_ago'] = np.nan
    
    # Create target variable (churn) based on features
    churn_prob = (
        (df['tenure_months'] < 12) * 0.4 +
        (df['support_tickets'] > 5) * 0.3 +
        (df['contract_type'] == 'monthly') * 0.2
    )
    df['churn'] = (np.random.random(n_samples) < np.clip(churn_prob, 0, 1)).astype(int)
    
    print(f"Generated {len(df):,} records with {len(df.columns)} features")
    print(f"Target variable (churn) distribution: {df['churn'].value_counts().to_dict()}")
    
    return df


def main():
    # Generate data
    data = generate_synthetic_data(n_samples=1000)
    
    print("\n=== Data Ingestion ===")
    print(f"Loaded {len(data):,} records ({data.shape[1]} features)")
    print(f"Memory usage: {data.memory_usage(deep=True).sum() / 1024:.1f} KB")
    
    # --- Step 1: Data Preprocessing ---
    print("\n" + "=" * 70)
    print("STEP 1: Data Preprocessing")
    print("=" * 70)
    
    preprocessor = DataPreprocessor(data)
    
    # Handle missing values
    preprocessor.handle_missing_values({
        'billing_amount': 'mean',
        'last_login_days_ago': 'median',
    })
    
    # Remove outliers
    preprocessor.remove_outliers(['monthly_charge', 'total_charges'], method='iqr')
    
    clean_data = preprocessor.get_processed_data()
    
    print(f"\nData shape after preprocessing: {clean_data.shape}")
    
    # --- Step 2: Feature Engineering ---
    print("\n" + "=" * 70)
    print("STEP 2: Feature Engineering")
    print("=" * 70)
    print()
    
    engineer = FeatureEngineer(clean_data)
    
    # Create tenure bins
    engineer.create_tenure_features('tenure_months', bins=[0, 12, 24, 36, 60])
    
    # Create ratio features
    engineer.create_ratio_features('support_tickets', 'tenure_months', 'support_freq_ratio')
    engineer.create_ratio_features('total_charges', 'tenure_months', 'avg_monthly_spend')
    
    # Create polynomial features
    engineer.create_polynomial_features(['tenure_months'], degree=2)
    
    engineered_data = engineer.create_tenure_features('monthly_charge', bins=[20, 50, 75, 100, 150]).copy()
    engineered_data = engineer.get_engineered_data()
    
    print(f"Engineered {len(engineer.engineered_features)} new features:")
    for feat in engineer.engineered_features:
        print(f"  - {feat}")
    
    # One-hot encode categorical features
    print("\nEncoding categorical features...")
    engineered_data = pd.get_dummies(
        engineered_data,
        columns=['contract_type', 'internet_service'],
        drop_first=True
    )
    
    print(f"Final feature count: {engineered_data.shape[1]}")
    
    # --- Step 3: Prepare Data for Modeling ---
    print("\n" + "=" * 70)
    print("STEP 3: Data Preparation for Modeling")
    print("=" * 70)
    print()
    
    # Separate features and target
    X = engineered_data.drop(['customer_id', 'churn'], axis=1)
    y = engineered_data['churn']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    print(f"Features: {X_train.shape[1]}")
    print(f"Target distribution (train): {y_train.value_counts().to_dict()}")
    
    # --- Step 4: Model Training and Comparison ---
    print("\n" + "=" * 70)
    print("STEP 4: Model Training and Comparison")
    print("=" * 70)
    
    trainer = ModelTrainer(X_train, X_test, y_train, y_test)
    trainer.train_models()
    
    # Print results
    trainer.print_results()
    
    # --- Step 5: Hyperparameter Tuning ---
    print("\n" + "=" * 70)
    print("STEP 5: Hyperparameter Tuning")
    print("=" * 70)
    
    trainer.tune_best_model()
    
    # --- Step 6: Best Model Details ---
    print("\n" + "=" * 70)
    print("STEP 6: Best Model Summary")
    print("=" * 70)
    print()
    
    best_name = trainer.get_best_model_name()
    best_result = trainer.results[best_name]
    
    print(f"Best Model: {best_name}")
    print(f"  - Accuracy:  {best_result['accuracy']:.3f}")
    print(f"  - Precision: {best_result['precision']:.3f}")
    print(f"  - Recall:    {best_result['recall']:.3f}")
    print(f"  - F1 Score:  {best_result['f1']:.3f}")
    if best_result['roc_auc']:
        print(f"  - ROC-AUC:   {best_result['roc_auc']:.3f}")
    
    # Feature importance (if available)
    importance = trainer.get_feature_importance(best_name)
    if importance:
        print(f"\nTop Features:")
        for feat, imp in sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {feat}: {imp:.3f}")
    
    # --- Step 7: Model Persistence ---
    print("\n" + "=" * 70)
    print("STEP 7: Model Persistence")
    print("=" * 70)
    print()
    
    model_path = f"model_churn_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(trainer.best_model, f)
    
    print(f"Model saved to: {model_path}")
    
    # --- Summary Statistics ---
    print("\n" + "=" * 70)
    print("PIPELINE SUMMARY")
    print("=" * 70)
    print()
    
    print(f"✓ Data Records: {len(data):,}")
    print(f"✓ Features Engineered: {len(engineer.engineered_features)}")
    print(f"✓ Final Feature Count: {X_train.shape[1]}")
    print(f"✓ Models Trained: {len(trainer.models)}")
    print(f"✓ Best Model: {best_name}")
    print(f"✓ Best F1 Score: {best_result['f1']:.3f}")
    print(f"✓ Model Saved: {model_path}")


if __name__ == "__main__":
    main()
