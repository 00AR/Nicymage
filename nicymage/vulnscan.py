import json
import subprocess


class TrivyError(Exception):
    pass


def scan_vulnerabilities(image: str) -> list:
    try:
        result = subprocess.run(
            ["trivy", "image", image, "-f", "json"],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise TrivyError("Trivy is not installed or not on PATH")

    if result.returncode != 0:
        raise TrivyError(f"trivy failed: {result.stderr.strip()}")

    data = json.loads(result.stdout)

    vulnerabilities = []
    for target_result in data.get("Results", []) or []:
        for vuln in target_result.get("Vulnerabilities", []) or []:
            vulnerabilities.append({
                "package": vuln.get("PkgName"),
                "cve_id": vuln.get("VulnerabilityID"),
                "severity": vuln.get("Severity"),
                "fixed_version": vuln.get("FixedVersion"),
            })

    return vulnerabilities
