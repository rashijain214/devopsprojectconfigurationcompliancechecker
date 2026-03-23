# User Guide - Configuration Compliance Checker

**Version:** 1.0.0  
**Last Updated:** March 2026

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Using the CLI](#using-the-cli)
5. [Understanding Reports](#understanding-reports)
6. [CI/CD Integration](#cicd-integration)
7. [Web Dashboard](#web-dashboard)
8. [Troubleshooting](#troubleshooting)

---

## Introduction

The Configuration Compliance Checker is a DevOps tool that automatically scans infrastructure-as-code files for security misconfigurations and best practice violations.

### Supported File Types

- **Dockerfile** - Container image definitions
- **docker-compose.yml** - Multi-container orchestration
- **Kubernetes YAML** - Container orchestration manifests
- **Jenkinsfile** - CI/CD pipeline definitions

### Severity Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| **CRITICAL** | Security risk | Must fix before deployment |
| **HIGH** | Important issue | Should fix soon |
| **MEDIUM** | Recommended fix | Fix when convenient |
| **LOW** | Best practice | Nice to have |

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Step 1: Clone the Repository

```bash
git clone https://github.com/rashijain214/devopsprojectcompliancechecker.git
cd devopsprojectcompliancechecker
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Verify Installation

```bash
python src/main/python/compliance_checker.py --help
```

---

## Quick Start

### Check a Single File

```bash
python src/main/python/compliance_checker.py infrastructure/docker/Dockerfile
```

### Check Multiple Files

```bash
python src/main/python/compliance_checker.py \
  infrastructure/docker/Dockerfile \
  infrastructure/docker/docker-compose.yml \
  infrastructure/kubernetes/deployment.yaml
```

### Example Output

```
============================================================
  CONFIGURATION COMPLIANCE REPORT
============================================================
  Files Checked   : 1
  Rules Passed    : 3
  Violations      : 2
  Critical Issues : 1
  Status          : NON-COMPLIANT
============================================================

[FAIL] [Dockerfile] infrastructure/docker/Dockerfile
   [CRITICAL] DF003: Container may run as root — no non-root USER set.
         Fix: Add: RUN adduser --disabled-password appuser && USER appuser
   [HIGH] DF001 (line 1): FROM uses ':latest' tag — non-deterministic builds.
         Fix: Pin to a specific image version e.g. `FROM python:3.11-slim`
   [PASS] DF004: EXPOSE present
   [PASS] DF005: LABEL metadata present

============================================================
```

---

## Using the CLI

### Basic Syntax

```bash
python src/main/python/compliance_checker.py [FILES...] [OPTIONS]
```

### Options

| Option | Description | Example |
|--------|-------------|---------|
| `--json` | Output as JSON | `--json` |
| `--output FILE` | Save JSON to file | `--output report.json` |

### JSON Output Example

```bash
python src/main/python/compliance_checker.py infrastructure/docker/Dockerfile --json
```

Output:
```json
{
  "summary": {
    "files_checked": 1,
    "total_violations": 2,
    "total_passed": 3,
    "critical": 1,
    "overall_compliant": false
  },
  "files": [...]
}
```

### Save Report to File

```bash
python src/main/python/compliance_checker.py \
  infrastructure/docker/Dockerfile \
  --output reports/compliance-report.json
```

---

## Understanding Reports

### Report Sections

1. **Summary** - Overview of all checks
   - Files checked
   - Rules passed
   - Violations found
   - Critical issues count
   - Overall status

2. **File Details** - Per-file breakdown
   - File path and type
   - Compliance status
   - Violations with remediation hints
   - Passed rules

### Interpreting Violations

Each violation includes:

- **Rule ID** - Unique identifier (e.g., DF001)
- **Severity** - CRITICAL/HIGH/MEDIUM/LOW
- **Line Number** - Where applicable
- **Message** - What was found
- **Remediation** - How to fix it

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - no critical violations |
| 1 | Failure - critical violations found |

Use exit codes in CI/CD pipelines to block deployments with critical issues.

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Compliance Check

on: [push, pull_request]

jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run compliance check
        run: |
          python src/main/python/compliance_checker.py \
            infrastructure/docker/Dockerfile \
            infrastructure/docker/docker-compose.yml
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    stages {
        stage('Compliance Check') {
            steps {
                sh '''
                    python src/main/python/compliance_checker.py \
                        infrastructure/docker/Dockerfile \
                        --output compliance-report.json
                '''
            }
        }
    }
    post {
        failure {
            echo 'Critical compliance violations found!'
        }
    }
}
```

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
python src/main/python/compliance_checker.py \
  infrastructure/docker/Dockerfile \
  infrastructure/kubernetes/deployment.yaml

if [ $? -ne 0 ]; then
    echo "Commit blocked: Critical violations found"
    exit 1
fi
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Web Dashboard

### Starting the Dashboard

```bash
python src/main/python/app.py
```

The dashboard will be available at `http://localhost:5000`

### Dashboard Features

- **Real-time compliance status** - Current state of all checked files
- **Violation summary** - Count of issues by severity
- **Detailed violations** - List with rule IDs and messages
- **Timestamp** - Last check time

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Dashboard UI |
| `/api/compliance` | JSON compliance data |
| `/api/health` | Health check |

---

## Policy Rules Reference

### Dockerfile Rules

| ID | Severity | Rule | Fix |
|----|----------|------|-----|
| DF001 | HIGH | No `:latest` tag in FROM | Use specific version: `FROM python:3.11` |
| DF002 | MEDIUM | Must have HEALTHCHECK | Add: `HEALTHCHECK CMD curl -f http://localhost:8080/health \|\| exit 1` |
| DF003 | CRITICAL | Must not run as root | Add: `RUN adduser --disabled-password appuser && USER appuser` |
| DF004 | LOW | Must have EXPOSE | Add: `EXPOSE 8080` |
| DF005 | LOW | Must have LABEL | Add: `LABEL maintainer="you@example.com" version="1.0"` |

### Docker Compose Rules

| ID | Severity | Rule | Fix |
|----|----------|------|-----|
| DC001 | CRITICAL | No hardcoded passwords | Use: `PASSWORD=${MY_PASSWORD}` or Docker secrets |
| DC002 | MEDIUM | Must have restart policy | Add: `restart: unless-stopped` |
| DC003 | HIGH | Images must be pinned | Use: `image: nginx:1.24` not `nginx:latest` |

### Kubernetes Rules

| ID | Severity | Rule | Fix |
|----|----------|------|-----|
| K8S001 | HIGH | Must have resource limits | Add: `resources.limits: {cpu: '500m', memory: '256Mi'}` |
| K8S002 | MEDIUM | Must have livenessProbe | Add health check probe |
| K8S003 | MEDIUM | Must have readinessProbe | Add readiness probe |
| K8S004 | CRITICAL | No privileged containers | Set: `securityContext.privileged: false` |

### Jenkinsfile Rules

| ID | Severity | Rule | Fix |
|----|----------|------|-----|
| JK001 | HIGH | Must have Test stage | Add: `stage('Test') { steps { sh 'make test' } }` |
| JK002 | MEDIUM | Must have failure notification | Add: `post { failure { emailext(...) } }` |
| JK003 | CRITICAL | No hardcoded credentials | Use: `withCredentials([usernamePassword(...)])` |
| JK004 | MEDIUM | Must have Security Scan | Add Trivy/Snyk scan stage |

---

## Troubleshooting

### Common Issues

#### "No checker for file type"

**Cause:** File name not recognized  
**Solution:** Ensure files are named exactly:
- `Dockerfile` (not `dockerfile` or `DockerFile`)
- `docker-compose.yml` or `docker-compose.yaml`
- `deployment.yaml` or `deployment.yml`
- `Jenkinsfile`

#### YAML parsing errors

**Cause:** Invalid YAML syntax  
**Solution:** 
```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('file.yaml'))"
```

#### Permission denied

**Cause:** Script not executable  
**Solution:**
```bash
chmod +x src/main/python/compliance_checker.py
```

#### Missing dependencies

**Cause:** Requirements not installed  
**Solution:**
```bash
pip install -r requirements.txt
```

### Getting Help

- Check the [API Documentation](apidocumentation.md)
- Review the [Design Document](desgindocument.md)
- Contact: rashi.23fe10cse00411@muj.manipal.edu

---

**End of User Guide**
