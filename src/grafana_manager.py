"""Grafana dashboard and datasource management using grafana-client."""

import json
import os
from pathlib import Path

from grafana_client import GrafanaApi
from grafana_client.client import GrafanaClientError


class GrafanaManager:
    """Manager for Grafana dashboards and datasources."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 3000,
        username: str = "admin",
        password: str = "admin",
    ):
        self.grafana = GrafanaApi(
            auth=(username, password),
            host=host,
            port=port,
        )

    def health_check(self) -> dict:
        """Check Grafana health status."""
        try:
            return self.grafana.health.check()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_datasources(self) -> list:
        """List all configured datasources."""
        return self.grafana.datasource.list_datasources()

    def get_datasource(self, name: str) -> dict | None:
        """Get a datasource by name."""
        try:
            return self.grafana.datasource.get_datasource_by_name(name)
        except GrafanaClientError:
            return None

    def create_prometheus_datasource(
        self,
        name: str = "Prometheus",
        url: str = "http://prometheus:9090",
        is_default: bool = True,
    ) -> dict:
        """Create a Prometheus datasource."""
        datasource = {
            "name": name,
            "type": "prometheus",
            "url": url,
            "access": "proxy",
            "isDefault": is_default,
        }

        existing = self.get_datasource(name)
        if existing:
            return self.grafana.datasource.update_datasource(
                existing["id"], datasource
            )
        return self.grafana.datasource.create_datasource(datasource)

    def list_dashboards(self) -> list:
        """List all dashboards."""
        return self.grafana.search.search_dashboards()

    def get_dashboard(self, uid: str) -> dict | None:
        """Get a dashboard by UID."""
        try:
            return self.grafana.dashboard.get_dashboard(uid)
        except GrafanaClientError:
            return None

    def create_or_update_dashboard(
        self,
        dashboard: dict,
        folder_id: int = 0,
        overwrite: bool = True,
    ) -> dict:
        """Create or update a dashboard."""
        payload = {
            "dashboard": dashboard,
            "folderId": folder_id,
            "overwrite": overwrite,
        }
        return self.grafana.dashboard.update_dashboard(payload)

    def import_dashboard_from_file(self, file_path: str | Path) -> dict:
        """Import a dashboard from a JSON file."""
        path = Path(file_path)
        with open(path) as f:
            dashboard = json.load(f)

        # Reset id to allow creation
        dashboard["id"] = None

        return self.create_or_update_dashboard(dashboard)

    def delete_dashboard(self, uid: str) -> dict:
        """Delete a dashboard by UID."""
        return self.grafana.dashboard.delete_dashboard(uid)

    def create_metaflow_folder(self) -> dict:
        """Create a folder for Metaflow dashboards."""
        try:
            return self.grafana.folder.create_folder("Metaflow")
        except GrafanaClientError as e:
            if "name-exists" in str(e):
                folders = self.grafana.folder.get_all_folders()
                for folder in folders:
                    if folder["title"] == "Metaflow":
                        return folder
            raise

    def create_alert_rule(
        self,
        name: str,
        condition: str,
        threshold: float,
        for_duration: str = "5m",
    ) -> dict:
        """Create a simple alert rule (Grafana 8+ alerting)."""
        # Note: This is a simplified example. Real alerting rules
        # require more complex configuration.
        alert_rule = {
            "title": name,
            "condition": condition,
            "data": [
                {
                    "refId": "A",
                    "queryType": "",
                    "model": {
                        "expr": condition,
                        "intervalMs": 1000,
                        "maxDataPoints": 43200,
                        "refId": "A",
                    },
                }
            ],
            "for": for_duration,
            "annotations": {
                "summary": f"Alert: {name}",
            },
            "labels": {
                "severity": "warning",
            },
        }
        return alert_rule


def setup_grafana_for_metaflow(
    host: str = "localhost",
    port: int = 3000,
    username: str = "admin",
    password: str = "admin",
    dashboards_dir: str | Path | None = None,
) -> None:
    """Setup Grafana with Metaflow dashboards and datasources."""
    manager = GrafanaManager(host, port, username, password)

    print("Checking Grafana health...")
    health = manager.health_check()
    print(f"Grafana status: {health}")

    if health.get("database") != "ok":
        print("Warning: Grafana may not be fully ready")
        return

    print("\nSetting up Prometheus datasource...")
    ds = manager.create_prometheus_datasource()
    print(f"Datasource configured: {ds.get('name', 'unknown')}")

    if dashboards_dir:
        dashboards_path = Path(dashboards_dir)
        print(f"\nImporting dashboards from {dashboards_path}...")

        for dashboard_file in dashboards_path.glob("*.json"):
            print(f"  Importing {dashboard_file.name}...")
            try:
                result = manager.import_dashboard_from_file(dashboard_file)
                print(f"    Imported: {result.get('uid', 'unknown')}")
            except Exception as e:
                print(f"    Error: {e}")

    print("\nGrafana setup complete!")


if __name__ == "__main__":
    # Default setup when run directly
    dashboards_dir = Path(__file__).parent.parent / "grafana" / "dashboards"
    setup_grafana_for_metaflow(
        host=os.getenv("GRAFANA_HOST", "localhost"),
        port=int(os.getenv("GRAFANA_PORT", "3000")),
        username=os.getenv("GRAFANA_USER", "admin"),
        password=os.getenv("GRAFANA_PASSWORD", "admin"),
        dashboards_dir=dashboards_dir,
    )
