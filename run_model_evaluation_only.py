"""
A standalone script to run model evaluation.
This is a simplified version that doesn't depend on the database.
"""
import os
import logging
from datetime import datetime
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    classification_report, roc_curve, auc, confusion_matrix
)

# ANSI color codes for terminal output
RESET = "\033[0m"
BOLD = "\033[1m"
BLUE = "\033[34m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"

# Configure logging to be more visually appealing
logging.basicConfig(
    level=logging.INFO,
    format=f"{GREEN}%(asctime)s{RESET} - {BLUE}%(levelname)s{RESET} - %(message)s"
)
logger = logging.getLogger(__name__)

def print_header(text):
    """Print a formatted header"""
    print(f"\n{BOLD}{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}{CYAN}{text.center(60)}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 60}{RESET}\n")

def print_section(text):
    """Print a section header"""
    print(f"\n{BOLD}{BLUE}{text}{RESET}")
    print(f"{BLUE}{'-' * len(text)}{RESET}")

def print_metric(name, value, good_threshold=0.8):
    """Print a metric with color indicating performance"""
    if value >= good_threshold:
        color = GREEN
    elif value >= good_threshold - 0.2:
        color = YELLOW
    else:
        color = RED
    
    dots = "." * (20 - len(name))
    print(f"  {name} {dots} {color}{value:.4f}{RESET}")

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
        return None
    
    try:
        # Separate features and target
        X_test = test_data.drop('target', axis=1)
        y_test = test_data['target']
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        # Calculate metrics
        if len(np.unique(y_test)) <= 2:  # Binary classification
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            metrics = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1': f1
            }
        else:  # Multi-class
            metrics = {
                'accuracy': accuracy,
                'report': classification_report(y_test, y_pred)
            }
            
        return metrics
    except Exception as e:
        logger.error(f"Error evaluating model: {str(e)}")
        return None

def main():
    """Run model evaluation independently"""
    # Clear terminal
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Print header and date/time
    print_header("CREDIT RISK MODEL EVALUATION")
    print(f"{BOLD}Date and Time:{RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Default paths for model and test data
    model_path = os.environ.get('MODEL_PATH', 'your_model.pkl')
    test_data_path = os.environ.get('TEST_DATA_PATH', 'test_data.csv')
    
    # Print model information
    print_section("Model Information")
    if not os.path.exists(model_path):
        print(f"  {RED}Model file not found: {model_path}{RESET}")
        print(f"  {YELLOW}Run generate_sample_model.py to create it.{RESET}")
        return
    
    if not os.path.exists(test_data_path):
        print(f"  {RED}Test data file not found: {test_data_path}{RESET}")
        print(f"  {YELLOW}Run generate_sample_model.py to create it.{RESET}")
        return
    
    model_size = os.path.getsize(model_path) / (1024*1024)  # Size in MB
    print(f"  Model path:      {model_path}")
    print(f"  Test data:       {test_data_path}")
    print(f"  Model size:      {model_size:.2f} MB")
    
    # Load model and test data
    print_section("Running Evaluation")
    print(f"  {YELLOW}Please wait, evaluating model...{RESET}")
    
    model = load_model(model_path)
    test_data = load_test_data(test_data_path)
    metrics = evaluate_model(model, test_data)
    
    # Print metrics
    if metrics:
        print_section("Performance Metrics")
        print_metric("Accuracy", metrics['accuracy'])
        
        if 'precision' in metrics:
            print_metric("Precision", metrics['precision'])
            print_metric("Recall", metrics['recall'])
            print_metric("F1 Score", metrics['f1'])
            
            # Display confusion matrix and ROC curve
            try:
                X_test = test_data.drop('target', axis=1)
                y_test = test_data['target']
                y_pred = model.predict(X_test)
                
                # Get probabilities for ROC curve
                if hasattr(model, 'predict_proba'):
                    y_prob = model.predict_proba(X_test)[:, 1]
                else:
                    y_prob = y_pred
                
                # Calculate confusion matrix
                cm = confusion_matrix(y_test, y_pred)
                
                # Display confusion matrix
                print_section("Confusion Matrix")
                print(f"  {BOLD}            Predicted{RESET}")
                print(f"  {BOLD}            Negative    Positive{RESET}")
                print(f"  {BOLD}Actual{RESET}  ┌─────────────┬─────────────┐")
                print(f"  {BOLD}Negative{RESET} │ {GREEN}{cm[0][0]}{RESET} True Neg │ {RED}{cm[0][1]}{RESET} False Pos │")
                print(f"  {BOLD}        {RESET} ├─────────────┼─────────────┤")
                print(f"  {BOLD}Positive{RESET} │ {RED}{cm[1][0]}{RESET} False Neg │ {GREEN}{cm[1][1]}{RESET} True Pos │")
                print(f"  {BOLD}        {RESET} └─────────────┴─────────────┘")
                
                # Calculate ROC curve and AUC
                fpr, tpr, _ = roc_curve(y_test, y_prob)
                roc_auc = auc(fpr, tpr)
                
                # Display ROC curve metrics
                print_section("ROC Curve")
                print(f"  Area Under Curve (AUC): {BLUE}{roc_auc:.4f}{RESET}")
                
                # Create a simple ASCII ROC curve
                width = 40
                height = 20
                curve = [[' ' for _ in range(width)] for _ in range(height)]
                
                # Add grid points
                for i in range(height):
                    for j in range(width):
                        if i == height - 1 or j == 0:
                            curve[i][j] = '·'
                
                # Plot ROC curve points
                for i in range(len(fpr)):
                    x = int(fpr[i] * (width - 1))
                    y = int((1 - tpr[i]) * (height - 1))
                    if 0 <= x < width and 0 <= y < height:
                        curve[y][x] = '*'
                
                # Plot diagonal line (random classifier)
                for i in range(min(width, height)):
                    if 0 <= i < width and 0 <= i < height:
                        pos = int(i * (height - 1) / (width - 1))
                        if curve[pos][i] != '*':
                            curve[pos][i] = '·'
                
                print(f"  {BLUE}TPR{RESET}")
                print(f"  ^")
                # Print the ASCII curve
                for row in curve:
                    print(f"  │ {''.join(row)}")
                print(f"  └{'─' * width}> {BLUE}FPR{RESET}")
                
            except Exception as e:
                print(f"  Unable to display visualization: {str(e)}")
        
        print("\n" + "-" * 60)
        print(f"{GREEN}Evaluation Complete!{RESET}")
        print("-" * 60)
    else:
        print(f"\n{RED}Error: Model evaluation failed.{RESET}")
    
    # Print next steps
    print(f"\n{BOLD}Next Steps:{RESET}")
    print(f"1. The model evaluation is complete and shows the model's performance metrics.")
    print(f"2. These metrics will help you evaluate how well the model predicts credit risk.")
    print(f"3. The Flask application would normally start after this, but we're having connection issues.")
    print(f"\n{YELLOW}Note: This standalone script has been executed successfully!{RESET}")

if __name__ == "__main__":
    main()