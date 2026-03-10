import requests
import json
import re
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
       - Install: pip install -e . && pip install pytest
       - Test: export PYTHONPATH=$PYTHONPATH:. && python3 -m pytest
    4. DOCKER FAIL-SAFE (CRITICAL):
       - To check if secrets exist, you MUST map them to JOB-LEVEL environment variables.
       - Example Job structure:
         jobs:
           build:
             env:
               DOCKER_USERNAME: ${{{{ secrets.DOCKER_USERNAME }}}}
             steps:
               - name: Login
                 if: ${{{{ env.DOCKER_USERNAME != '' }}}}
                 uses: docker/login-action@v2
    5. MANDATORY: Never run just 'pytest'. Always use 'python3 -m pytest'.
    6. Ensure all steps have a 'name' and 'run'/'uses'.
    """

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a DevOps expert. You never use 'secrets' context directly in 'if' conditions because it causes 'Unrecognized named-value' errors. You always map secrets to job-level env variables first."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
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
        
        lines = content.splitlines()
        if lines and lines[0].strip().lower() in ["yml", "yaml"]:
            content = "\n".join(lines[1:]).strip()
            
        # Pós-processamento: Corrige erros de sintaxe
        content = re.sub(r'if:\s*\${(?!\s*{)', 'if: ${{', content)
        content = re.sub(r'\${{([^}]*)}', r'${{\1}}', content)
        content = content.replace('}}}', '}}')
        
        # Correção agressiva para o erro 'secrets' no if
        # Se a IA ainda assim usar secrets no if, tentamos converter para env
        content = content.replace('if: ${{ secrets.', 'if: ${{ env.')
            
        return content.strip()

    except Exception as e:
        logger.error(f"Failed to generate pipeline: {e}")
        raise RuntimeError(f"Failed to generate pipeline: {e}")
