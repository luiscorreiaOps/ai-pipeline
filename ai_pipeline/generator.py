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
       - Install step MUST run: pip install -e . && pip install pytest
       - Test step MUST run: python3 -m pytest
    4. If Containerization is 'Docker':
       - Include Docker steps but they MUST be fail-safe.
       - Use `if: ${{{{ secrets.DOCKER_USERNAME != '' }}}}` on all Docker login and push steps.
    5. Ensure all steps have a 'name' and a 'run' (or 'uses') field. No empty steps.
    6. MANDATORY: Never run just 'pytest'. Always use 'python3 -m pytest' to avoid PATH issues.
    7. DEPLOY: Include a placeholder deploy step that only runs if previous steps pass.
    
    TEMPLATE STRUCTURE:
    name: CI/CD Pipeline
    on: [push]
    jobs:
      build-and-deploy:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v3
          ...
    """

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a DevOps expert specialized in GitHub Actions. You always return valid YAML and use double curly braces ${{{{ }}}} for secrets and variables."},
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
            
        # Pós-processamento: Corrige erros comuns de sintaxe de IA
        # 1. Corrige ${ secrets... } para ${{ secrets... }}
        content = re.sub(r'if:\s*\${(?!\s*{)', 'if: ${{', content)
        # 2. Garante que se abriu com ${{ termine com }}
        content = re.sub(r'\${{([^}]*)}', r'${{\1}}', content)
        
        # 3. Corrige o erro comum de tentar usar ${{ PYTHONPATH }} (não existe no GitHub)
        content = content.replace('${{ PYTHONPATH }}', '$PYTHONPATH')
        content = content.replace('${{ env.PYTHONPATH }}', '$PYTHONPATH')
        
        # 4. Corrige chaves triplas acidentais como }}} para }}
        content = content.replace('}}}', '}}')
        # 4. Corrige funções inexistentes que IAs inventam como fileexists()
        content = re.sub(r'&&\s*fileexists\([^)]*\)', '', content)
        # 5. Remove espaços extras antes de }}
        content = re.sub(r'\s+}}', ' }}', content)
            
        return content.strip()

    except Exception as e:
        logger.error(f"Failed to generate pipeline: {e}")
        if 'response' in locals() and response.status_code == 401:
            raise RuntimeError(f"Authentication Error (401). Please check your API key.")
        raise RuntimeError(f"Failed to generate pipeline: {e}")
