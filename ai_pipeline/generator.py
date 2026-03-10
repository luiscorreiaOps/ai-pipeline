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
    model = provider_info["model"]
    
    logger.info(f"Connecting to AI provider: {provider_info['name']} using model {model}")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/ai-pipeline",
        "X-Title": "AI Pipeline Tool",
    }

    prompt = f"""
    Generate a complete GitHub Actions CI/CD pipeline YAML file for a project with the following stack:
    - Language: {stack.language} (Version: {stack.language_version or 'Latest'})
    - Test Framework: {stack.tests}
    - Containerization: {'Docker' if stack.container else 'None'}
    - Infrastructure: {stack.infrastructure}
    - Cloud Provider: {stack.cloud}
    - Custom Scripts: {stack.scripts}
    - Security Tools: {', '.join(stack.security_tools) if stack.security_tools else 'None'}

    CRITICAL INSTRUCTIONS:
    - If Containerization is 'Docker', include the Docker build and push steps DIRECTLY without 'if' conditions.
    - Use the detected Language Version in the setup steps.
    - Include: Checkout, Install dependencies, Run tests, Run Security scans (if present), Docker Build/Push (if present), and a placeholder Deploy step.
    - Return ONLY the YAML code within a code block. Do not add explanations.
    """

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a DevOps expert specialized in GitHub Actions."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=60)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        if "```yaml" in content:
            return content.split("```yaml")[1].split("```")[0].strip()
        elif "```" in content:
            return content.split("```")[1].strip()
        return content.strip()

    except Exception as e:
        logger.error(f"Failed to generate pipeline: {e}")
        if 'response' in locals() and response.status_code == 401:
            raise RuntimeError(f"Authentication Error (401). Please check your API key.")
        raise RuntimeError(f"Failed to generate pipeline: {e}")
