"""
ML Pipeline for end-to-end model training and evaluation.
Includes data preprocessing, feature engineering, model comparison, and tuning.
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any, Optional
from sklearn.model_selection import train_test_split, cross_validate, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder, KBinsDiscretizer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
import pickle
from datetime import datetime


class DataPreprocessor:
    """Handles data loading, cleaning, and basic preprocessing."""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.original_shape = data.shape
        self.missing_value_stats = {}
    
    def handle_missing_values(self, strategy: Dict[str, str]) -> pd.DataFrame:
        """
        Handle missing values using specified strategy.
        
        Args:
            strategy: Dict mapping column -> strategy ('mean', 'median', 'drop', 'ffill')
        
        Returns:
            DataFrame with missing values handled
        """
        data = self.data.copy()
        
        print("\n=== Missing Value Handling ===")
        print(f"Missing values before: {data.isnull().sum().sum()}")
        
        for col, method in strategy.items():
            if col in data.columns and data[col].isnull().sum() > 0:
                missing_count = data[col].isnull().sum()
                missing_pct = (missing_count / len(data)) * 100
                
                if method == 'mean':
                    data[col] = data[col].fillna(data[col].mean())
                elif method == 'median':
                    data[col] = data[col].fillna(data[col].median())
                elif method == 'mode':
                    data[col] = data[col].fillna(data[col].mode()[0])
                elif method == 'drop':
                    data = data.dropna(subset=[col])
                elif method == 'ffill':
                    data[col] = data[col].fillna(method='ffill')
                
                print(f"  {col}: {missing_count} ({missing_pct:.1f}%) → {method}")
                self.missing_value_stats[col] = missing_pct
        
        print(f"Missing values after: {data.isnull().sum().sum()}")
        
        self.data = data
        return data
    
    def remove_outliers(self, columns: List[str], method: str = 'iqr') -> pd.DataFrame:
        """
        Remove outliers from specified columns.
        
        Args:
            columns: Columns to check for outliers
            method: 'iqr' for IQR method, 'zscore' for Z-score method
        
        Returns:
            DataFrame with outliers removed
        """
        data = self.data.copy()
        original_rows = len(data)
        
        print(f"\n=== Outlier Removal ({method}) ===")
        
        for col in columns:
            if col not in data.columns or data[col].dtype in ['object', 'category']:
                continue
            
            if method == 'iqr':
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_count = ((data[col] < lower_bound) | (data[col] > upper_bound)).sum()
                if outlier_count > 0:
                    print(f"  {col}: Removed {outlier_count} outliers")
                    data = data[(data[col] >= lower_bound) & (data[col] <= upper_bound)]
            
            elif method == 'zscore':
                z_scores = np.abs((data[col] - data[col].mean()) / data[col].std())
                outlier_count = (z_scores > 3).sum()
                if outlier_count > 0:
                    print(f"  {col}: Removed {outlier_count} outliers")
                    data = data[z_scores <= 3]
        
        rows_removed = original_rows - len(data)
        print(f"Total rows removed: {rows_removed}")
        
        self.data = data
        return data
    
    def get_processed_data(self) -> pd.DataFrame:
        """Get cleaned and preprocessed data."""
        return self.data


class FeatureEngineer:
    """Handles feature creation and transformation."""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.engineered_features = []
    
    def create_tenure_features(self, tenure_col: str, bins: List[int] = None) -> pd.DataFrame:
        """Create tenure-based features."""
        data = self.data.copy()
        
        if tenure_col not in data.columns:
            return data
        
        # Binning
        if bins:
            data[f'{tenure_col}_bin'] = pd.cut(
                data[tenure_col],
                bins=bins,
                labels=[f'tenure_{i}' for i in range(len(bins)-1)]
            )
            self.engineered_features.append(f'{tenure_col}_bin')
        
        # Log transformation
        data[f'{tenure_col}_log'] = np.log1p(data[tenure_col])
        self.engineered_features.append(f'{tenure_col}_log')
        
        return data
    
    def create_ratio_features(self, numerator: str, denominator: str, name: str) -> pd.DataFrame:
        """Create ratio features."""
        data = self.data.copy()
        
        if numerator in data.columns and denominator in data.columns:
            # Avoid division by zero
            data[name] = data[numerator] / (data[denominator] + 1e-8)
            data[name] = data[name].replace([np.inf, -np.inf], 0)
            self.engineered_features.append(name)
        
        return data
    
    def create_polynomial_features(self, cols: List[str], degree: int = 2) -> pd.DataFrame:
        """Create polynomial features."""
        data = self.data.copy()
        
        for col in cols:
            if col not in data.columns or data[col].dtype == 'object':
                continue
            
            for d in range(2, degree + 1):
                name = f'{col}_power_{d}'
                data[name] = data[col] ** d
                self.engineered_features.append(name)
        
        return data
    
    def get_engineered_data(self) -> pd.DataFrame:
        """Get data with engineered features."""
        return self.data


class ModelTrainer:
    """Trains and evaluates multiple models."""
    
    def __init__(self, X_train, X_test, y_train, y_test):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.models = {}
        self.results = {}
        self.best_model = None
    
    def create_preprocessing_pipeline(
        self,
        numerical_features: List[str],
        categorical_features: List[str]
    ) -> ColumnTransformer:
        """Create preprocessing pipeline."""
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numerical_features),
                ('cat', OneHotEncoder(sparse=False, handle_unknown='ignore'), categorical_features),
            ],
            remainder='passthrough'
        )
        return preprocessor
    
    def train_models(self) -> Dict[str, Any]:
        """Train multiple models and compare."""
        print("\n=== Training Models ===\n")
        
        # Simple models without extensive tuning for demo
        models_config = {
            'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
            'SVM (RBF)': SVC(kernel='rbf', random_state=42, probability=True),
        }
        
        for name, model in models_config.items():
            print(f"Training {name}...")
            
            # Standard scaling for all
            pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('model', model),
            ])
            
            # Train
            pipeline.fit(self.X_train, self.y_train)
            
            # Predict
            y_pred = pipeline.predict(self.X_test)
            y_pred_proba = pipeline.predict_proba(self.X_test)[:, 1] if hasattr(model, 'predict_proba') else None
            
            # Evaluate
            results = {
                'model': pipeline,
                'accuracy': accuracy_score(self.y_test, y_pred),
                'precision': precision_score(self.y_test, y_pred, zero_division=0),
                'recall': recall_score(self.y_test, y_pred, zero_division=0),
                'f1': f1_score(self.y_test, y_pred, zero_division=0),
                'roc_auc': roc_auc_score(self.y_test, y_pred_proba) if y_pred_proba is not None else None,
                'y_pred': y_pred,
            }
            
            self.models[name] = pipeline
            self.results[name] = results
            
            print(f"  ✓ Accuracy: {results['accuracy']:.3f}, F1: {results['f1']:.3f}")
        
        return self.results
    
    def tune_best_model(self) -> None:
        """Tune hyperparameters for best model."""
        # Find best model by F1 score
        best_name = max(self.results.keys(), key=lambda k: self.results[k]['f1'])
        best_model = self.models[best_name]
        
        print(f"\n=== Hyperparameter Tuning: {best_name} ===\n")
        
        # Simple tuning for demo
        if 'Random Forest' in best_name:
            print("Tuning Random Forest parameters...")
            param_grid = {
                'model__n_estimators': [50, 100],
                'model__max_depth': [5, 10],
            }
            
            grid_search = GridSearchCV(best_model, param_grid, cv=3, n_jobs=-1)
            grid_search.fit(self.X_train, self.y_train)
            
            self.best_model = grid_search.best_estimator_
            print(f"Best parameters: {grid_search.best_params_}")
            print(f"Best CV score: {grid_search.best_score_:.3f}")
            
            # Re-evaluate
            y_pred = self.best_model.predict(self.X_test)
            self.results[f'{best_name} (tuned)'] = {
                'accuracy': accuracy_score(self.y_test, y_pred),
                'precision': precision_score(self.y_test, y_pred, zero_division=0),
                'recall': recall_score(self.y_test, y_pred, zero_division=0),
                'f1': f1_score(self.y_test, y_pred, zero_division=0),
                'model': self.best_model,
            }
        else:
            self.best_model = best_model
    
    def print_results(self) -> None:
        """Print model comparison results."""
        print("\n=== Model Comparison Results ===\n")
        
        rows = []
        for name, result in sorted(self.results.items(), key=lambda x: x[1]['f1'], reverse=True):
            rows.append([
                name,
                f"{result['accuracy']:.3f}",
                f"{result['precision']:.3f}",
                f"{result['recall']:.3f}",
                f"{result['f1']:.3f}",
            ])
        
        from tabulate import tabulate
        headers = ["Model", "Accuracy", "Precision", "Recall", "F1"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    
    def get_best_model_name(self) -> str:
        """Get name of best model by F1."""
        return max(self.results.keys(), key=lambda k: self.results[k]['f1'])
    
    def get_feature_importance(self, model_name: str) -> Dict[str, float]:
        """Get feature importance from model."""
        if model_name not in self.models:
            return {}
        
        model = self.models[model_name]
        
        # Extract the actual model from pipeline
        if hasattr(model, 'named_steps'):
            actual_model = model.named_steps.get('model')
        else:
            actual_model = model
        
        if hasattr(actual_model, 'feature_importances_'):
            importances = actual_model.feature_importances_
            # This is simplified - in real scenarios you'd map back to feature names
            return {f'Feature_{i}': imp for i, imp in enumerate(importances[:10])}
        
        return {}
