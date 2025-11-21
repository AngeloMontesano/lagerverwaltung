"""Einfache Orchestrierung über Docker Compose oder Portainer."""
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import requests


@dataclass
class DeploymentResult:
    success: bool
    message: str


class TenantOrchestrator:
    def __init__(self, template_path: str, portainer_url: Optional[str] = None, token: Optional[str] = None):
        self.template_path = Path(template_path)
        self.portainer_url = portainer_url
        self.token = token

    def deploy(self, code: str, api_key: str) -> DeploymentResult:
        env = os.environ.copy()
        env.update({"CUSTOMER_CODE": code, "API_KEY": api_key})
        compose_file = self.template_path / "docker-compose.yml"
        if self.portainer_url and self.token:
            return self._trigger_portainer_stack(code, compose_file)
        cmd = ["docker", "compose", "-f", str(compose_file), "up", "-d", "--build"]
        try:
            subprocess.check_output(cmd, env=env)
            return DeploymentResult(True, "Compose gestartet")
        except subprocess.CalledProcessError as exc:
            return DeploymentResult(False, exc.output.decode())

    def stop(self, code: str) -> DeploymentResult:
        env = os.environ.copy()
        env.update({"CUSTOMER_CODE": code})
        compose_file = self.template_path / "docker-compose.yml"
        cmd = ["docker", "compose", "-f", str(compose_file), "down"]
        try:
            subprocess.check_output(cmd, env=env)
            return DeploymentResult(True, "Compose gestoppt")
        except subprocess.CalledProcessError as exc:
            return DeploymentResult(False, exc.output.decode())

    def _trigger_portainer_stack(self, code: str, compose_file: Path) -> DeploymentResult:
        headers = {"X-API-Key": self.token}
        url = f"{self.portainer_url}/stacks"
        files = {"file": open(compose_file, "rb")}
        data = {"name": f"lager-{code}", "endpointId": 1}
        resp = requests.post(url, headers=headers, files=files, data=data, timeout=10)
        if resp.status_code < 300:
            return DeploymentResult(True, "Portainer-Stack aktualisiert")
        return DeploymentResult(False, f"Portainer-Fehler: {resp.text}")
