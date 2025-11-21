"""HTTP-Client für Mandanten-APIs."""
import requests


class InstanceApiClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _headers(self) -> dict:
        return {"X-API-Key": self.api_key}

    def health(self) -> dict:
        resp = requests.get(f"{self.base_url}/api/health", headers=self._headers(), timeout=5)
        resp.raise_for_status()
        return resp.json()

    def inventory_summary(self) -> dict:
        resp = requests.get(
            f"{self.base_url}/api/inventory/summary", headers=self._headers(), timeout=5
        )
        resp.raise_for_status()
        return resp.json()

    def sync_master(self, records: list[dict]) -> dict:
        resp = requests.post(
            f"{self.base_url}/api/sync/master",
            headers=self._headers(),
            json=records,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
