"""
Unit tests for Configuration Compliance Checker
Run: pytest tests/unit/test_compliance.py -v
"""

import os
import tempfile
import pytest
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src/main/python"))
from compliance_checker import (
    DockerfileChecker, DockerComposeChecker,
    KubernetesChecker, JenkinsfileChecker,
    ComplianceRunner, Severity
)


class TestDockerfileChecker:
    checker = DockerfileChecker()

    def _check(self, content: str):
        with tempfile.NamedTemporaryFile("w", suffix="Dockerfile", delete=False) as f:
            f.write(content)
            path = f.name
        new_path = path + "_Dockerfile"
        os.rename(path, new_path)
        result = self.checker.check(new_path)
        os.unlink(new_path)
        return result

    def test_latest_tag_violation(self):
        result = self._check("FROM python:latest\nRUN echo hi\n")
        ids = [v.rule_id for v in result.violations]
        assert "DF001" in ids

    def test_pinned_tag_passes(self):
        result = self._check(
            "FROM python:3.11-slim\nUSER appuser\n"
            "HEALTHCHECK CMD curl -f http://localhost/ || exit 1\n"
            "EXPOSE 8080\nLABEL v=1\n"
        )
        ids = [v.rule_id for v in result.violations]
        assert "DF001" not in ids

    def test_missing_healthcheck(self):
        result = self._check("FROM python:3.11\nUSER appuser\n")
        ids = [v.rule_id for v in result.violations]
        assert "DF002" in ids

    def test_root_user_violation(self):
        result = self._check("FROM python:3.11\n")
        ids = [v.rule_id for v in result.violations]
        assert "DF003" in ids

    def test_non_root_user_passes(self):
        result = self._check(
            "FROM python:3.11\nUSER appuser\n"
            "HEALTHCHECK CMD true\nEXPOSE 8080\nLABEL v=1\n"
        )
        ids = [v.rule_id for v in result.violations]
        assert "DF003" not in ids

    def test_missing_expose(self):
        result = self._check("FROM python:3.11\nUSER appuser\n")
        ids = [v.rule_id for v in result.violations]
        assert "DF004" in ids


class TestDockerComposeChecker:
    checker = DockerComposeChecker()

    def _check(self, content: str):
        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False,
                                         prefix="docker-compose") as f:
            f.write(content)
            path = f.name
        result = self.checker.check(path)
        os.unlink(path)
        return result

    def test_hardcoded_password_violation(self):
        content = """
services:
  db:
    image: postgres:13
    environment:
      - POSTGRES_PASSWORD=mysecretpassword
"""
        result = self._check(content)
        ids = [v.rule_id for v in result.violations]
        assert "DC001" in ids

    def test_missing_restart_policy(self):
        content = """
services:
  app:
    image: myapp:1.0
"""
        result = self._check(content)
        ids = [v.rule_id for v in result.violations]
        assert "DC002" in ids

    def test_latest_image_violation(self):
        content = """
services:
  app:
    image: myapp:latest
    restart: always
"""
        result = self._check(content)
        ids = [v.rule_id for v in result.violations]
        assert "DC003" in ids

    def test_compliant_compose(self):
        content = """
services:
  app:
    image: myapp:1.2.3
    restart: unless-stopped
    environment:
      - APP_ENV=production
"""
        result = self._check(content)
        ids = [v.rule_id for v in result.violations]
        assert "DC002" not in ids
        assert "DC003" not in ids


class TestKubernetesChecker:
    checker = KubernetesChecker()

    def _check(self, content: str):
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False,
                                         prefix="deployment") as f:
            f.write(content)
            path = f.name
        result = self.checker.check(path)
        os.unlink(path)
        return result

    def test_missing_resource_limits(self):
        content = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
      - name: app
        image: myapp:1.0
"""
        result = self._check(content)
        ids = [v.rule_id for v in result.violations]
        assert "K8S001" in ids

    def test_privileged_container(self):
        content = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
      - name: app
        image: myapp:1.0
        securityContext:
          privileged: true
"""
        result = self._check(content)
        ids = [v.rule_id for v in result.violations]
        assert "K8S004" in ids

    def test_missing_probes(self):
        content = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
      - name: app
        image: myapp:1.0
"""
        result = self._check(content)
        ids = [v.rule_id for v in result.violations]
        assert "K8S002" in ids
        assert "K8S003" in ids


class TestComplianceRunner:
    def test_report_summary(self):
        with tempfile.NamedTemporaryFile("w", suffix="_Dockerfile", delete=False) as f:
            f.write("FROM python:latest\n")
            path = f.name
        results = [DockerfileChecker().check(path)]
        report = ComplianceRunner().generate_report(results)
        os.unlink(path)
        assert report["summary"]["files_checked"] == 1
        assert report["summary"]["total_violations"] > 0

    def test_compliant_report(self):
        report = ComplianceRunner().generate_report([])
        assert report["summary"]["overall_compliant"] is True
        assert report["summary"]["files_checked"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])