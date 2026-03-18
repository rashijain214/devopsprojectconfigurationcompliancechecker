"""
Configuration Compliance Checker
CSE3253 DevOps Project
Checks infrastructure configs against defined policies.
"""

import os
import re
import json
import yaml
import argparse
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH     = "HIGH"
    MEDIUM   = "MEDIUM"
    LOW      = "LOW"
    INFO     = "INFO"


@dataclass
class Violation:
    rule_id:     str
    severity:    Severity
    file:        str
    line:        Optional[int]
    message:     str
    remediation: str


@dataclass
class CheckResult:
    file:       str
    file_type:  str
    violations: List[Violation] = field(default_factory=list)
    passed:     List[str]       = field(default_factory=list)

    @property
    def is_compliant(self) -> bool:
        return len(self.violations) == 0

    @property
    def critical_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == Severity.CRITICAL)


# ─── Policy Rules ──────────────────────────────────────────────────────────────

class DockerfileChecker:
    FILE_TYPE = "Dockerfile"

    def check(self, filepath: str) -> CheckResult:
        result = CheckResult(file=filepath, file_type=self.FILE_TYPE)
        try:
            with open(filepath) as f:
                lines = f.readlines()
        except FileNotFoundError:
            return result

        content = "".join(lines)

        # DF001 – No 'latest' tag on FROM
        for i, line in enumerate(lines, 1):
            if re.match(r'^\s*FROM\s+\S+:latest', line, re.IGNORECASE):
                result.violations.append(Violation(
                    rule_id="DF001", severity=Severity.HIGH,
                    file=filepath, line=i,
                    message=f"Line {i}: FROM uses ':latest' tag — non-deterministic builds.",
                    remediation="Pin to a specific image version e.g. `FROM python:3.11-slim`"
                ))
            elif re.match(r'^\s*FROM\s+', line, re.IGNORECASE):
                result.passed.append("DF001: FROM uses a pinned tag")

        # DF002 – Must have HEALTHCHECK
        if "HEALTHCHECK" not in content:
            result.violations.append(Violation(
                rule_id="DF002", severity=Severity.MEDIUM,
                file=filepath, line=None,
                message="No HEALTHCHECK instruction found.",
                remediation="Add: HEALTHCHECK CMD curl -f http://localhost:8080/health || exit 1"
            ))
        else:
            result.passed.append("DF002: HEALTHCHECK present")

        # DF003 – Must not run as root (USER instruction)
        if not re.search(r'^\s*USER\s+(?!root)', content, re.MULTILINE):
            result.violations.append(Violation(
                rule_id="DF003", severity=Severity.CRITICAL,
                file=filepath, line=None,
                message="Container may run as root — no non-root USER set.",
                remediation="Add: RUN adduser --disabled-password appuser && USER appuser"
            ))
        else:
            result.passed.append("DF003: Non-root USER configured")

        # DF004 – Must expose a port
        if "EXPOSE" not in content:
            result.violations.append(Violation(
                rule_id="DF004", severity=Severity.LOW,
                file=filepath, line=None,
                message="No EXPOSE instruction found.",
                remediation="Add: EXPOSE 8080 (or your application port)"
            ))
        else:
            result.passed.append("DF004: EXPOSE present")

        # DF005 – Must have a LABEL for maintainer/version
        if "LABEL" not in content:
            result.violations.append(Violation(
                rule_id="DF005", severity=Severity.LOW,
                file=filepath, line=None,
                message="No LABEL metadata found.",
                remediation='Add: LABEL maintainer="you@example.com" version="1.0"'
            ))
        else:
            result.passed.append("DF005: LABEL metadata present")

        return result


class DockerComposeChecker:
    FILE_TYPE = "docker-compose"

    def check(self, filepath: str) -> CheckResult:
        result = CheckResult(file=filepath, file_type=self.FILE_TYPE)
        try:
            with open(filepath) as f:
                data = yaml.safe_load(f)
        except Exception as e:
            result.violations.append(Violation(
                rule_id="DC000", severity=Severity.CRITICAL,
                file=filepath, line=None,
                message=f"Failed to parse YAML: {e}",
                remediation="Fix YAML syntax errors."
            ))
            return result

        services = data.get("services", {})

        for svc_name, svc in services.items():
            # DC001 – No hardcoded passwords in environment
            env_list = svc.get("environment", [])
            if isinstance(env_list, list):
                for item in env_list:
                    if isinstance(item, str) and re.search(r'PASSWORD\s*=\s*\S+', item, re.IGNORECASE):
                        result.violations.append(Violation(
                            rule_id="DC001", severity=Severity.CRITICAL,
                            file=filepath, line=None,
                            message=f"Service '{svc_name}': Hardcoded password in environment.",
                            remediation="Use Docker secrets or .env file: PASSWORD=${MY_PASSWORD}"
                        ))
            elif isinstance(env_list, dict):
                for k, v in env_list.items():
                    if "PASSWORD" in k.upper() and v and str(v) not in ("", "${" + k + "}"):
                        result.violations.append(Violation(
                            rule_id="DC001", severity=Severity.CRITICAL,
                            file=filepath, line=None,
                            message=f"Service '{svc_name}': Hardcoded password for key '{k}'.",
                            remediation=f"Use: {k}: ${{{k}}}"
                        ))

            # DC002 – restart policy required
            if "restart" not in svc:
                result.violations.append(Violation(
                    rule_id="DC002", severity=Severity.MEDIUM,
                    file=filepath, line=None,
                    message=f"Service '{svc_name}': No 'restart' policy defined.",
                    remediation=f"Add under '{svc_name}': restart: unless-stopped"
                ))
            else:
                result.passed.append(f"DC002: '{svc_name}' has restart policy")

            # DC003 – no 'latest' image tag
            image = svc.get("image", "")
            if image.endswith(":latest") or (image and ":" not in image):
                result.violations.append(Violation(
                    rule_id="DC003", severity=Severity.HIGH,
                    file=filepath, line=None,
                    message=f"Service '{svc_name}': Image '{image}' uses latest/unpinned tag.",
                    remediation=f"Pin the image version e.g. image: {image.split(':')[0]}:1.2.3"
                ))
            elif image:
                result.passed.append(f"DC003: '{svc_name}' image is pinned")

        return result


class KubernetesChecker:
    FILE_TYPE = "Kubernetes"

    def check(self, filepath: str) -> CheckResult:
        result = CheckResult(file=filepath, file_type=self.FILE_TYPE)
        try:
            with open(filepath) as f:
                docs = list(yaml.safe_load_all(f))
        except Exception as e:
            result.violations.append(Violation(
                rule_id="K8S000", severity=Severity.CRITICAL,
                file=filepath, line=None,
                message=f"Failed to parse YAML: {e}",
                remediation="Fix YAML syntax errors."
            ))
            return result

        for doc in docs:
            if not doc:
                continue
            kind = doc.get("kind", "")
            name = doc.get("metadata", {}).get("name", "unknown")

            if kind in ("Deployment", "StatefulSet", "DaemonSet"):
                containers = (
                    doc.get("spec", {})
                       .get("template", {})
                       .get("spec", {})
                       .get("containers", [])
                )
                for c in containers:
                    cname = c.get("name", "?")

                    # K8S001 – Resource limits
                    resources = c.get("resources", {})
                    if not resources.get("limits"):
                        result.violations.append(Violation(
                            rule_id="K8S001", severity=Severity.HIGH,
                            file=filepath, line=None,
                            message=f"{kind}/{name} container '{cname}': No resource limits set.",
                            remediation="Add resources.limits: {cpu: '500m', memory: '256Mi'}"
                        ))
                    else:
                        result.passed.append(f"K8S001: {kind}/{name}/{cname} has resource limits")

                    # K8S002 – Liveness probe
                    if not c.get("livenessProbe"):
                        result.violations.append(Violation(
                            rule_id="K8S002", severity=Severity.MEDIUM,
                            file=filepath, line=None,
                            message=f"{kind}/{name} container '{cname}': No livenessProbe defined.",
                            remediation="Add livenessProbe with httpGet or tcpSocket."
                        ))
                    else:
                        result.passed.append(f"K8S002: {kind}/{name}/{cname} has livenessProbe")

                    # K8S003 – Readiness probe
                    if not c.get("readinessProbe"):
                        result.violations.append(Violation(
                            rule_id="K8S003", severity=Severity.MEDIUM,
                            file=filepath, line=None,
                            message=f"{kind}/{name} container '{cname}': No readinessProbe defined.",
                            remediation="Add readinessProbe with httpGet or tcpSocket."
                        ))
                    else:
                        result.passed.append(f"K8S003: {kind}/{name}/{cname} has readinessProbe")

                    # K8S004 – No privileged containers
                    sec = c.get("securityContext", {})
                    if sec.get("privileged") is True:
                        result.violations.append(Violation(
                            rule_id="K8S004", severity=Severity.CRITICAL,
                            file=filepath, line=None,
                            message=f"{kind}/{name} container '{cname}': Running as privileged!",
                            remediation="Set securityContext.privileged: false"
                        ))
                    else:
                        result.passed.append(f"K8S004: {kind}/{name}/{cname} not privileged")

        return result


class JenkinsfileChecker:
    FILE_TYPE = "Jenkinsfile"

    def check(self, filepath: str) -> CheckResult:
        result = CheckResult(file=filepath, file_type=self.FILE_TYPE)
        try:
            with open(filepath) as f:
                content = f.read()
        except FileNotFoundError:
            return result

        # JK001 – Must have a 'Test' stage
        if not re.search(r"stage\s*\(\s*['\"]Test", content, re.IGNORECASE):
            result.violations.append(Violation(
                rule_id="JK001", severity=Severity.HIGH,
                file=filepath, line=None,
                message="No 'Test' stage found in pipeline.",
                remediation="Add: stage('Test') { steps { sh 'npm test' } }"
            ))
        else:
            result.passed.append("JK001: Test stage present")

        # JK002 – Must have post failure notification
        if "failure" not in content:
            result.violations.append(Violation(
                rule_id="JK002", severity=Severity.MEDIUM,
                file=filepath, line=None,
                message="No failure notification in 'post' block.",
                remediation="Add post { failure { emailext(...) } } block."
            ))
        else:
            result.passed.append("JK002: Failure notification configured")

        # JK003 – Must not hardcode credentials
        if re.search(r'password\s*=\s*["\'][^"\'${}]+["\']', content, re.IGNORECASE):
            result.violations.append(Violation(
                rule_id="JK003", severity=Severity.CRITICAL,
                file=filepath, line=None,
                message="Possible hardcoded credential found in Jenkinsfile.",
                remediation="Use Jenkins credentials: withCredentials([usernamePassword(...)])"
            ))
        else:
            result.passed.append("JK003: No hardcoded credentials detected")

        # JK004 – Should have a Security Scan stage
        if not re.search(r"stage\s*\(\s*['\"]Security", content, re.IGNORECASE):
            result.violations.append(Violation(
                rule_id="JK004", severity=Severity.MEDIUM,
                file=filepath, line=None,
                message="No 'Security Scan' stage found.",
                remediation="Add a Trivy/Snyk scan stage after build."
            ))
        else:
            result.passed.append("JK004: Security Scan stage present")

        return result


# ─── Runner ────────────────────────────────────────────────────────────────────

class ComplianceRunner:
    CHECKERS = {
        "Dockerfile":          DockerfileChecker(),
        "docker-compose.yml":  DockerComposeChecker(),
        "docker-compose.yaml": DockerComposeChecker(),
        "deployment.yaml":     KubernetesChecker(),
        "deployment.yml":      KubernetesChecker(),
        "service.yaml":        KubernetesChecker(),
        "Jenkinsfile":         JenkinsfileChecker(),
    }

    def run(self, paths: List[str]) -> List[CheckResult]:
        results = []
        for path in paths:
            basename = os.path.basename(path)
            checker = self.CHECKERS.get(basename)
            if checker:
                results.append(checker.check(path))
            else:
                print(f"[SKIP] No checker for: {basename}")
        return results

    def generate_report(self, results: List[CheckResult]) -> Dict[str, Any]:
        total_violations = sum(len(r.violations) for r in results)
        total_passed     = sum(len(r.passed) for r in results)
        critical_count   = sum(r.critical_count for r in results)

        report = {
            "summary": {
                "files_checked":     len(results),
                "total_violations":  total_violations,
                "total_passed":      total_passed,
                "critical":          critical_count,
                "overall_compliant": total_violations == 0,
            },
            "files": []
        }

        for r in results:
            report["files"].append({
                "file":       r.file,
                "type":       r.file_type,
                "compliant":  r.is_compliant,
                "violations": [
                    {
                        "rule_id":     v.rule_id,
                        "severity":    v.severity.value,
                        "line":        v.line,
                        "message":     v.message,
                        "remediation": v.remediation,
                    }
                    for v in r.violations
                ],
                "passed": r.passed,
            })

        return report


# ─── CLI ───────────────────────────────────────────────────────────────────────

def print_report(report: Dict[str, Any]) -> None:
    s = report["summary"]
    print("\n" + "="*60)
    print("  CONFIGURATION COMPLIANCE REPORT")
    print("="*60)
    print(f"  Files Checked   : {s['files_checked']}")
    print(f"  Rules Passed    : {s['total_passed']}")
    print(f"  Violations      : {s['total_violations']}")
    print(f"  Critical Issues : {s['critical']}")
    status = "COMPLIANT" if s["overall_compliant"] else "NON-COMPLIANT"
    print(f"  Status          : {status}")
    print("="*60)

    for f in report["files"]:
        icon = "OK" if f["compliant"] else "FAIL"
        print(f"\n[{icon}] [{f['type']}] {f['file']}")
        for v in f["violations"]:
            line_info = f" (line {v['line']})" if v["line"] else ""
            print(f"   [{v['severity']}] {v['rule_id']}{line_info}: {v['message']}")
            print(f"         Fix: {v['remediation']}")
        for p in f["passed"]:
            print(f"   [PASS] {p}")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configuration Compliance Checker")
    parser.add_argument("files", nargs="+", help="Files to check")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--output", help="Write JSON report to file")
    args = parser.parse_args()

    runner  = ComplianceRunner()
    results = runner.run(args.files)
    report  = runner.generate_report(results)

    if args.json or args.output:
        json_out = json.dumps(report, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(json_out)
            print(f"Report written to {args.output}")
        else:
            print(json_out)
    else:
        print_report(report)

    if report["summary"]["critical"] > 0:
        exit(1)