"""
Standalone script to run model evaluation.
This script can be executed directly to evaluate the model
without needing to start the Flask application.
"""
from model_evaluation import run_evaluation
import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')

# ANSI color codes for terminal output
RESET = "\033[0m"
BOLD = "\033[1m"
BLUE = "\033[34m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"

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
    if name.lower() == "accuracy" or name.lower() == "f1 score":
        if value >= good_threshold:
            color = GREEN
        elif value >= good_threshold - 0.2:
            color = YELLOW
        else:
            color = RED
    else:
        color = BLUE
    
    dots = "." * (20 - len(name))
    print(f"  {name} {dots} {color}{value:.4f}{RESET}")

def main():
    """Run model evaluation independently"""
    # Clear terminal
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print_header("MACHINE LEARNING MODEL EVALUATION")
    
    print(f"{BOLD}Date and Time:{RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get model and data paths from environment or use defaults
    model_path = os.environ.get('MODEL_PATH', 'your_model.pkl')
    test_data_path = os.environ.get('TEST_DATA_PATH', 'test_data.csv')
    
    print_section("Model Information")
    
    # Check if model and test data files exist
    if not os.path.exists(model_path):
        print(f"  {RED}Model file not found:{RESET} {model_path}")
        print(f"  {YELLOW}Run generate_sample_model.py to create it.{RESET}")
        return
    
    if not os.path.exists(test_data_path):
        print(f"  {RED}Test data file not found:{RESET} {test_data_path}")
        print(f"  {YELLOW}Run generate_sample_model.py to create it.{RESET}")
        return
    
    model_size = os.path.getsize(model_path) / (1024*1024)  # Size in MB
    print(f"  Model path:      {model_path}")
    print(f"  Test data:       {test_data_path}")
    print(f"  Model size:      {model_size:.2f} MB")
    
    try:
        print_section("Running Evaluation")
        print(f"  {YELLOW}Please wait, evaluating model...{RESET}")
        
        results = run_evaluation(model_path, test_data_path)
        
        if results:
            print_section("Performance Metrics")
            print_metric("Accuracy", results['accuracy'])
            
            # For binary classification metrics, we need to monitor for them
            # Add placeholders for additional metrics that will show in logs
            
            # Manually look at the predictions to calculate metrics if needed
            if 'predictions' in results and 'true_values' in results:
                from sklearn.metrics import precision_score, recall_score, f1_score
                y_pred = results['predictions']
                y_true = results['true_values']
                
                try:
                    precision = precision_score(y_true, y_pred)
                    recall = recall_score(y_true, y_pred)
                    f1 = f1_score(y_true, y_pred)
                    
                    print_metric("Precision", precision)
                    print_metric("Recall", recall)
                    print_metric("F1 Score", f1)
                except Exception as e:
                    print(f"  Note: Could not calculate additional metrics: {str(e)}")
            
            print("\n" + "-" * 60)
            print(f"{GREEN}Evaluation Complete!{RESET}")
            print("-" * 60)
        else:
            print(f"\n{RED}Error: Model evaluation failed to return results.{RESET}")
    
    except Exception as e:
        print(f"\n{RED}Error during model evaluation: {str(e)}{RESET}")
        import traceback
        print(f"{YELLOW}{traceback.format_exc()}{RESET}")

if __name__ == "__main__":
    main()