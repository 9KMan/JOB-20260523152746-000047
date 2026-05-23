"""
BI Dashboard Integration
Metabase/Superset connection utilities
"""
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class MetricDefinition:
    """Defines a metric with consistent calculation across all reports"""

    def __init__(self, name: str, calculation: str, description: str):
        self.name = name
        self.calculation = calculation
        self.description = description

class MetricStore:
    """Centralized metric definitions for consistent reporting"""

    def __init__(self):
        self.metrics: Dict[str, MetricDefinition] = {}
        self._register_default_metrics()

    def _register_default_metrics(self):
        default_metrics = [
            MetricDefinition(
                "daily_record_count",
                "COUNT(*) WHERE date_key = CURRENT_DATE",
                "Number of records processed today"
            ),
            MetricDefinition(
                "daily_error_rate",
                "SUM(error_count) / SUM(record_count) * 100",
                "Percentage of records with errors"
            ),
            MetricDefinition(
                "avg_processing_latency",
                "AVG(latency_p50_ms)",
                "Average P50 processing latency in ms"
            ),
            MetricDefinition(
                "p99_latency",
                "AVG(latency_p99_ms)",
                "Average P99 processing latency in ms"
            ),
            MetricDefinition(
                "source_uptime",
                "COUNT(DISTINCT source_id) WHERE record_count > 0",
                "Number of active sources today"
            ),
        ]
        for metric in default_metrics:
            self.register(metric)

    def register(self, metric: MetricDefinition):
        self.metrics[metric.name] = metric
        logger.info(f"Registered metric: {metric.name}")

    def get(self, name: str) -> Optional[MetricDefinition]:
        return self.metrics.get(name)

    def list_all(self) -> List[str]:
        return list(self.metrics.keys())

class DashboardConnection:
    """Connection utilities for BI tools"""

    def __init__(self, tool: str = "metabase"):
        self.tool = tool
        self.base_url = None
        self.api_key = None

    def configure(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        logger.info(f"Configured {self.tool} connection to {base_url}")

    def refresh_dashboard(self, dashboard_id: int):
        """Trigger dashboard refresh (Metabase API)"""
        import requests
        if not self.base_url:
            raise ValueError("Dashboard connection not configured")

        url = f"{self.base_url}/api/dashboard/{dashboard_id}/refresh"
        response = requests.post(url, headers={"x-api-key": self.api_key})
        response.raise_for_status()
        return response.json()

    def get_dashboard(self, dashboard_id: int) -> Dict:
        """Get dashboard details"""
        import requests
        url = f"{self.base_url}/api/dashboard/{dashboard_id}"
        response = requests.get(url, headers={"x-api-key": self.api_key})
        response.raise_for_status()
        return response.json()

    def list_dashboards(self) -> List[Dict]:
        """List all dashboards"""
        import requests
        url = f"{self.base_url}/api/dashboard"
        response = requests.get(url, headers={"x-api-key": self.api_key})
        response.raise_for_status()
        return response.json()

class RowLevelSecurity:
    """Multi-tenant data isolation"""

    def __init__(self):
        self.policies = {}

    def add_policy(self, tenant_id: str, filter_rule: str):
        """Add a row-level security policy for a tenant"""
        self.policies[tenant_id] = {
            "filter": filter_rule,
            "tenant_id": tenant_id
        }
        logger.info(f"Added RLS policy for tenant: {tenant_id}")

    def get_policy(self, tenant_id: str) -> Optional[Dict]:
        return self.policies.get(tenant_id)

    def apply_filter(self, tenant_id: str, query: str) -> str:
        """Apply row-level security filter to a query"""
        policy = self.get_policy(tenant_id)
        if not policy:
            return query
        return f"{query} WHERE {policy['filter']}"