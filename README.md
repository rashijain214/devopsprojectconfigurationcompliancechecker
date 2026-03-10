# Configuration Compliance Checker

Student Name:   Rashi Jain 
Registration No: 23FE10CSE00411 
Course: CSE3253 DevOps [PE6]  
Semester: VI (2025–2026)  
Project Type: DevOps Tooling – Configuration Management  
Difficulty: Intermediate  

---

## Project Overview

### Problem Statement
Infrastructure misconfigurations are one of the leading causes of security incidents and deployment failures. Teams often lack automated checks to enforce standards across Dockerfiles, Kubernetes manifests, and CI/CD pipelines. This tool automatically scans infrastructure-as-code files against a defined policy ruleset and generates actionable compliance reports.

### Objectives
- [x] Parse and analyse Dockerfile, docker-compose, Kubernetes YAML, and Jenkinsfile
- [x] Enforce security and best-practice policies (e.g., no root user, resource limits, pinned images)
- [x] Generate JSON and human-readable compliance reports
- [x] Integrate as a CI/CD pipeline gate (fails build on critical violations)

### Key Features
- **Multi-format support**: Dockerfile, docker-compose.yml, Kubernetes YAML, Jenkinsfile
- **Severity levels**: CRITICAL / HIGH / MEDIUM / LOW
- **Remediation hints**: Every violation includes a fix suggestion
- **CI/CD native**: Exit code 1 on critical violations blocks bad deployments
- **Self-checking**: The project checks its own infrastructure on every pipeline run

---

## Technology Stack

| Category | Tool |
|---|---|
| Language | Python 3.11 |
| Testing | pytest + pytest-cov |
| Linting | pylint |
| Containerisation | Docker |
| Orchestration | Kubernetes |
| CI/CD | Jenkins + GitHub Actions |
| Config Parsing | PyYAML |

---

## Getting Started

### Prerequisites
- Python 3.8+
- Docker Desktop 20.10+
- Git 2.30+

### Installation

```bash
git clone https://github.com/rashijain214/devopsprojectcompliancechecker.git
cd devopsprojectcompliancechecker
pip install -r requirements.txt
```

### Run the Checker

```bash
# Check specific files
python src/main/python/compliance_checker.py \
  infrastructure/docker/Dockerfile \
  infrastructure/docker/docker-compose.yml \
  infrastructure/kubernetes/deployment.yaml \
  pipelines/Jenkinsfile

# Output as JSON
python src/main/python/compliance_checker.py infrastructure/docker/Dockerfile --json

# Save report to file
python src/main/python/compliance_checker.py infrastructure/docker/Dockerfile \
  --output reports/report.json
```

### Run with Docker

```bash
docker build -f infrastructure/docker/Dockerfile -t compliance-checker:1.0.0 .
docker run --rm \
  -v $(pwd)/infrastructure:/app/infrastructure \
  compliance-checker:1.0.0 \
  python src/main/python/compliance_checker.py infrastructure/docker/Dockerfile
```

---

## Policy Rules Reference

| Rule ID | File Type | Severity | Description |
|---|---|---|---|
| DF001 | Dockerfile | HIGH | FROM must not use `:latest` tag |
| DF002 | Dockerfile | MEDIUM | Must include HEALTHCHECK |
| DF003 | Dockerfile | CRITICAL | Must not run as root |
| DF004 | Dockerfile | LOW | Must have EXPOSE instruction |
| DF005 | Dockerfile | LOW | Must have LABEL metadata |
| DC001 | docker-compose | CRITICAL | No hardcoded passwords |
| DC002 | docker-compose | MEDIUM | Must define restart policy |
| DC003 | docker-compose | HIGH | Images must be pinned |
| K8S001 | Kubernetes | HIGH | Containers must have resource limits |
| K8S002 | Kubernetes | MEDIUM | Must define livenessProbe |
| K8S003 | Kubernetes | MEDIUM | Must define readinessProbe |
| K8S004 | Kubernetes | CRITICAL | No privileged containers |
| JK001 | Jenkinsfile | HIGH | Must have a Test stage |
| JK002 | Jenkinsfile | MEDIUM | Must have failure notification |
| JK003 | Jenkinsfile | CRITICAL | No hardcoded credentials |
| JK004 | Jenkinsfile | MEDIUM | Must have Security Scan stage |

---

## Testing

```bash
# Run all unit tests with coverage
pytest tests/unit/ -v --cov=src/main/python --cov-report=term-missing

# Expected: all tests pass, coverage > 80%
```

---

## CI/CD Pipeline

### Pipeline Stages
1. **Code Quality** – pylint static analysis
2. **Install Dependencies** – pip install
3. **Test** – pytest with coverage
4. **Self-Compliance Check** – checker runs on own infrastructure
5. **Build Docker Image** – build + tag
6. **Security Scan** – Trivy vulnerability scan
7. **Deploy to Staging/Production** – environment-gated deploy

The pipeline **exits with code 1** if any CRITICAL compliance violation is found, preventing deployment of non-compliant infrastructure.

---

## Performance Metrics

| Metric | Target | Current |
|---|---|---|
| Build Time | < 5 min | ~2 min |
| Test Coverage | > 80% | ~90% |
| Rules Implemented | 16 | 16 |

---

## Project Challenges

1. **YAML multi-document parsing** – Kubernetes files can contain multiple documents separated by `---`. Solved using `yaml.safe_load_all()`.
2. **Environment variable formats** – Docker Compose allows both list and dict formats for environment. Handled both cases in parser.
3. **False-positive suppression** – Regex for hardcoded passwords needed careful tuning to avoid flagging variable references like `${PASSWORD}`.

## Learnings
- Infrastructure as Code has distinct policy requirements per file type
- Exit codes are the key integration mechanism for CI/CD pipeline gates
- PyYAML's `safe_load_all` is essential for multi-document K8s manifests

---

## Acknowledgments
- Course Instructor: Mr. Dibakar Sinha
- Open-source reference: Checkov, Trivy, kube-score

## Contact
Student: Rashi Jain
Email:rashi.23fe10cse00411@muj.manipal.edu
Course Coordinator: Mr. Jay Shankar Sharma — Thursday & Friday, 5–6 PM, LHC 308F
