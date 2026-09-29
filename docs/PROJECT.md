# Nicymage

A local-first, AI-assisted container image security auditor. Point it at a Docker image and it tells you whether to trust it — SBOM, known vulnerabilities, and a risk score, with everything running on your own machine. No cloud, no registry, no paid API required to get value out of it.

## MVP scope (V1)

```
nicymage scan <image>
```

Pipeline:
1. Pull image metadata (digest, size, base image) via Docker
2. Generate an SBOM via Syft
3. Scan the SBOM for known CVEs via Trivy
4. Compute a risk score from a heuristic (severity × whether a fix is available)
5. Print a terminal report (packages found, vuln counts by severity, score, verdict), with a non-zero exit code on a HIGH verdict

Language: Python. Storage: none (stateless, single scan in/out) — history comes in V2.

### Out of scope for V1
- AI-generated analysis/remediation (heuristic score only)
- Grype cross-check
- Dependency graph correlation (direct vs. transitive)
- Secret scanning (Gitleaks)
- Image signing (Cosign)
- Any Kubernetes or cloud integration

## Roadmap (post-MVP)

- **V2 — Supply-chain depth**: Grype cross-check, dependency graph correlation, Gitleaks secret detection, Cosign signing/verification, local scan history (SQLite) with diffing between scans of the same image.
- **V3 — AI + DX**: swap the heuristic score for real AI analysis (local via Ollama, or pluggable to a hosted API) that explains why a finding matters and suggests remediation. Wrap the core in a FastAPI REST API + simple web UI + GitHub Action for CI use.
- **V4 — Local Kubernetes** (optional): run against a `kind` cluster, gate deploys with Kyverno, add Falco for runtime detection.
- **V5 — Optional cloud demo**: point it at a real registry (ECR/GCR/OCI) — only if useful for a portfolio demo, not required for the tool to work.

See #1 for the original discussion and any scope changes since this was written.
