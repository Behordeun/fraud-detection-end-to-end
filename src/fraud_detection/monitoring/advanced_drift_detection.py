import pandas as pd
import numpy as np
from scipy import stats
from sklearn.metrics import jensen_shannon_distance
import mlflow
import json
from datetime import datetime

class AdvancedDriftDetector:
    def __init__(self, reference_data_path="data/processed/train"):
        self.reference_data = pd.read_parquet(reference_data_path)
        self.drift_threshold = 0.1
        
    def calculate_psi(self, expected, actual, buckets=10):
        """Calculate Population Stability Index."""
        def scale_range(input_x, min_x, max_x):
            range_x = max_x - min_x
            if range_x == 0:
                return np.zeros_like(input_x)
            return (input_x - min_x) / range_x
        
        min_val, max_val = expected.min(), expected.max()
        expected_scaled = scale_range(expected, min_val, max_val)
        actual_scaled = scale_range(actual, min_val, max_val)
        
        expected_counts, _ = np.histogram(expected_scaled, bins=buckets, range=(0, 1))
        actual_counts, _ = np.histogram(actual_scaled, bins=buckets, range=(0, 1))
        
        expected_percents = expected_counts / len(expected)
        actual_percents = actual_counts / len(actual)
        
        # Avoid division by zero
        expected_percents = np.where(expected_percents == 0, 0.0001, expected_percents)
        actual_percents = np.where(actual_percents == 0, 0.0001, actual_percents)
        
        psi = np.sum((actual_percents - expected_percents) * np.log(actual_percents / expected_percents))
        return psi
    
    def detect_feature_drift(self, new_data):
        """Detect drift in individual features."""
        drift_results = {}
        
        for column in self.reference_data.columns:
            if column in new_data.columns and pd.api.types.is_numeric_dtype(self.reference_data[column]):
                # PSI for numerical features
                psi = self.calculate_psi(self.reference_data[column], new_data[column])
                
                # KS test
                ks_stat, ks_p_value = stats.ks_2samp(self.reference_data[column], new_data[column])
                
                # Jensen-Shannon distance
                ref_hist, _ = np.histogram(self.reference_data[column], bins=50, density=True)
                new_hist, _ = np.histogram(new_data[column], bins=50, density=True)
                js_distance = jensen_shannon_distance(ref_hist + 1e-10, new_hist + 1e-10)
                
                drift_results[column] = {
                    'psi': psi,
                    'ks_statistic': ks_stat,
                    'ks_p_value': ks_p_value,
                    'js_distance': js_distance,
                    'drift_detected': psi > self.drift_threshold or ks_p_value < 0.05
                }
        
        return drift_results
    
    def detect_model_drift(self, predictions, actuals=None):
        """Detect model performance drift."""
        model_drift = {}
        
        # Prediction distribution drift
        if hasattr(self, 'reference_predictions'):
            pred_psi = self.calculate_psi(self.reference_predictions, predictions)
            model_drift['prediction_psi'] = pred_psi
            model_drift['prediction_drift'] = pred_psi > self.drift_threshold
        
        # Performance drift (if actuals available)
        if actuals is not None:
            from sklearn.metrics import roc_auc_score, precision_score, recall_score
            
            current_auc = roc_auc_score(actuals, predictions)
            current_precision = precision_score(actuals, predictions > 0.5)
            current_recall = recall_score(actuals, predictions > 0.5)
            
            model_drift.update({
                'current_auc': current_auc,
                'current_precision': current_precision,
                'current_recall': current_recall
            })
        
        return model_drift
    
    def generate_drift_report(self, new_data_path, output_path="drift_report.json"):
        """Generate comprehensive drift report."""
        new_data = pd.read_parquet(new_data_path)
        
        # Feature drift detection
        feature_drift = self.detect_feature_drift(new_data)
        
        # Summary statistics
        drift_summary = {
            'timestamp': datetime.now().isoformat(),
            'total_features': len(feature_drift),
            'drifted_features': sum(1 for f in feature_drift.values() if f['drift_detected']),
            'drift_percentage': sum(1 for f in feature_drift.values() if f['drift_detected']) / len(feature_drift) * 100,
            'feature_drift_details': feature_drift
        }
        
        # Save report
        with open(output_path, 'w') as f:
            json.dump(drift_summary, f, indent=2, default=str)
        
        # Log to MLflow
        with mlflow.start_run(run_name="drift_detection"):
            mlflow.log_metrics({
                'drift_percentage': drift_summary['drift_percentage'],
                'drifted_features': drift_summary['drifted_features']
            })
            mlflow.log_artifact(output_path)
        
        print(f"Drift Report: {drift_summary['drift_percentage']:.1f}% of features show drift")
        return drift_summary

if __name__ == "__main__":
    detector = AdvancedDriftDetector()
    detector.generate_drift_report("data/processed/test")