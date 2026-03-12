import os
from pathlib import Path
from typing import List

def scan_repo(directory: str = ".") -> List[str]:
    """Scans the directory for common files and folders."""
    common_files = [
        "package.json",
        "requirements.txt",
        "setup.py",
        "pyproject.toml",
        "main.py",
        "boot.py",
        "Makefile",
        "go.mod",
        "pom.xml",
        "Dockerfile",
        "terraform",
        "swagger.json",
        "openapi.json",
        "openapi.yaml",
        "openapi.yml"
    ]

    # .csproj e .sln
    found_files = []
    path = Path(directory)

    for item in common_files:
        if (path / item).exists():
            found_files.append(item)

    for file in path.glob("*.csproj"):
        found_files.append(file.name)
    for file in path.glob("*.sln"):
        found_files.append(file.name)

    return found_files
