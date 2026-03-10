import os
from pathlib import Path
from typing import List

def scan_repo(directory: str = ".") -> List[str]:
    """Scans the directory for common files and folders."""
    common_files = [
        "package.json",
        "requirements.txt",
        "go.mod",
        "pom.xml",
        "Dockerfile",
        "terraform",
        "k8s",
        "helm"
    ]
    
    found_files = []
    path = Path(directory)
    
    for item in common_files:
        if (path / item).exists():
            found_files.append(item)
            
    return found_files
