"""
Feature Engineering
Compute features from Gold layer for ML models
"""
from typing import Dict, List, Optional
import pandas as pd
import pyarrow.parquet as pq
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class FeatureEngineering:
    """Feature engineering from Gold layer data"""

    def __init__(self, gold_path: str = "/tmp/warehouse/gold"):
        self.gold_path = gold_path

    def load_table(self, table_name: str) -> pd.DataFrame:
        """Load a table from the Gold layer"""
        table_path = f"{self.gold_path}/{table_name}.parquet"
        try:
            return pd.read_parquet(table_path)
        except FileNotFoundError:
            logger.warning(f"Table not found: {table_path}")
            return pd.DataFrame()

    def compute_all_features(self) -> Dict[str, pd.DataFrame]:
        """Compute all ML features"""
        features = {}

        # Load Gold layer tables
        fct_daily = self.load_table("fct_daily_aggregates")
        dim_sources = self.load_table("dim_sources")
        dim_time = self.load_table("dim_time")

        if fct_daily.empty:
            logger.warning("No fact data available")
            return features

        # Compute time-based features
        features["time_features"] = self.compute_time_features(fct_daily)

        # Compute aggregate features
        features["aggregate_features"] = self.compute_aggregate_features(fct_daily)

        # Compute source features
        features["source_features"] = self.compute_source_features(fct_daily, dim_sources)

        return features

    def compute_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute time-based features for ML"""
        if "date_key" not in df.columns:
            return pd.DataFrame()

        df = df.copy()
        df["date_key"] = pd.to_datetime(df["date_key"])

        features = pd.DataFrame()
        features["date_key"] = df["date_key"]
        features["day_of_week"] = df["date_key"].dt.dayofweek
        features["is_weekend"] = features["day_of_week"].isin([5, 6]).astype(int)
        features["month"] = df["date_key"].dt.month
        features["day_of_month"] = df["date_key"].dt.day
        features["week_of_year"] = df["date_key"].dt.isocalendar().week.astype(int)

        return features

    def compute_aggregate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute aggregate statistical features"""
        if "record_count" not in df.columns:
            return pd.DataFrame()

        features = pd.DataFrame()

        # Rolling aggregates
        for window in [7, 14, 30]:
            features[f"record_count_rolling_{window}d_mean"] = (
                df.groupby("source_id")["record_count"]
                .transform(lambda x: x.rolling(window, min_periods=1).mean())
            )
            features[f"error_rate_rolling_{window}d"] = (
                df.groupby("source_id")
                .apply(lambda x: (x["error_count"].sum() / x["record_count"].sum() * 100)
                       if x["record_count"].sum() > 0 else 0)
            )

        # Lag features
        for lag in [1, 7, 30]:
            features[f"record_count_lag_{lag}"] = df.groupby("source_id")["record_count"].shift(lag)

        return features

    def compute_source_features(self, fct_df: pd.DataFrame, dim_sources: pd.DataFrame) -> pd.DataFrame:
        """Compute source-related features"""
        if fct_df.empty or dim_sources.empty:
            return pd.DataFrame()

        source_stats = fct_df.groupby("source_id").agg({
            "record_count": ["sum", "mean", "std"],
            "error_count": ["sum", "mean"],
            "latency_p50_ms": "mean",
            "latency_p99_ms": "mean"
        }).reset_index()

        source_stats.columns = [
            "source_id", "total_records", "avg_records", "std_records",
            "total_errors", "avg_errors", "avg_latency_p50", "avg_latency_p99"
        ]

        # Join with source dimension
        merged = source_stats.merge(
            dim_sources[["source_id", "source_type"]],
            on="source_id",
            how="left"
        )

        return merged

class FeatureStore:
    """Feature store for ML models"""

    def __init__(self, store_path: str = "/tmp/warehouse/features"):
        self.store_path = store_path
        import os
        os.makedirs(store_path, exist_ok=True)

    def save_features(self, feature_name: str, df: pd.DataFrame):
        """Save features to the feature store"""
        path = f"{self.store_path}/{feature_name}.parquet"
        df.to_parquet(path, index=False)
        logger.info(f"Saved features to {path}")

    def load_features(self, feature_name: str) -> pd.DataFrame:
        """Load features from the feature store"""
        path = f"{self.store_path}/{feature_name}.parquet"
        return pd.read_parquet(path)

    def list_features(self) -> List[str]:
        """List all available features"""
        import os
        return [f.replace(".parquet", "") for f in os.listdir(self.store_path) if f.endswith(".parquet")]