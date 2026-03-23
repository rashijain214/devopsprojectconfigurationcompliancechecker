# Design Document - Configuration Compliance Checker

**Project:** Configuration Compliance Checker  
**Version:** 1.0.0  
**Author:** Rashi Jain  
**Date:** March 2026

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
+------------------+     +------------------+     +------------------+
|   Input Files    | --> |  Parser Engine   | --> |  Policy Checker  |
|                  |     |                  |     |                  |
| - Dockerfile     |     | - Dockerfile     |     | - Rule Engine    |
| - docker-compose |     | - DockerCompose  |     | - Violation      |
| - Kubernetes     |     | - Kubernetes     |     |   Detection      |
| - Jenkinsfile    |     | - Jenkinsfile    |     |                  |
+------------------+     +------------------+     +------------------+
                                                          |
                                                          v
+------------------+     +------------------+     +------------------+
|  Report Output   | <-- | Report Generator | <-- |  Check Results   |
|                  |     |                  |     |                  |
| - CLI (text)     |     | - JSON           |     | - Violations     |
| - JSON           |     | - Summary        |     | - Passed Rules   |
| - Dashboard      |     | - Statistics     |     |                  |
+------------------+     +------------------+     +------------------+
```

### 1.2 Design Principles

1. **Modularity** - Each file type has its own checker class
2. **Extensibility** - Easy to add new policy rules
3. **CI/CD Native** - Exit codes for pipeline integration
4. **Actionable** - Every violation includes remediation hints

---

## 2. Core Components

### 2.1 Data Classes

```python
@dataclass
class Violation:
    rule_id: str        # Unique identifier (e.g., "DF001")
    severity: Severity  # CRITICAL/HIGH/MEDIUM/LOW/INFO
    file: str           # File path
    line: Optional[int] # Line number (if applicable)
    message: str        # Human-readable description
    remediation: str    # Fix suggestion

@dataclass
class CheckResult:
    file: str           # File path
    file_type: str      # Type of file checked
    violations: List[Violation]
    passed: List[str]   # Rules that passed
```

### 2.2 Checker Classes

| Class | File Type | Rules |
|-------|-----------|-------|
| `DockerfileChecker` | Dockerfile | DF001-DF005 |
| `DockerComposeChecker` | docker-compose.yml | DC001-DC003 |
| `KubernetesChecker` | K8s YAML | K8S001-K8S004 |
| `JenkinsfileChecker` | Jenkinsfile | JK001-JK004 |

### 2.3 Severity Levels

```python
class Severity(Enum):
    CRITICAL = "CRITICAL"  # Blocks deployment
    HIGH     = "HIGH"      # Should be fixed
    MEDIUM   = "MEDIUM"    # Recommended fix
    LOW      = "LOW"       # Nice to have
    INFO     = "INFO"      # Informational
```

---

## 3. Policy Rules Specification

### 3.1 Dockerfile Rules (DF)

| ID | Severity | Check | Regex/Logic |
|----|----------|-------|-------------|
| DF001 | HIGH | No `:latest` tag | `FROM\s+\S+:latest` |
| DF002 | MEDIUM | HEALTHCHECK present | `HEALTHCHECK in content` |
| DF003 | CRITICAL | Non-root USER | `USER\s+(?!root)` |
| DF004 | LOW | EXPOSE instruction | `EXPOSE in content` |
| DF005 | LOW | LABEL metadata | `LABEL in content` |

### 3.2 Docker Compose Rules (DC)

| ID | Severity | Check | Logic |
|----|----------|-------|-------|
| DC001 | CRITICAL | No hardcoded passwords | Regex on environment vars |
| DC002 | MEDIUM | Restart policy defined | `restart in service` |
| DC003 | HIGH | Image pinned to version | `image` without `:latest` |

### 3.3 Kubernetes Rules (K8S)

| ID | Severity | Check | Path |
|----|----------|-------|------|
| K8S001 | HIGH | Resource limits | `spec.template.spec.containers[].resources.limits` |
| K8S002 | MEDIUM | Liveness probe | `spec.template.spec.containers[].livenessProbe` |
| K8S003 | MEDIUM | Readiness probe | `spec.template.spec.containers[].readinessProbe` |
| K8S004 | CRITICAL | No privileged mode | `securityContext.privileged != true` |

### 3.4 Jenkinsfile Rules (JK)

| ID | Severity | Check | Regex/Logic |
|----|----------|-------|-------------|
| JK001 | HIGH | Test stage present | `stage\s*\(\s*['"]Test` |
| JK002 | MEDIUM | Failure notification | `failure in content` |
| JK003 | CRITICAL | No hardcoded credentials | `password\s*=\s*["']` |
| JK004 | MEDIUM | Security scan stage | `stage\s*\(\s*['"]Security` |

---

## 4. Web Dashboard Architecture

### 4.1 Flask Application (`app.py`)

```
+-------------+     +----------------+     +------------------+
|   Routes    |     |   Compliance   |     |   Dashboard      |
|             | --> |    Checker     | --> |     View         |
| /           |     |   Subprocess   |     |  (dashboard.html)|
| /api/compliance |  |                |     |                  |
| /api/health |     |                |     |                  |
+-------------+     +----------------+     +------------------+
```

### 4.2 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve dashboard HTML |
| `/api/compliance` | GET | Real-time compliance data |
| `/api/health` | GET | Health check |

---

## 5. Testing Strategy

### 5.1 Test Structure

```
tests/
├── unit/
│   ├── test_dockerfile_checker.py
│   ├── test_compose_checker.py
│   ├── test_kubernetes_checker.py
│   └── test_jenkinsfile_checker.py
└── integration/
    └── test_compliance_runner.py
```

### 5.2 Test Coverage Requirements

- Minimum 80% code coverage
- All severity levels tested
- Edge cases for YAML parsing
- CI/CD exit code verification

---

## 6. CI/CD Integration Design

### 6.1 Pipeline Gate

```
+----------------+     +----------------+     +----------------+
|  Build Step    | --> | Compliance     | --> | Deploy?        |
|                |     | Check          |     |                |
|                |     |                |     | Exit 0: YES    |
|                |     |                |     | Exit 1: NO     |
+----------------+     +----------------+     +----------------+
```

### 6.2 Self-Checking

The project runs its own compliance checker on its infrastructure files during CI/CD to demonstrate the tool's effectiveness.

---

## 7. Error Handling

### 7.1 Exception Scenarios

| Scenario | Handling |
|----------|----------|
| File not found | Log warning, skip file |
| YAML parse error | Return CRITICAL violation |
| Invalid file type | Log warning, skip file |
| Empty file | No violations (compliant) |

### 7.2 Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All files compliant |
| 1 | Critical violations found |

---

## 8. Future Design Considerations

1. **Plugin Architecture** - Load checkers dynamically
2. **Rule Configuration** - External YAML/JSON for custom rules
3. **Caching** - Cache parsed results for large repositories
4. **Parallel Processing** - Check multiple files concurrently
5. **SARIF Export** - Standard format for security tools

---

**Document Version:** 1.0  
**Last Updated:** March 2026
