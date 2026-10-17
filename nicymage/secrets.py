import json
import os
import shutil
import subprocess
import tempfile

from .metadata import DockerError


class GitleaksError(Exception):
    pass


def _export_image_filesystem(image: str, dest_dir: str) -> None:
    try:
        create = subprocess.run(["docker", "create", image], capture_output=True, text=True)
    except FileNotFoundError:
        raise DockerError("Docker is not installed or not on PATH")

    if create.returncode != 0:
        raise DockerError(f"failed to create container for {image}: {create.stderr.strip()}")

    container_id = create.stdout.strip()
    try:
        export = subprocess.run(["docker", "export", container_id], capture_output=True)
        if export.returncode != 0:
            raise DockerError(f"failed to export container filesystem: {export.stderr.decode().strip()}")

        tar_path = os.path.join(dest_dir, "image.tar")
        with open(tar_path, "wb") as tar_file:
            tar_file.write(export.stdout)

        shutil.unpack_archive(tar_path, dest_dir, format="tar")
        os.remove(tar_path)
    finally:
        subprocess.run(["docker", "rm", "-f", container_id], capture_output=True)


def scan_secrets(image: str) -> list:
    with tempfile.TemporaryDirectory() as fs_dir:
        _export_image_filesystem(image, fs_dir)

        report_fd, report_path = tempfile.mkstemp(suffix=".json")
        os.close(report_fd)
        try:
            try:
                result = subprocess.run(
                    ["gitleaks", "detect", "--source", fs_dir, "--no-git", "-f", "json", "-r", report_path, "--exit-code", "0"],
                    capture_output=True,
                    text=True,
                )
            except FileNotFoundError:
                raise GitleaksError("Gitleaks is not installed or not on PATH")

            if result.returncode != 0:
                raise GitleaksError(f"gitleaks failed: {result.stderr.strip()}")

            with open(report_path) as f:
                content = f.read().strip()
                raw_findings = json.loads(content) if content else []
        finally:
            os.remove(report_path)

    return [
        {
            "file": finding.get("File"),
            "secret_type": finding.get("RuleID"),
            "line": finding.get("StartLine"),
        }
        for finding in raw_findings
    ]
