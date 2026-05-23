"""
ML Model Training
scikit-learn / PyTorch training with MLflow tracking
"""
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import mlflow
from mlflow.tracking import MlflowClient
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ModelTraining:
    """ML model training with experiment tracking"""

    def __init__(
        self,
        experiment_name: str = "data-pipeline-ml",
        tracking_uri: str = "http://mlflow:5000"
    ):
        self.experiment_name = experiment_name
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        self.client = MlflowClient()

    def train_model(
        self,
        model_type: str,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        params: Optional[Dict] = None
    ) -> Dict:
        """Train a model and log to MLflow"""

        if params is None:
            params = {}

        with mlflow.start_run(run_name=f"{model_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}") as run:
            # Log parameters
            mlflow.log_params({
                "model_type": model_type,
                "n_features": X_train.shape[1],
                "n_train_samples": X_train.shape[0],
                "n_test_samples": X_test.shape[0],
                **{k: str(v) for k, v in params.items()}
            })

            # Train based on model type
            if model_type == "sklearn_rf":
                from sklearn.ensemble import RandomForestRegressor
                model = RandomForestRegressor(**params)
            elif model_type == "sklearn_lr":
                from sklearn.linear_model import LinearRegression
                model = LinearRegression(**params)
            elif model_type == "sklearn_gb":
                from sklearn.ensemble import GradientBoostingRegressor
                model = GradientBoostingRegressor(**params)
            else:
                raise ValueError(f"Unknown model type: {model_type}")

            model.fit(X_train, y_train)

            # Evaluate
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)

            mlflow.log_metrics({
                "train_r2": train_score,
                "test_r2": test_score
            })

            # Log model
            mlflow.sklearn.log_model(model, f"model_{model_type}")

            return {
                "run_id": run.info.run_id,
                "train_r2": train_score,
                "test_r2": test_score,
                "model_type": model_type
            }

    def train_all_models(self) -> List[Dict]:
        """Train all configured models"""
        results = []

        # Load features
        try:
            features = pd.read_parquet("/tmp/warehouse/features/aggregate_features.parquet")
            if features.empty:
                logger.warning("No features available for training")
                return results
        except FileNotFoundError:
            logger.warning("Feature store not found")
            return results

        # Prepare data (placeholder - actual implementation would load real data)
        X = features.dropna()
        y = X.pop("record_count") if "record_count" in X.columns else pd.Series([0])

        # Split
        from sklearn.model_selection import train_test_split
        if len(X) < 10:
            logger.warning("Insufficient data for training")
            return results

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train models
        model_types = ["sklearn_rf", "sklearn_lr", "sklearn_gb"]

        for model_type in model_types:
            try:
                result = self.train_model(
                    model_type=model_type,
                    X_train=X_train,
                    y_train=y_train,
                    X_test=X_test,
                    y_test=y_test
                )
                results.append(result)
                logger.info(f"Trained {model_type}: test_r2={result['test_r2']:.4f}")
            except Exception as e:
                logger.error(f"Failed to train {model_type}: {e}")

        return results

    def register_best_model(self, experiment_name: str, model_name: str):
        """Register the best model from an experiment"""
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if not experiment:
            return

        runs = self.client.search_runs(experiment_ids=[experiment.experiment_id])
        best_run = max(runs, key=lambda r: r.data.metrics.get("test_r2", 0))

        model_uri = f"runs:/{best_run.info.run_id}/model"
        self.client.create_registered_model(model_name)
        self.client.create_model_version(
            name=model_name,
            source=model_uri,
            run_id=best_run.info.run_id
        )
        logger.info(f"Registered model: {model_name} from run: {best_run.info.run_id}")