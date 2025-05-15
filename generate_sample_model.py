"""
Generate a sample model and test data for demonstration.
Run this script once to create sample files for the model evaluation.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pickle
import os

# Set random seed for reproducibility
np.random.seed(42)

def generate_credit_data(n_samples=1000):
    """Generate synthetic credit risk data"""
    data = {
        'credit_score': np.random.randint(300, 850, n_samples),
        'income': np.random.randint(20000, 200000, n_samples),
        'debt': np.random.randint(0, 100000, n_samples),
        'employment_length': np.random.randint(0, 30, n_samples),
        'loan_amount': np.random.randint(1000, 50000, n_samples),
    }
    
    # Calculate debt-to-income ratio
    data['dti_ratio'] = data['debt'] / data['income']
    
    # Create target variable (default probability) based on features
    # Lower credit score, higher dti_ratio, and higher loan amounts increase default probability
    default_prob = ((850 - data['credit_score']) / 550) * 0.4 + \
                   (data['dti_ratio'] * 0.4) + \
                   (data['loan_amount'] / 50000 * 0.2)
    
    # Add some randomness
    default_prob += np.random.normal(0, 0.1, n_samples)
    default_prob = np.clip(default_prob, 0, 1)
    
    # Convert to binary target (1 = default, 0 = no default)
    data['target'] = (default_prob > 0.5).astype(int)
    
    return pd.DataFrame(data)

def main():
    print("Generating sample credit risk data and model...")
    
    # Generate data
    credit_data = generate_credit_data(1000)
    
    # Split data
    X = credit_data.drop('target', axis=1)
    y = credit_data['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Save model
    with open('your_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    # Save test data (with target for evaluation)
    test_data = pd.DataFrame(X_test_scaled, columns=X_test.columns)
    test_data['target'] = y_test.values
    test_data.to_csv('test_data.csv', index=False)
    
    # Also save scaler for future use
    with open('scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    
    print(f"Files created successfully:")
    print(f"  - Model: your_model.pkl ({os.path.getsize('your_model.pkl') / 1024:.1f} KB)")
    print(f"  - Test data: test_data.csv ({os.path.getsize('test_data.csv') / 1024:.1f} KB)")
    print(f"  - Scaler: scaler.pkl ({os.path.getsize('scaler.pkl') / 1024:.1f} KB)")
    
    # Quick accuracy check
    y_pred = model.predict(X_test_scaled)
    accuracy = (y_pred == y_test).mean()
    print(f"Model accuracy on test data: {accuracy:.4f}")

if __name__ == "__main__":
    main()