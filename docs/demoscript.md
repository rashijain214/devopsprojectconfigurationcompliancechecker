# Demo Script - Configuration Compliance Checker

**Version:** 1.0.0  
**Last Updated:** March 2026

---

## Demo Overview

This demo script demonstrates the Configuration Compliance Checker tool's capabilities across different infrastructure-as-code file types.

---

## Demo Setup

### 1. Environment Preparation

```bash
# Clone and setup
git clone https://github.com/rashijain214/devopsprojectcompliancechecker.git
cd devopsprojectcompliancechecker
pip install -r requirements.txt

# Verify installation
python src/main/python/compliance_checker.py --help
```

### 2. Demo Files Location

All demo files are in the `test_violations/` directory:
- `Dockerfile` - Contains common violations
- `docker-compose.yml` - Multi-container setup with issues
- `deployment.yaml` - Kubernetes manifest with security problems

---

## Demo Script

### Part 1: Individual File Checks

#### Dockerfile Demo

```bash
echo "=== Dockerfile Compliance Check ==="
python src/main/python/compliance_checker.py test_violations/Dockerfile
```

**Expected Output:** Shows violations for latest tag, missing healthcheck, root user

#### Docker Compose Demo

```bash
echo "=== Docker Compose Compliance Check ==="
python src/main/python/compliance_checker.py test_violations/docker-compose.yml
```

**Expected Output:** Shows hardcoded passwords, missing restart policy, unpinned images

#### Kubernetes Demo

```bash
echo "=== Kubernetes Compliance Check ==="
python src/main/python/compliance_checker.py test_violations/deployment.yaml
```

**Expected Output:** Shows missing resource limits, probes, privileged containers

---

### Part 2: Multi-File Check

```bash
echo "=== Multi-File Compliance Check ==="
python src/main/python/compliance_checker.py \
  test_violations/Dockerfile \
  test_violations/docker-compose.yml \
  test_violations/deployment.yaml
```

**Expected Output:** Comprehensive report with all violations and summary

---

### Part 3: JSON Output

```bash
echo "=== JSON Format Output ==="
python src/main/python/compliance_checker.py \
  test_violations/Dockerfile \
  --json | jq .
```

**Expected Output:** Structured JSON with violations, passed rules, and metadata

---

### Part 4: CI/CD Integration Demo

```bash
echo "=== CI/CD Exit Code Demo ==="
python src/main/python/compliance_checker.py test_violations/Dockerfile
echo "Exit code: $?"
```

**Expected Output:** Exit code 1 (critical violations found)

---

### Part 5: Web Dashboard Demo

```bash
# Start dashboard (in new terminal)
echo "=== Starting Web Dashboard ==="
python src/main/python/app.py

# In another terminal, test API
curl http://localhost:5000/api/compliance | jq .
```

**Expected Output:** Real-time compliance data in JSON format

---

## Key Talking Points

### 1. Security Focus
- "The tool flags CRITICAL violations like running as root and hardcoded passwords"
- "Each violation includes actionable remediation steps"

### 2. CI/CD Integration
- "Exit code 1 blocks deployments with critical issues"
- "Self-checking: The project validates its own infrastructure"

### 3. Multi-Format Support
- "Single tool covers Docker, Docker Compose, Kubernetes, and Jenkins"
- "Consistent violation format across all file types"

### 4. Reporting Capabilities
- "Human-readable reports for developers"
- "JSON output for automation and dashboards"
- "Web dashboard for real-time monitoring"

---

## Demo Flow Summary

1. **Setup** - Install and verify tool
2. **Individual Checks** - Show each file type
3. **Multi-File** - Demonstrate comprehensive checking
4. **JSON Output** - Show machine-readable format
5. **CI/CD Integration** - Demonstrate exit codes
6. **Web Dashboard** - Show real-time monitoring

---

## Common Demo Questions

### Q: How does this compare to existing tools?
A: "Lightweight, focused on DevOps basics, easy to extend, CI/CD native"

### Q: Can we add custom rules?
A: "Yes, the modular design allows adding new rules and file types"

### Q: What about false positives?
A: "Rules are carefully tuned to avoid flagging variable references"

### Q: How to integrate with existing pipelines?
A: "Simple CLI with exit codes, JSON output, and webhook support"

---

**Demo Duration:** 15-20 minutes
**Target Audience:** DevOps engineers, security teams, developers
