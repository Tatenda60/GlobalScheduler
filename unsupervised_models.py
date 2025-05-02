"""
Unsupervised learning models for credit risk assessment.
This module provides functionality for anomaly detection and self-training
from uploaded datasets.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from joblib import dump, load
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnomalyDetector:
    """
    Anomaly detection for loan applications using unsupervised learning.
    This class provides methods to train anomaly detection models and 
    identify outliers in loan application data.
    """
    
    def __init__(self, model_dir='./models'):
        """
        Initialize the anomaly detector.
        
        Parameters:
        - model_dir: Directory to save trained models
        """
        self.model_dir = model_dir
        self.isolation_forest = None
        self.scaler = None
        self.pca = None
        self.kmeans = None
        
        # Create model directory if it doesn't exist
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
    
    def preprocess_data(self, df):
        """
        Preprocess data for anomaly detection.
        
        Parameters:
        - df: DataFrame with loan application data
        
        Returns:
        - X: Preprocessed numerical features
        - feature_names: List of feature names used
        """
        try:
            # Select numerical features
            numerical_features = [
                'loan_amount', 'loan_term', 'credit_score', 
                'annual_income', 'monthly_expenses', 'existing_debt'
            ]
            
            # Ensure all required numerical features are present
            available_features = [f for f in numerical_features if f in df.columns]
            
            if len(available_features) < 3:
                logger.warning(f"Only {len(available_features)} numerical features available. Minimum 3 required.")
                raise ValueError(f"Not enough numerical features for anomaly detection. Found: {available_features}")
            
            # Extract features
            X = df[available_features].copy()
            
            # Check for non-numeric values and convert if possible
            for col in X.columns:
                if not pd.api.types.is_numeric_dtype(X[col]):
                    logger.warning(f"Column {col} is not numeric. Attempting to convert.")
                    try:
                        X[col] = pd.to_numeric(X[col], errors='coerce')
                    except:
                        logger.error(f"Failed to convert column {col} to numeric. Dropping column.")
                        X = X.drop(columns=[col])
                        available_features.remove(col)
            
            # Check if we still have enough features
            if len(X.columns) < 3:
                raise ValueError(f"Not enough valid numerical features after preprocessing. Only {len(X.columns)} remain.")
            
            # Calculate derived features safely
            try:
                # Avoid division by zero
                X['debt_to_income'] = df['existing_debt'] / df['annual_income'].replace(0, np.nan)
                X['expense_to_income'] = (df['monthly_expenses'] * 12) / df['annual_income'].replace(0, np.nan)
                X['loan_to_income'] = df['loan_amount'] / df['annual_income'].replace(0, np.nan)
            except Exception as e:
                logger.warning(f"Error calculating derived features: {str(e)}. Using only base features.")
            
            # Replace infinities and NaN values
            X.replace([np.inf, -np.inf], np.nan, inplace=True)
            
            # Check if we have non-NaN values to calculate a valid mean
            if X.count().min() > 0:
                X.fillna(X.mean(), inplace=True)
            else:
                # If a column is all NaN, we can't use mean, so use 0 as fallback
                X.fillna(0, inplace=True)
                
            # Drop any problematic columns after all preprocessing
            X = X.select_dtypes(include=['number'])
            
            if len(X.columns) < 3:
                raise ValueError(f"Not enough valid numerical features after preprocessing. Only {len(X.columns)} remain.")
                
        except Exception as e:
            logger.error(f"Error preprocessing data: {str(e)}")
            raise
        
        # Return preprocessed data and feature names
        return X, X.columns.tolist()
    
    def train(self, df):
        """
        Train anomaly detection models on new data.
        
        Parameters:
        - df: DataFrame with loan application data
        
        Returns:
        - training_info: Dictionary containing training results and metrics
        """
        logger.info(f"Training anomaly detection models on {len(df)} records")
        
        try:
            # Preprocess data
            X, feature_names = self.preprocess_data(df)
            
            # Make sure we have enough data
            if len(X) < 5:
                logger.warning("Not enough data for reliable anomaly detection")
                return None
                
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Determine appropriate contamination rate based on dataset size
            # Smaller datasets should have lower contamination to avoid false positives
            if len(X) <= 10:
                contamination = 0.1  # 10% for small datasets
            elif len(X) <= 50:
                contamination = 0.05  # 5% for medium datasets
            else:
                contamination = 0.03  # 3% for larger datasets
                
            # Train Isolation Forest for anomaly detection with adjusted parameters for small datasets
            self.isolation_forest = IsolationForest(
                n_estimators=min(100, max(50, len(X) * 5)),  # Scale estimators with dataset size
                max_samples='auto',  # 'auto' uses min(256, n_samples)
                contamination=contamination,
                random_state=42
            )
            self.isolation_forest.fit(X_scaled)
            
            # Train PCA for dimensionality reduction and visualization
            # Limit number of components to number of features or 3, whichever is smaller
            n_components = min(3, X.shape[1])
            self.pca = PCA(n_components=n_components)
            X_pca = self.pca.fit_transform(X_scaled)
            
            # Train KMeans for clustering
            # Adjust number of clusters based on dataset size
            n_clusters = min(3, max(2, len(X) // 4))  # At least 2, at most 3 clusters
            self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = self.kmeans.fit_predict(X_scaled)
            
            logger.info(f"Successfully trained models with {len(X)} records, {len(feature_names)} features")
        except Exception as e:
            logger.error(f"Error during model training: {str(e)}")
            raise
        
        # Save models
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        dump(self.scaler, os.path.join(self.model_dir, f'scaler_{timestamp}.joblib'))
        dump(self.isolation_forest, os.path.join(self.model_dir, f'isolation_forest_{timestamp}.joblib'))
        dump(self.pca, os.path.join(self.model_dir, f'pca_{timestamp}.joblib'))
        dump(self.kmeans, os.path.join(self.model_dir, f'kmeans_{timestamp}.joblib'))
        
        # Determine anomalies using Isolation Forest
        anomaly_predictions = self.isolation_forest.predict(X_scaled)
        anomaly_indices = np.where(anomaly_predictions == -1)[0]
        anomaly_scores = self.isolation_forest.decision_function(X_scaled)
        
        # Calculate feature importance for anomalies
        feature_importance = {}
        for i, feature in enumerate(feature_names):
            # Calculate feature importance based on its contribution to anomalies
            importance = abs(X_scaled[anomaly_indices, i].mean() - X_scaled[:, i].mean())
            feature_importance[feature] = float(importance)
            
        # Normalize feature importance
        total_importance = sum(feature_importance.values())
        if total_importance > 0:
            for feature in feature_importance:
                feature_importance[feature] /= total_importance
        
        # Calculate cluster statistics
        cluster_stats = {}
        for cluster_id in range(self.kmeans.n_clusters):
            cluster_indices = np.where(clusters == cluster_id)[0]
            cluster_stats[f'cluster_{cluster_id}'] = {
                'size': len(cluster_indices),
                'percentage': len(cluster_indices) / len(X) * 100,
                'anomaly_count': sum(1 for i in cluster_indices if i in anomaly_indices),
                'center': self.kmeans.cluster_centers_[cluster_id].tolist()
            }
        
        # Prepare training results
        training_info = {
            'timestamp': timestamp,
            'dataset_size': len(df),
            'features_used': feature_names,
            'anomaly_count': len(anomaly_indices),
            'anomaly_percentage': len(anomaly_indices) / len(X) * 100,
            'feature_importance': feature_importance,
            'clusters': cluster_stats,
            'variance_explained': self.pca.explained_variance_ratio_.tolist() if hasattr(self.pca, 'explained_variance_ratio_') else []
        }
        
        logger.info(f"Training completed. Detected {len(anomaly_indices)} anomalies ({training_info['anomaly_percentage']:.1f}%)")
        
        return training_info
    
    def detect_anomalies(self, df):
        """
        Detect anomalies in new data.
        
        Parameters:
        - df: DataFrame with loan application data
        
        Returns:
        - anomaly_results: Dictionary containing detected anomalies and their scores
        """
        if self.isolation_forest is None or self.scaler is None:
            logger.warning("Models not trained. Cannot detect anomalies.")
            return {
                'total_records': len(df),
                'anomaly_count': 0,
                'anomaly_percentage': 0.0,
                'anomaly_records': [],
                'cluster_distribution': {'cluster_0': len(df)},
                'pca_explained_variance': [1.0]  # Default value
            }
        
        try:
            # Preprocess data
            X, feature_names = self.preprocess_data(df)
            
            # Check if we have enough data
            if len(X) < 3:
                logger.warning("Not enough data for anomaly detection")
                return {
                    'total_records': len(df),
                    'anomaly_count': 0,
                    'anomaly_percentage': 0.0,
                    'anomaly_records': [],
                    'cluster_distribution': {'cluster_0': len(df)},
                    'pca_explained_variance': [1.0]
                }
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Detect anomalies
            anomaly_predictions = self.isolation_forest.predict(X_scaled)
            anomaly_scores = self.isolation_forest.decision_function(X_scaled)
            
            # Create anomaly mask (True for anomalies)
            anomaly_mask = anomaly_predictions == -1
            
            # Get indices of anomalies
            anomaly_indices = np.where(anomaly_mask)[0]
            
            # If we detected too many anomalies (more than 30%), limit to the most anomalous ones
            if len(anomaly_indices) > len(X) * 0.3:
                logger.warning(f"Too many anomalies detected ({len(anomaly_indices)}). Limiting to 30% most anomalous.")
                # Sort indices by anomaly score (lower is more anomalous)
                sorted_indices = np.argsort(anomaly_scores)
                # Take the top 30% as anomalies
                max_anomalies = int(len(X) * 0.3)
                anomaly_indices = sorted_indices[:max_anomalies]
        except Exception as e:
            logger.error(f"Error in anomaly detection: {str(e)}")
            return {
                'total_records': len(df),
                'anomaly_count': 0,
                'anomaly_percentage': 0.0,
                'anomaly_records': [],
                'error_message': str(e),
                'cluster_distribution': {'cluster_0': len(df)},
                'pca_explained_variance': [1.0]
            }
        
        # Project to PCA space for visualization
        X_pca = self.pca.transform(X_scaled)
        
        # Get cluster assignments
        clusters = self.kmeans.predict(X_scaled)
        
        # Prepare anomaly report
        anomaly_records = []
        for idx in anomaly_indices:
            # Get the most anomalous features for this record
            record_values = X_scaled[idx]
            feature_scores = {}
            
            for i, feature in enumerate(feature_names):
                # Calculate how unusual this value is (distance from mean in std devs)
                z_score = abs(record_values[i])
                feature_scores[feature] = float(z_score)
            
            # Sort features by anomaly contribution
            sorted_features = sorted(
                feature_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # Extract top anomalous features
            top_anomalous_features = {k: v for k, v in sorted_features[:3]}
            
            # Create anomaly record
            anomaly_record = {
                'index': int(idx),
                'score': float(anomaly_scores[idx]),
                'cluster': int(clusters[idx]),
                'pca_coordinates': X_pca[idx].tolist(),
                'anomalous_features': top_anomalous_features,
                'record_values': {
                    feature: float(X.iloc[idx][feature]) 
                    for feature in feature_names
                }
            }
            
            anomaly_records.append(anomaly_record)
        
        # Sort anomalies by score (most anomalous first)
        anomaly_records.sort(key=lambda x: x['score'])
        
        # Prepare results
        anomaly_results = {
            'total_records': len(df),
            'anomaly_count': len(anomaly_indices),
            'anomaly_percentage': (len(anomaly_indices) / len(df)) * 100,
            'anomaly_threshold': self.isolation_forest.threshold_,
            'anomaly_records': anomaly_records,
            'pca_explained_variance': self.pca.explained_variance_ratio_.tolist() if hasattr(self.pca, 'explained_variance_ratio_') else [1.0],
            'cluster_distribution': {
                f'cluster_{i}': sum(1 for c in clusters if c == i)
                for i in range(self.kmeans.n_clusters)
            }
        }
        
        return anomaly_results
    
    def load_latest_models(self):
        """
        Load the latest trained models from disk.
        
        Returns:
        - success: Boolean indicating if models were loaded successfully
        """
        try:
            # Get all model files
            isolation_forest_files = [f for f in os.listdir(self.model_dir) if f.startswith('isolation_forest_')]
            scaler_files = [f for f in os.listdir(self.model_dir) if f.startswith('scaler_')]
            pca_files = [f for f in os.listdir(self.model_dir) if f.startswith('pca_')]
            kmeans_files = [f for f in os.listdir(self.model_dir) if f.startswith('kmeans_')]
            
            # Get latest files
            if isolation_forest_files and scaler_files and pca_files and kmeans_files:
                latest_isolation_forest = sorted(isolation_forest_files)[-1]
                latest_scaler = sorted(scaler_files)[-1]
                latest_pca = sorted(pca_files)[-1]
                latest_kmeans = sorted(kmeans_files)[-1]
                
                # Load models
                self.isolation_forest = load(os.path.join(self.model_dir, latest_isolation_forest))
                self.scaler = load(os.path.join(self.model_dir, latest_scaler))
                self.pca = load(os.path.join(self.model_dir, latest_pca))
                self.kmeans = load(os.path.join(self.model_dir, latest_kmeans))
                
                logger.info(f"Loaded models: {latest_isolation_forest}, {latest_scaler}, {latest_pca}, {latest_kmeans}")
                return True
            else:
                logger.warning("No models found in directory.")
                return False
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            return False