from typing import Dict, Optional

PROVIDERS_CONFIG = {
    "OPENAI_API_KEY": {
        "url": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo",
        "name": "Generic Provider 1"
    },
    "OPENROUTER_API_KEY": {
        "url": "https://openrouter.ai/api/v1",
        "model": "meta-llama/llama-3-8b-instruct",
        "name": "Generic Provider 2"
    },
    "GROQ_API_KEY": {
        "url": "https://api.groq.com/openai/v1",
        "model": "llama3-8b-8192",
        "name": "Generic Provider 3"
    },
    "DEEPSEEK_API_KEY": {
        "url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "name": "Generic Provider 4"
    },
    "MISTRAL_API_KEY": {
        "url": "https://api.mistral.ai/v1",
        "model": "mistral-tiny",
        "name": "Generic Provider 5"
    },
    "TOGETHER_API_KEY": {
        "url": "https://api.together.xyz/v1",
        "model": "togethercomputer/llama-2-70b-chat",
        "name": "Generic Provider 6"
    },
    "FIREWORKS_API_KEY": {
        "url": "https://api.fireworks.ai/inference/v1",
        "model": "accounts/fireworks/models/llama-v3-8b-instruct",
        "name": "Generic Provider 7"
    },
    "PPLX_API_KEY": {
        "url": "https://api.perplexity.ai",
        "model": "llama-3-sonar-small-32k-chat",
        "name": "Generic Provider 8"
    }
}

KNOWN_KEYS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
    "COHERE_API_KEY",
    "AI21_API_KEY",
    "MISTRAL_API_KEY",
    "TOGETHER_API_KEY",
    "PPLX_API_KEY",
    "GROQ_API_KEY",
    "DEEPSEEK_API_KEY",
    "REPLICATE_API_TOKEN",
    "HUGGINGFACE_API_KEY",
    "HF_TOKEN",
    "FIREWORKS_API_KEY",
    "OPENROUTER_API_KEY",
    "OCTOAI_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "LANGCHAIN_API_KEY",
    "PINECONE_API_KEY",
    "WEAVIATE_API_KEY"
]
