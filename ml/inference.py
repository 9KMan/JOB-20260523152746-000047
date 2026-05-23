"""
ML Batch Inference
Score new records as they enter the pipeline
"""
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
import mlflow
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BatchInference:
    """Batch inference for ML models"""

    def __init__(self, model_name: str = "data-pipeline-model"):
        self.model_name = model_name
        self.model = None
        self.model_version = None

    def load_model(self):
        """Load the latest production model"""
        try:
            client = mlflow.tracking.MlflowClient()
            latest_version = client.get_latest_version(self.model_name)

            self.model = mlflow.sklearn.load_model(
                f"models:/{self.model_name}/{latest_version.version}"
            )
            self.model_version = latest_version.version
            logger.info(f"Loaded model {self.model_name}:{self.model_version}")
        except Exception as e:
            logger.warning(f"Could not load model: {e}")
            self.model = None

    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """Run inference on features"""
        if self.model is None:
            self.load_model()

        if self.model is None:
            logger.warning("No model available, returning zeros")
            return np.zeros(len(features))

        predictions = self.model.predict(features)
        return predictions

    def run(self) -> Dict:
        """Run batch inference on new records"""
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "records_processed": 0,
            "predictions": []
        }

        # Load new records from the pipeline
        try:
            new_records = pd.read_parquet("/tmp/warehouse/bronze/new_records.parquet")
        except FileNotFoundError:
            logger.info("No new records for inference")
            return results

        if new_records.empty:
            return results

        # Compute features
        from ml.features import FeatureEngineering
        fe = FeatureEngineering()

        # Prepare features (placeholder - actual implementation would compute real features)
        features = new_records.select_dtypes(include=[np.number]).fillna(0)

        if features.empty:
            return results

        # Run inference
        predictions = self.predict(features)

        # Save predictions
        new_records["prediction"] = predictions
        output_path = f"/tmp/warehouse/gold/predictions_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.parquet"
        new_records.to_parquet(output_path)

        results["records_processed"] = len(new_records)
        results["output_path"] = output_path

        logger.info(f"Processed {len(new_records)} records, predictions saved to {output_path}")

        return results

class ModelMonitoring:
    """Monitor model performance and detect drift"""

    def __init__(self):
        self.baseline_metrics = {}
        self.current_metrics = {}

    def compute_metrics(self, predictions: np.ndarray, actuals: Optional[np.ndarray] = None) -> Dict:
        """Compute monitoring metrics"""
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "n_predictions": len(predictions),
            "prediction_mean": float(np.mean(predictions)),
            "prediction_std": float(np.std(predictions)),
            "prediction_min": float(np.min(predictions)),
            "prediction_max": float(np.max(predictions))
        }

        if actuals is not None:
            from sklearn.metrics import mean_squared_error, mean_absolute_error
            metrics["mae"] = float(mean_absolute_error(actuals, predictions))
            metrics["mse"] = float(mean_squared_error(actuals, predictions))
            metrics["rmse"] = float(np.sqrt(metrics["mse"]))

        return metrics

    def detect_drift(self, current_metrics: Dict, baseline_metrics: Dict, threshold: float = 0.1) -> List[str]:
        """Detect drift in model metrics"""
        drifts = []

        for metric in ["prediction_mean", "prediction_std"]:
            if metric in current_metrics and metric in baseline_metrics:
                current_val = current_metrics[metric]
                baseline_val = baseline_metrics[metric]

                if baseline_val != 0:
                    change = abs(current_val - baseline_val) / baseline_val
                    if change > threshold:
                        drifts.append(f"{metric}: {change:.2%} change (baseline={baseline_val:.4f}, current={current_val:.4f})")

        return drifts