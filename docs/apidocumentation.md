# API Documentation - Configuration Compliance Checker

**Version:** 1.0.0  
**Last Updated:** March 2026

---

## Table of Contents

1. [Command Line Interface (CLI)](#cli)
2. [Python API](#python-api)
3. [Web API (Flask)](#web-api)
4. [Data Structures](#data-structures)

---

## CLI

### Usage

```bash
python src/main/python/compliance_checker.py [FILES...] [OPTIONS]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `FILES` | Yes | One or more files to check |

### Options

| Option | Description |
|--------|-------------|
| `--json` | Output report as JSON |
| `--output FILE` | Write JSON report to file |

### Examples

```bash
# Check a single Dockerfile
python src/main/python/compliance_checker.py infrastructure/docker/Dockerfile

# Check multiple files
python src/main/python/compliance_checker.py \
  infrastructure/docker/Dockerfile \
  infrastructure/docker/docker-compose.yml \
  infrastructure/kubernetes/deployment.yaml

# Output as JSON
python src/main/python/compliance_checker.py infrastructure/docker/Dockerfile --json

# Save report to file
python src/main/python/compliance_checker.py infrastructure/docker/Dockerfile \
  --output reports/report.json
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All files compliant (no critical violations) |
| 1 | Critical violations found |

---

## Python API

### Import

```python
from src.main.python.compliance_checker import (
    ComplianceRunner,
    DockerfileChecker,
    DockerComposeChecker,
    KubernetesChecker,
    JenkinsfileChecker,
    Severity,
    Violation,
    CheckResult
)
```

### ComplianceRunner

Main entry point for running compliance checks.

```python
runner = ComplianceRunner()
results = runner.run(['path/to/Dockerfile', 'path/to/docker-compose.yml'])
report = runner.generate_report(results)
```

#### Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `run` | `run(paths: List[str]) -> List[CheckResult]` | Run checks on specified files |
| `generate_report` | `generate_report(results: List[CheckResult]) -> Dict[str, Any]` | Generate structured report |

#### Supported File Types

| File Name | Checker Class |
|-----------|---------------|
| `Dockerfile` | `DockerfileChecker` |
| `docker-compose.yml` | `DockerComposeChecker` |
| `docker-compose.yaml` | `DockerComposeChecker` |
| `deployment.yaml` | `KubernetesChecker` |
| `deployment.yml` | `KubernetesChecker` |
| `service.yaml` | `KubernetesChecker` |
| `Jenkinsfile` | `JenkinsfileChecker` |

### Individual Checkers

Each checker can be used independently:

```python
# Dockerfile Checker
checker = DockerfileChecker()
result = checker.check('/path/to/Dockerfile')

# Docker Compose Checker
checker = DockerComposeChecker()
result = checker.check('/path/to/docker-compose.yml')

# Kubernetes Checker
checker = KubernetesChecker()
result = checker.check('/path/to/deployment.yaml')

# Jenkinsfile Checker
checker = JenkinsfileChecker()
result = checker.check('/path/to/Jenkinsfile')
```

### CheckResult Properties

| Property | Type | Description |
|----------|------|-------------|
| `file` | `str` | File path |
| `file_type` | `str` | Type of file checked |
| `violations` | `List[Violation]` | List of violations found |
| `passed` | `List[str]` | List of rules that passed |
| `is_compliant` | `bool` | True if no violations |
| `critical_count` | `int` | Count of CRITICAL violations |

### Violation Properties

| Property | Type | Description |
|----------|------|-------------|
| `rule_id` | `str` | Rule identifier (e.g., "DF001") |
| `severity` | `Severity` | CRITICAL/HIGH/MEDIUM/LOW/INFO |
| `file` | `str` | File path |
| `line` | `Optional[int]` | Line number (if applicable) |
| `message` | `str` | Violation description |
| `remediation` | `str` | Fix suggestion |

---

## Web API

The Flask application provides a web dashboard and REST API endpoints.

### Running the Web Server

```bash
python src/main/python/app.py
```

Server starts on `http://localhost:5000`

### Endpoints

#### GET /

Serves the main dashboard HTML page.

**Response:** `text/html`

---

#### GET /api/compliance

Returns real-time compliance data from the checker.

**Response Format:**
```json
{
  "summary": {
    "critical_issues": 2,
    "total_violations": 5,
    "status": "NON-COMPLIANT"
  },
  "violations": [
    {
      "severity": "CRITICAL",
      "message": "[DF003] Container may run as root..."
    }
  ],
  "timestamp": "2026-03-20T10:30:00"
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `summary.critical_issues` | `int` | Number of critical violations |
| `summary.total_violations` | `int` | Total violation count |
| `summary.status` | `string` | "COMPLIANT" or "NON-COMPLIANT" |
| `violations` | `array` | List of violation objects |
| `violations[].severity` | `string` | Severity level |
| `violations[].message` | `string` | Violation message with rule ID |
| `timestamp` | `string` | ISO 8601 timestamp |

---

#### GET /api/health

Health check endpoint for monitoring.

**Response Format:**
```json
{
  "status": "OK",
  "timestamp": "2026-03-20T10:30:00"
}
```

---

## Data Structures

### JSON Report Schema

```json
{
  "summary": {
    "files_checked": 3,
    "total_violations": 5,
    "total_passed": 8,
    "critical": 2,
    "overall_compliant": false
  },
  "files": [
    {
      "file": "/path/to/Dockerfile",
      "type": "Dockerfile",
      "compliant": false,
      "violations": [
        {
          "rule_id": "DF003",
          "severity": "CRITICAL",
          "line": 12,
          "message": "Container may run as root...",
          "remediation": "Add: RUN adduser... && USER appuser"
        }
      ],
      "passed": [
        "DF001: FROM uses a pinned tag",
        "DF004: EXPOSE present"
      ]
    }
  ]
}
```

### Severity Enum Values

| Value | Priority | Use Case |
|-------|----------|----------|
| `CRITICAL` | 1 | Security risks that must be fixed |
| `HIGH` | 2 | Important best practices |
| `MEDIUM` | 3 | Recommended improvements |
| `LOW` | 4 | Nice to have |
| `INFO` | 5 | Informational only |

---

## Rule IDs Reference

### Dockerfile Rules

| ID | Severity | Description |
|----|----------|-------------|
| DF001 | HIGH | FROM must not use `:latest` tag |
| DF002 | MEDIUM | Must include HEALTHCHECK |
| DF003 | CRITICAL | Must not run as root |
| DF004 | LOW | Must have EXPOSE instruction |
| DF005 | LOW | Must have LABEL metadata |

### Docker Compose Rules

| ID | Severity | Description |
|----|----------|-------------|
| DC001 | CRITICAL | No hardcoded passwords |
| DC002 | MEDIUM | Must define restart policy |
| DC003 | HIGH | Images must be pinned |

### Kubernetes Rules

| ID | Severity | Description |
|----|----------|-------------|
| K8S001 | HIGH | Containers must have resource limits |
| K8S002 | MEDIUM | Must define livenessProbe |
| K8S003 | MEDIUM | Must define readinessProbe |
| K8S004 | CRITICAL | No privileged containers |

### Jenkinsfile Rules

| ID | Severity | Description |
|----|----------|-------------|
| JK001 | HIGH | Must have a Test stage |
| JK002 | MEDIUM | Must have failure notification |
| JK003 | CRITICAL | No hardcoded credentials |
| JK004 | MEDIUM | Must have Security Scan stage |

---

**End of API Documentation**
