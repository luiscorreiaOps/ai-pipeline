import json
import re
from pathlib import Path
from typing import List, Optional, Dict
from pydantic import BaseModel
from .utils import get_logger

logger = get_logger("detector")

class Stack(BaseModel):
    language: Optional[str] = None
    language_version: Optional[str] = None
    tests: Optional[str] = None
    container: bool = False
    infrastructure: Optional[str] = None
    cloud: Optional[str] = None
    scripts: Dict[str, str] = {}
    security_tools: List[str] = []

def detect_stack(found_files: List[str], base_path: Path = Path(".")) -> Stack:
    """Detects the stack based on found files and their content with versioning."""
    stack = Stack()
    logger.info(f"Analyzing stack in {base_path} for files: {found_files}")

    # Language Detection Node
    if "package.json" in found_files:
        stack.language = "Node.js"
        try:
            with open(base_path / "package.json", "r") as f:
                pkg_data = json.load(f)

                engines = pkg_data.get("engines", {})
                if "node" in engines:
                    stack.language_version = engines.get("node").strip()

                stack.scripts = pkg_data.get("scripts", {})

                # Tests & Security)
                all_deps = {}
                all_deps.update(pkg_data.get("dependencies", {}))
                all_deps.update(pkg_data.get("devDependencies", {}))
                all_deps.update(pkg_data.get("peerDependencies", {}))

                logger.info(f"Checking dependencies: {list(all_deps.keys())}")

                if "jest" in all_deps: stack.tests = "Jest"
                elif "mocha" in all_deps: stack.tests = "Mocha"

                if "snyk" in all_deps:
                    stack.security_tools.append("Snyk")
                if "trivy" in all_deps:
                    stack.security_tools.append("Trivy")

                # Check scripts for security tools too
                scripts_str = json.dumps(stack.scripts).lower()
                if "snyk" in scripts_str and "Snyk" not in stack.security_tools:
                    stack.security_tools.append("Snyk")

        except Exception as e:
            logger.error(f"Failed to parse package.json: {e}")

    # Language Detection Python
    elif "requirements.txt" in found_files:
        stack.language = "Python"
        try:
            with open(base_path / "requirements.txt", "r") as f:
                content = f.read().lower()
                if "pytest" in content: stack.tests = "Pytest"
                if "bandit" in content: stack.security_tools.append("Bandit")

            if (base_path / ".python-version").exists():
                stack.language_version = (base_path / ".python-version").read_text().strip()
        except Exception as e:
            logger.error(f"Failed to parse python files: {e}")

    # Docker Detection
    if "Dockerfile" in found_files:
        stack.container = True
        try:
            content = (base_path / "Dockerfile").read_text()
            match = re.search(r"^FROM\s+[\w\./-]+:([^\s\n\r]+)", content, re.MULTILINE)
            if match and not stack.language_version:
                stack.language_version = match.group(1).strip()
        except Exception as e:
             logger.warning(f"Failed to read Dockerfile version: {e}")

    # Infrastructure Detection
    if "terraform" in found_files:
        stack.infrastructure = "Terraform"
        tf_dir = base_path / "terraform"
        if tf_dir.exists() and tf_dir.is_dir():
            try:
                for tf_file in tf_dir.glob("*.tf"):
                    with open(tf_file, "r") as f:
                        if 'provider "aws"' in f.read():
                            stack.cloud = "AWS"
                            break
            except Exception: pass

    logger.info(f"Detected Stack: {stack.dict()}")
    return stack
