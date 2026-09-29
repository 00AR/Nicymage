SEVERITY_WEIGHTS = {
    "CRITICAL": 40,
    "HIGH": 20,
    "MEDIUM": 8,
    "LOW": 2,
    "UNKNOWN": 1,
}

NO_FIX_MULTIPLIER = 1.5


def compute_risk_score(vulnerabilities: list) -> dict:
    total = 0.0
    for vuln in vulnerabilities:
        severity = (vuln.get("severity") or "UNKNOWN").upper()
        weight = SEVERITY_WEIGHTS.get(severity, SEVERITY_WEIGHTS["UNKNOWN"])
        if not vuln.get("fixed_version"):
            weight *= NO_FIX_MULTIPLIER
        total += weight

    score = min(round(total), 100)

    if score >= 67:
        verdict = "HIGH"
    elif score >= 34:
        verdict = "MEDIUM"
    else:
        verdict = "LOW"

    return {"score": score, "verdict": verdict}
