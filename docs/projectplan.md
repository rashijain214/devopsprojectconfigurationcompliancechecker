# Project Plan - Configuration Compliance Checker

**Student:** Rashi Jain  
**Registration No:** 23FE10CSE00411  
**Course:** CSE3253 DevOps [PE6]  
**Semester:** VI (2025–2026)

---

## 1. Project Overview

### 1.1 Problem Statement
Infrastructure misconfigurations are one of the leading causes of security incidents and deployment failures. Teams often lack automated checks to enforce standards across Dockerfiles, Kubernetes manifests, and CI/CD pipelines.

### 1.2 Solution
A Python-based compliance checker tool that automatically scans infrastructure-as-code files against a defined policy ruleset and generates actionable compliance reports.

---

## 2. Objectives & Deliverables

| Phase | Objective | Deliverable | Status |
|-------|-----------|-------------|--------|
| 1 | Core Engine Development | Compliance checker with parsers for Dockerfile, docker-compose, K8s YAML, Jenkinsfile | Complete |
| 2 | Policy Implementation | 16 policy rules across all file types | Complete |
| 3 | Reporting & Output | JSON and human-readable report formats | Complete |
| 4 | CI/CD Integration | Exit codes for pipeline gates, self-checking capability | Complete |
| 5 | Web Dashboard | Flask-based real-time compliance dashboard | Complete |
| 6 | Testing & Documentation | Unit tests with >80% coverage, full documentation | Complete |

---

## 3. Timeline

| Week | Activities |
|------|------------|
| Week 1-2 | Research on compliance tools (Checkov, Trivy, kube-score), define policy rules |
| Week 3-4 | Implement core parser engine and Dockerfile checker |
| Week 5-6 | Implement Docker Compose, Kubernetes, and Jenkinsfile checkers |
| Week 7-8 | Build reporting engine and CLI interface |
| Week 9 | Develop Flask web dashboard |
| Week 10 | Write unit tests, achieve coverage targets |
| Week 11 | CI/CD pipeline setup (Jenkins + GitHub Actions) |
| Week 12 | Documentation and final presentation |

---

## 4. Resource Requirements

### 4.1 Software
- Python 3.11+
- Docker Desktop 20.10+
- Jenkins LTS
- Kubernetes cluster (local or cloud)
- Git 2.30+

### 4.2 Python Dependencies
```
pyyaml>=6.0
pytest>=7.0
pytest-cov>=4.0
pylint>=2.15
flask>=2.0
```

---

## 5. Risk Management

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| YAML parsing edge cases | Medium | High | Use `yaml.safe_load_all()` for multi-document support |
| False positives in password detection | Medium | Medium | Carefully tune regex patterns, test with real configs |
| Complex Jenkinsfile parsing | High | Medium | Focus on declarative pipeline syntax only |
| Time constraints | Low | High | Prioritize core features, add nice-to-haves if time permits |

---

## 6. Success Criteria

- [x] Parse and analyze all target file formats
- [x] Implement 16 policy rules with proper severity levels
- [x] Generate both JSON and human-readable reports
- [x] Exit code 1 on critical violations (CI/CD gate)
- [x] Test coverage >80%
- [x] Self-checking capability (project checks its own infrastructure)
- [x] Web dashboard for real-time compliance view

---

## 7. Future Enhancements

- Additional file support (Terraform HCL, Ansible playbooks)
- Custom policy rule definitions via YAML/JSON
- SARIF output format for GitHub Advanced Security integration
- Pre-commit hook support
- IDE extensions (VS Code, IntelliJ)

---

**Last Updated:** March 2026
