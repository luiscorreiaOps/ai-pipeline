from ai_pipeline.detector import detect_stack, Stack
from ai_pipeline.scanner import scan_repo
import pytest
from pathlib import Path

def test_detect_node_stack(tmp_path):
    #mock files
    (tmp_path / "package.json").write_text('{"dependencies": {"react": "18.0.0"}, "devDependencies": {"jest": "^29.0.0"}}')

    # detector
    files = ["package.json"]
    stack = detect_stack(files, base_path=tmp_path)

    assert stack.language == "Node.js"
    assert stack.tests == "Jest"
    assert stack.container == False

def test_detect_python_stack(tmp_path):
    (tmp_path / "requirements.txt").write_text("pytest\nrequests")
    (tmp_path / "Dockerfile").touch()

    files = ["requirements.txt", "Dockerfile"]
    stack = detect_stack(files, base_path=tmp_path)

    assert stack.language == "Python"
    assert stack.tests == "Pytest"
    assert stack.container == True

def test_detect_terraform_aws(tmp_path):
    tf_dir = tmp_path / "terraform"
    tf_dir.mkdir()
    (tf_dir / "main.tf").write_text('provider "aws" { region = "us-east-1" }')

    files = ["terraform"]
    stack = detect_stack(files, base_path=tmp_path)

    assert stack.infrastructure == "Terraform"
    assert stack.cloud == "AWS"
