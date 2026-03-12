import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional, Dict
from pydantic import BaseModel
from .utils import get_logger

logger = get_logger("detector")

class Stack(BaseModel):
    language: Optional[str] = None
    language_version: Optional[str] = None
    project_version: Optional[str] = "0.1.0"
    tests: Optional[str] = None
    container: bool = False
    infrastructure: Optional[str] = None
    cloud: Optional[str] = None
    has_api: bool = False
    api_spec_path: Optional[str] = None
    scripts: Dict[str, str] = {}
    security_tools: List[str] = []

def detect_stack(found_files: List[str], base_path: Path = Path(".")) -> Stack:
    """Detects the stack based on found files and their content with versioning."""
    stack = Stack()
    logger.info(f"Analyzing stack in {base_path}")

    # .Net
    csproj_files = list(base_path.glob("**/*.csproj"))
    if csproj_files or any(f.endswith(".sln") for f in found_files):
        stack.language = "C#"
        stack.tests = "dotnet test"
        if csproj_files:
            try:
                tree = ET.parse(csproj_files[0])
                root = tree.getroot()
                version = root.find(".//Version")
                if version is not None:
                    stack.project_version = version.text

                target_framework = root.find(".//TargetFramework")
                if target_framework is not None:
                    raw_tf = target_framework.text
                    # convert net9.0 or netcoreapp3.1 to 9.0 or 3.1
                    version_match = re.search(r"(\d+\.\d+)", raw_tf)
                    if version_match:
                        stack.language_version = version_match.group(1)
                    else:
                        stack.language_version = raw_tf
            except Exception as e:
                logger.warning(f"Failed to parse .csproj: {e}")

    # Node
    elif "package.json" in found_files:
        stack.language = "Node.js"
        try:
            with open(base_path / "package.json", "r") as f:
                pkg_data = json.load(f)
                stack.project_version = pkg_data.get("version", "0.1.0")
                engines = pkg_data.get("engines", {})
                if "node" in engines:
                    stack.language_version = engines.get("node").strip()

                stack.scripts = pkg_data.get("scripts", {})
                all_deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}

                if "jest" in all_deps: stack.tests = "Jest"
                elif "mocha" in all_deps: stack.tests = "Mocha"

                if "snyk" in all_deps: stack.security_tools.append("Snyk")
        except Exception as e:
            logger.error(f"Failed to parse package.json: {e}")

    # Python/MicroPython
    elif "requirements.txt" in found_files or "setup.py" in found_files or "main.py" in found_files or "boot.py" in found_files:
        stack.language = "Python"
        if "boot.py" in found_files or "main.py" in found_files:
            logger.info("MicroPython/Generic Python project detected.")
            stack.tests = "pytest"

        if "setup.py" in found_files:
            try:
                content = (base_path / "setup.py").read_text()
                version_match = re.search(r"version\s*=\s*['\"]([^'\"]+)['\"]", content)
                if version_match:
                    stack.project_version = version_match.group(1)
            except Exception: pass

        try:
            if (base_path / "requirements.txt").exists():
                content = (base_path / "requirements.txt").read_text().lower()
                if "pytest" in content: stack.tests = "Pytest"
                if "bandit" in content: stack.security_tools.append("Bandit")

            if (base_path / ".python-version").exists():
                stack.language_version = (base_path / ".python-version").read_text().strip()
        except Exception: pass

    # Makefile
    if "Makefile" in found_files and not stack.language:
        stack.language = "C/C++ or Makefile based"
        stack.infrastructure = "Makefile"

    # API Detection OpenAPI/Swagger
    api_specs = list(base_path.glob("**/swagger.json")) + \
                list(base_path.glob("**/openapi.json")) + \
                list(base_path.glob("**/openapi.yaml")) + \
                list(base_path.glob("**/openapi.yml"))

    if api_specs:
        stack.has_api = True
        stack.api_spec_path = str(api_specs[0].relative_to(base_path))
        logger.info(f"API Specification found at: {stack.api_spec_path}")

    # Docker-
    if "Dockerfile" in found_files:
        stack.container = True
        try:
            content = (base_path / "Dockerfile").read_text()
            match = re.search(r"^FROM\s+[\w\./-]+:([^\s\n\r]+)", content, re.MULTILINE)
            if match and not stack.language_version:
                stack.language_version = match.group(1).strip()
        except Exception: pass

    # Infrastructure
    if "terraform" in found_files or any(f.endswith(".tf") for f in found_files):
        stack.infrastructure = "Terraform"
        # Scan provider
        for tf_file in base_path.glob("**/*.tf"):
            try:
                content = tf_file.read_text()
                if 'provider "aws"' in content:
                    stack.cloud = "AWS"
                    break
                elif 'provider "google"' in content:
                    stack.cloud = "GCP"
                    break
                elif 'provider "azurerm"' in content:
                    stack.cloud = "Azure"
                    break
            except Exception: pass

    logger.info(f"Detected Stack: {stack.model_dump()}")
    return stack

