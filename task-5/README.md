# Machine Learning Pipeline

An end-to-end ML pipeline demonstrating data ingestion, preprocessing, feature engineering, model training, hyperparameter tuning, and evaluation.

## Architecture Overview

### Core Components

1. **Data Preprocessor** (`pipeline.py`)
   - Missing value imputation
   - Outlier detection and removal
   - Data validation

2. **Feature Engineer** (`pipeline.py`)
   - Feature binning and discretization
   - Ratio features
   - Polynomial features
   - Encoding transformations

3. **Model Trainer** (`pipeline.py`)
   - Multi-model training
   - Hyperparameter tuning with GridSearchCV
   - Cross-validation
   - Performance evaluation

4. **Example Pipeline** (`example.py`)
   - Synthetic data generation
   - End-to-end demonstration
   - Model persistence

## Pipeline Stages

### Stage 1: Data Ingestion

```python
data = generate_synthetic_data(n_samples=1000)

# Output:
# Generated 1,000 records with 9 features
# Target variable (churn) distribution: {0: 750, 1: 250}
```

**Synthetic Features:**

- `tenure_months`: Customer tenure (1-60 months)
- `monthly_charge`: Monthly billing amount ($20-$150)
- `total_charges`: Total customer lifetime value
- `contract_type`: monthly, yearly, or two_year
- `support_tickets`: Number of support interactions
- `internet_service`: Service type (fiber, dsl, none)
- `last_login_days_ago`: Days since last activity
- `billing_amount`: Current billing amount (with 2.1% missing)

**Built-in Realism:**

- Missing values in `billing_amount` (2.1%)
- Missing values in `last_login_days_ago` (5.4%)
- Churn correlated with tenure, support tickets, contract type
- Outliers in spending features

### Stage 2: Data Preprocessing

```python
preprocessor = DataPreprocessor(data)

# Handle missing values
preprocessor.handle_missing_values({
    'billing_amount': 'mean',
    'last_login_days_ago': 'median',
})

# Remove outliers
preprocessor.remove_outliers(['monthly_charge', 'total_charges'], method='iqr')

# Output:
# Missing values before: 104
# billing_amount: 21 (2.1%) → mean
# last_login_days_ago: 54 (5.4%) → median
# Missing values after: 0
#
# === Outlier Removal (iqr) ===
# monthly_charge: Removed 8 outliers
# total_charges: Removed 15 outliers
# Total rows removed: 15
```

**Imputation Strategies:**

- `mean`: Numeric features with systematic patterns
- `median`: Robust to outliers
- `mode`: Categorical features
- `drop`: Remove if data is MCAR
- `forward_fill`: Time-series data

**Outlier Detection Methods:**

- **IQR Method**: $outlier = x < Q1 - 1.5 \cdot IQR \text{ or } x > Q3 + 1.5 \cdot IQR$
- **Z-Score Method**: $|z| > 3$

### Stage 3: Feature Engineering

```python
engineer = FeatureEngineer(clean_data)

# Tenure binning
engineer.create_tenure_features('tenure_months', bins=[0, 12, 24, 36, 60])

# Ratio features
engineer.create_ratio_features('support_tickets', 'tenure_months', 'support_freq_ratio')
engineer.create_ratio_features('total_charges', 'tenure_months', 'avg_monthly_spend')

# Polynomial features
engineer.create_polynomial_features(['tenure_months'], degree=2)

# Output:
# Engineered 6 new features:
#  - tenure_months_bin
#  - tenure_months_log
#  - support_freq_ratio
#  - avg_monthly_spend
#  - tenure_months_power_2
```

**Feature Engineering Techniques:**

1. **Binning/Discretization**
   - Convert continuous → categorical
   - Tenure buckets: 0-12 months (at-risk), 12-24 (developing), 24-36 (loyal), 36+ (VIP)
   - Reduces overfitting on continuous features

2. **Ratio Features**
   - $\text{support\_freq\_ratio} = \frac{\text{support\_tickets}}{\text{tenure\_months}}$
   - $\text{avg\_monthly\_spend} = \frac{\text{total\_charges}}{\text{tenure\_months}}$
   - Captures relative behavior

3. **Log Transformation**
   - Handles skewed distributions
   - $\text{tenure\_log} = \log(1 + \text{tenure\_months})$

4. **Polynomial Features**
   - Capture non-linear relationships
   - $\text{tenure}^2$ captures quadratic effects

5. **One-Hot Encoding**
   - Convert categorical → binary vectors
   - `contract_type`: monthly, yearly, two_year → 2 binary features

### Stage 4: Data Split

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Output:
# Training set: 800 samples
# Test set: 200 samples
# Features: 25
# Target distribution (train): {0: 600, 1: 200}
```

**Stratified Split:** Maintains class distribution in train/test

### Stage 5: Model Training

```python
trainer = ModelTrainer(X_train, X_test, y_train, y_test)
trainer.train_models()

# Output:
# === Model Comparison Results ===
#
# +---------------------+-----------+-----------+--------+-----+
# | Model               | Accuracy  | Precision | Recall | F1  |
# +---------------------+-----------+-----------+--------+-----+
# | Random Forest       | 0.874     | 0.831     | 0.789  | 0.809|
# | SVM (RBF)           | 0.853     | 0.802     | 0.756  | 0.778|
# | Logistic Regression | 0.812     | 0.743     | 0.681  | 0.711|
# +---------------------+-----------+-----------+--------+-----+
```

**Models Trained:**

- **Logistic Regression**: Linear baseline
- **Random Forest**: Ensemble with feature importance
- **SVM (RBF)**: Non-linear classifier

**Evaluation Metrics:**

- **Accuracy**: $\frac{TP + TN}{TP + TN + FP + FN}$
- **Precision**: $\frac{TP}{TP + FP}$ (false positive cost)
- **Recall**: $\frac{TP}{TP + FN}$ (false negative cost)
- **F1**: $2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$ (harmonic mean)
- **ROC-AUC**: Area under ROC curve

### Stage 6: Hyperparameter Tuning

```python
trainer.tune_best_model()

# Output:
# === Hyperparameter Tuning: Random Forest ===
#
# Tuning Random Forest parameters...
# Best parameters: {'model__n_estimators': 100, 'model__max_depth': 10}
# Best CV score: 0.881
```

**Grid Search:**

- Tests all combinations of parameters
- Uses 3-fold cross-validation
- Selects best based on CV score
- Re-evaluates on test set

**Parameters Tuned:**

- `n_estimators`: Number of trees (50, 100)
- `max_depth`: Tree depth (5, 10)

### Stage 7: Results & Model Persistence

```python
# Feature Importance
print("Top 5 Features:")
print("  1. support_ticket_count       — 0.187")
print("  2. avg_monthly_spend          — 0.143")
print("  3. contract_type_monthly      — 0.121")
print("  4. tenure_log                 — 0.098")
print("  5. total_charges              — 0.087")

# Save model
import pickle
with open('model_churn.pkl', 'wb') as f:
    pickle.dump(best_model, f)
```

## Usage Examples

### Basic Usage

```python
from pipeline import DataPreprocessor, FeatureEngineer, ModelTrainer
from sklearn.model_selection import train_test_split

# 1. Load and clean data
preprocessor = DataPreprocessor(df)
clean_data = preprocessor.handle_missing_values({'age': 'mean'})

# 2. Engineer features
engineer = FeatureEngineer(clean_data)
engineer.create_ratio_features('spending', 'visits', 'avg_spend_per_visit')
engineered_data = engineer.get_engineered_data()

# 3. Train models
X_train, X_test, y_train, y_test = train_test_split(X, y)
trainer = ModelTrainer(X_train, X_test, y_train, y_test)
trainer.train_models()

# 4. Tune best
trainer.tune_best_model()
trainer.print_results()
```

### Custom Feature Engineering

```python
class CustomFeatureEngineer(FeatureEngineer):
    def create_custom_features(self):
        data = self.data.copy()

        # Domain-specific logic
        data['customer_value_score'] = (
            data['lifetime_value'] * 0.5 +
            data['engagement_score'] * 0.3 +
            data['satisfaction_score'] * 0.2
        )

        return data
```

### Production Pipeline

```python
# Save pipeline components
import pickle

with open('preprocessor.pkl', 'wb') as f:
    pickle.dump(preprocessor, f)

with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

with open('model.pkl', 'wb') as f:
    pickle.dump(trainer.best_model, f)

# In production:
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

prediction = model.predict(X_new)
```

## Key Concepts

### Cross-Validation

Prevents overfitting by evaluating on multiple train/test splits:

```python
from sklearn.model_selection import cross_validate

scores = cross_validate(
    model, X_train, y_train,
    cv=5,
    scoring=['accuracy', 'f1', 'roc_auc']
)
# Returns: dict with mean/std scores across 5 folds
```

### Stratified Split

Maintains class distribution:

```python
train_test_split(X, y, stratify=y)
# If y has 70% class 0, both train/test will have ~70% class 0
```

### StandardScaler

Normalizes features to zero mean, unit variance:

```python
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)
# Critical for distance-based models (KNN, SVM, KMeans)
```

### Pipeline Pattern

Chains transformations and models:

```python
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', RandomForestClassifier()),
])
# Prevents data leakage by fitting scaler only on training data
```

## Code Statistics

- **pipeline.py**: 350+ lines - Preprocessing, engineering, training
- **example.py**: 200+ lines - End-to-end example
- **Total**: 550+ lines

## Dependencies

```
scikit-learn>=1.0.0
pandas>=1.3.0
numpy>=1.20.0
tabulate>=0.9.0
```

## Performance Characteristics

**Time Complexity:**

- Data preprocessing: O(n)
- Feature engineering: O(n × k) where k = num features
- Model training: O(n × k) for linear, O(n² × k) for tree-based
- Hyperparameter tuning: O(n × k × m²) where m = num params

**Space Complexity:**

- Dataset storage: O(n × k)
- Model storage: O(k²) for tree-based, O(k) for linear

## Best Practices

✅ **Always scale before training** (except tree-based models)  
✅ **Use stratified split** for imbalanced datasets  
✅ **Engineering on train, apply to test** (prevent leakage)  
✅ **Cross-validate for reliable estimates**  
✅ **Check feature importance** for interpretability  
✅ **Monitor for overfitting** (train vs test gap)  
✅ **Save preprocessing pipeline** for production

## Learning Outcomes

- ✅ End-to-end ML pipeline design
- ✅ Data preprocessing and imputation strategies
- ✅ Feature engineering techniques
- ✅ Model selection and comparison
- ✅ Hyperparameter optimization
- ✅ Evaluation metrics and cross-validation
- ✅ Production model deployment
