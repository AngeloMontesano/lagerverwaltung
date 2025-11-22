"""Client helpers for talking to warehouse instances."""
from __future__ import annotations

from typing import Any

import requests
from flask import current_app

from .models import Instance


class InstanceAPI:
    def _headers(self, instance: Instance) -> dict[str, str]:
        headers = {}
        if instance.api_auth_token:
            headers["X-API-TOKEN"] = instance.api_auth_token
        return headers

    def _timeout(self) -> int:
        return current_app.config.get("INSTANCE_API_TIMEOUT", 5)

    def call_health(self, instance: Instance) -> dict[str, Any] | None:
        url = f"{instance.api_base_url}/health" if instance.api_base_url else None
        if not url:
            return None
        response = requests.get(url, headers=self._headers(instance), timeout=self._timeout())
        response.raise_for_status()
        return response.json()

    def call_inventory_summary(self, instance: Instance) -> dict[str, Any] | None:
        url = f"{instance.api_base_url}/api/inventory/summary" if instance.api_base_url else None
        if not url:
            return None
        response = requests.get(url, headers=self._headers(instance), timeout=self._timeout())
        response.raise_for_status()
        return response.json()

    def sync_articles(self, instance: Instance, articles: list[dict]) -> dict[str, Any] | None:
        url = f"{instance.api_base_url}/api/articles/bulk_upsert" if instance.api_base_url else None
        if not url:
            return None
        response = requests.post(url, json={"articles": articles}, headers=self._headers(instance), timeout=self._timeout())
        response.raise_for_status()
        return response.json()
