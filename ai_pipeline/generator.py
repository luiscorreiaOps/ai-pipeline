import requests
import json
from .config import config
from .detector import Stack
from .providers import PROVIDERS_CONFIG
from .utils import get_logger

logger = get_logger("generator")

def generate_pipeline(stack: Stack, api_key: str, provider_key: str = None) -> str:
    """Generates a CI/CD pipeline using a generic AI interface."""

    keys = list(PROVIDERS_CONFIG.keys())
    fallback_provider = keys[0] if keys else None
    provider_info = PROVIDERS_CONFIG.get(provider_key, PROVIDERS_CONFIG.get(fallback_provider))

    if not provider_info:
        logger.error("No AI provider configuration found.")
        raise RuntimeError("No suitable AI provider configuration found.")

    url = provider_info["url"].rstrip("/") + "/chat/completions"

    if provider_key == "OLLAMA_MODEL":
        model = api_key
    else:
        model = provider_info["model"]

    logger.info(f"Connecting to AI provider: {provider_info['name']} using model {model}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/ai-pipeline-tool",
        "X-Title": "AI Pipeline Tool",
    }


    prompt = f"""
    Generate a complete GitHub Actions CI/CD pipeline YAML file.
    
    PROJECT STACK:
    - Language: {stack.language} (Version: {stack.language_version or '3.x'})
    - Test Framework: {stack.tests}
    - Containerization: {'Docker' if stack.container else 'None'}
    - Infrastructure: {stack.infrastructure or 'None'}
    - Cloud Provider: {stack.cloud or 'None'}
    - Security Tools: {', '.join(stack.security_tools) if stack.security_tools else 'None'}

    STRICT RULES (MUST FOLLOW):
    1. Output MUST be ONLY valid YAML code.
    2. DO NOT include language markers like 'yml', 'yaml' or 'bash' inside the code block.
    3. If Language is Python:
       - Use actions/setup-python@v4 with python-version: '3.x'
       - Install step MUST run: pip install -e . && pip install pytest
       - Test step MUST run: export PYTHONPATH=$PYTHONPATH:. && python3 -m pytest
    4. If Containerization is 'Docker':
       - Include steps for 'docker build' and 'docker push' using secrets.DOCKER_USERNAME.
    5. Ensure all steps have a 'name' and a 'run' (or 'uses') field. No empty steps.
    6. MANDATORY: Never run just 'pytest'. Always use 'python3 -m pytest' to avoid PATH issues.
    
    TEMPLATE STRUCTURE:
    name: CI/CD Pipeline
    on: [push]
    jobs:
      build-and-deploy:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v3
          ... (add language setup, install, test, and docker steps here)
    """

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a CICD expert specialized in GitHub Actions."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=300)
        response.raise_for_status()

        result = response.json()
        content = result['choices'][0]['message']['content']

        if "```yaml" in content:
            content = content.split("```yaml")[1].split("```")[0].strip()
        elif "```yml" in content:
            content = content.split("```yml")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()

        # Remove prefixo 'yml' ou 'yaml' se ele ainda existir (algumas IAs bugam)
        lines = content.splitlines()
        if lines and lines[0].strip().lower() in ["yml", "yaml"]:
            content = "\n".join(lines[1:]).strip()

        return content.strip()

    except Exception as e:
        logger.error(f"Failed to generate pipeline: {e}")
        if 'response' in locals() and response.status_code == 401:
            raise RuntimeError(f"Authentication Error (401). Please check your API key.")
        raise RuntimeError(f"Failed to generate pipeline: {e}")
