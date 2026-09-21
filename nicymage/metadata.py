import json
import subprocess


class DockerError(Exception):
    pass


def get_image_metadata(image: str) -> dict:
    try:
        result = subprocess.run(
            ["docker", "inspect", image],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise DockerError("Docker is not installed or not on PATH")

    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "Cannot connect to the Docker daemon" in stderr:
            raise DockerError("Docker daemon is not running")
        if "No such object" in stderr:
            raise DockerError(f"Image not found locally: {image}")
        raise DockerError(f"docker inspect failed: {stderr}")

    data = json.loads(result.stdout)[0]

    return {
        "image": image,
        "digest": _extract_digest(data),
        "size": data.get("Size"),
        "base_layers": data.get("RootFS", {}).get("Layers", []),
    }


def _extract_digest(data):
    repo_digests = data.get("RepoDigests") or []
    if repo_digests:
        return repo_digests[0].split("@")[-1]
    return data.get("Id")
