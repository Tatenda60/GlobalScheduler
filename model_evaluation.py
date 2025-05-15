"""
Model Evaluation Script
Loads a trained model and test data, then evaluates and prints metrics.
This runs automatically when the Flask app starts.
"""
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_model(model_path):
    """Load the trained model from pickle file"""
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        logger.info(f"Model loaded successfully from {model_path}")
        return model
    except FileNotFoundError:
        logger.error(f"Model file not found at {model_path}")
        return None
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return None

def load_test_data(data_path):
    """Load test data from CSV file"""
    try:
        test_data = pd.read_csv(data_path)
        logger.info(f"Test data loaded successfully from {data_path} with {len(test_data)} samples")
        return test_data
    except FileNotFoundError:
        logger.error(f"Test data file not found at {data_path}")
        return None
    except Exception as e:
        logger.error(f"Error loading test data: {str(e)}")
        return None

def evaluate_model(model, test_data):
    """Evaluate model performance and print metrics"""
    if model is None or test_data is None:
        logger.error("Cannot evaluate: model or test data is missing")
        return
    
    try:
        # Separate features and target
        # Modify these column names according to your dataset
        X_test = test_data.drop('target', axis=1)
        y_test = test_data['target']
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        # If binary classification
        if len(np.unique(y_test)) == 2:
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            logger.info("\n" + "=" * 50)
            logger.info("MODEL EVALUATION METRICS")
            logger.info("=" * 50)
            logger.info(f"Accuracy:  {accuracy:.4f}")
            logger.info(f"Precision: {precision:.4f}")
            logger.info(f"Recall:    {recall:.4f}")
            logger.info(f"F1 Score:  {f1:.4f}")
            logger.info("=" * 50)
        
        # For multi-class classification
        else:
            logger.info("\n" + "=" * 50)
            logger.info("MODEL EVALUATION METRICS (MULTI-CLASS)")
            logger.info("=" * 50)
            logger.info(f"Accuracy:  {accuracy:.4f}")
            logger.info(f"\nClassification Report:\n{classification_report(y_test, y_pred)}")
            logger.info("=" * 50)
            
        return {
            'accuracy': accuracy,
            'predictions': y_pred,
            'true_values': y_test
        }
    
    except Exception as e:
        logger.error(f"Error during model evaluation: {str(e)}")
        return None

def run_evaluation(model_path='your_model.pkl', test_data_path='test_data.csv'):
    """Run the complete evaluation process"""
    logger.info("Starting model evaluation...")
    
    model = load_model(model_path)
    test_data = load_test_data(test_data_path)
    results = evaluate_model(model, test_data)
    
    logger.info("Model evaluation complete")
    return results

if __name__ == "__main__":
    run_evaluation()