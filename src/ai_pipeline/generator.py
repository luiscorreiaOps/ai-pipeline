import requests
import json
import re
import os
from .config import config
from .detector import Stack
from .providers import PROVIDERS_CONFIG
from .utils import get_logger

logger = get_logger("generator")

def generate_pipeline(stack: Stack, api_key: str, provider_key: str = None) -> str:
    """Generates an indestructible CI/CD pipeline."""
    
    provider_info = PROVIDERS_CONFIG.get(provider_key, list(PROVIDERS_CONFIG.values())[0])
    url = provider_info["url"].rstrip("/") + "/chat/completions"
    model = api_key if provider_key == "OLLAMA_MODEL" else provider_info["model"]
    
    headers = {"Content-Type": "application/json"}
    if provider_key != "OLLAMA_MODEL":
        headers["Authorization"] = f"Bearer {api_key}"

    lang = stack.language.lower() if stack.language else "python"
    snyk_action = "python" if "python" in lang else "dotnet" if "c#" in lang or "net" in lang else "node"
    setup_action = "actions/setup-python@v5" if "python" in lang else "actions/setup-dotnet@v4" if "c#" in lang or "net" in lang else "actions/setup-node@v4"
    setup_version_key = "python-version" if "python" in lang else "dotnet-version" if "c#" in lang or "net" in lang else "node-version"
    setup_version_val = stack.language_version or ("3.11" if "python" in lang else "9.0" if "c#" in lang else "20")

    # Get commands from AI
    prompt = f"Act as a CI console. Provide ONLY the shell commands for a {stack.language} project to build and test. DO NOT EXPLAIN. NO MARKDOWN. NO YAML."
    data = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.0}
    
    indented_commands = "          dotnet build"
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=300)
        response.raise_for_status()
        raw_output = response.json()['choices'][0]['message']['content'].strip()
        clean_lines = re.sub(r"```[\w]*\n?", "", raw_output).replace("```", "").split("\n")
        valid_lines = []
        for line in clean_lines:
            t = line.strip()
            if t and any(t.startswith(c) for c in ["dotnet", "npm", "pip", "pytest", "python", "cd ", "mkdir ", "ls "]):
                # Force corrected test path in Python commands
                if "python" in lang:
                    t = t.replace(" tests", " src/tests").replace(" tests/", " src/tests/")
                valid_lines.append("          " + t)
        if valid_lines:
            indented_commands = "\n".join(valid_lines)
    except Exception:
        pass

    # Indestructible paths
    python_path_fix = "export PYTHONPATH=$PYTHONPATH:$(pwd)/src\n          " if "python" in lang else ""

    yaml = f"name: CI Pipeline\n"
    yaml += "on:\n  push:\n    branches: [ main, develop ]\n"
    yaml += "env:\n  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}\n  SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}\n  SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}\n"
    yaml += "jobs:\n"
    
    yaml += "  Security:\n    runs-on: ubuntu-latest\n    steps:\n"
    yaml += "      - uses: actions/checkout@v4\n"
    yaml += "      - uses: gitleaks/gitleaks-action@v2\n        continue-on-error: true\n"
    yaml += f"      - name: Snyk Scan\n        if: env.SNYK_TOKEN != ''\n        uses: snyk/actions/{snyk_action}@master\n"
    yaml += "        continue-on-error: true\n"
    yaml += "        env:\n          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}\n\n"

    yaml += "  Build_and_Test:\n    runs-on: ubuntu-latest\n    steps:\n"
    yaml += "      - uses: actions/checkout@v4\n"
    yaml += f"      - uses: {setup_action}\n        with:\n          {setup_version_key}: '{setup_version_val}'\n"
    yaml += "      - name: Install and Test\n        run: |\n"
    yaml += f"          {python_path_fix}" + indented_commands + "\n"
    yaml += "      - name: SonarCloud\n        if: env.SONAR_TOKEN != ''\n        uses: sonarsource/sonarcloud-github-action@master\n"
    yaml += "        continue-on-error: true\n"
    yaml += "        env:\n          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}\n\n"

    if stack.has_api:
        yaml += "  API_Compliance:\n    runs-on: ubuntu-latest\n    needs: Build_and_Test\n    steps:\n"
        yaml += "      - uses: actions/checkout@v4\n"
        yaml += f"      - name: Lint API\n        run: npx @stoplight/spectral-cli lint {stack.api_spec_path}\n        continue-on-error: true\n\n"

    if stack.container:
        yaml += "  Docker:\n    runs-on: ubuntu-latest\n    needs: Build_and_Test\n    steps:\n"
        yaml += "      - uses: actions/checkout@v4\n"
        yaml += f"      - name: Build\n        run: docker build -t project:{stack.project_version} .\n\n"

    yaml += "  Reporting:\n    runs-on: ubuntu-latest\n    needs: Build_and_Test\n    steps:\n"
    yaml += "      - name: Summary\n"
    yaml += "        run: |\n"
    yaml += f"          echo '## Project Version: {stack.project_version}' >> $GITHUB_STEP_SUMMARY\n"

    return yaml.strip()
