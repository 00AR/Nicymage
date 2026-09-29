import json
import subprocess


class SyftError(Exception):
    pass


def generate_sbom(image: str) -> list:
    try:
        result = subprocess.run(
            ["syft", image, "-o", "json"],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise SyftError("Syft is not installed or not on PATH")

    if result.returncode != 0:
        raise SyftError(f"syft failed: {result.stderr.strip()}")

    data = json.loads(result.stdout)

    return [
        {
            "name": artifact.get("name"),
            "version": artifact.get("version"),
            "type": artifact.get("type"),
        }
        for artifact in data.get("artifacts", [])
    ]
