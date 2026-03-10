from typing import Dict, Optional

PROVIDERS_CONFIG = {
    "OPENAI_API_KEY": {
        "url": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo",
        "name": "OpenAI"
    },
    "OPENROUTER_API_KEY": {
        "url": "https://openrouter.ai/api/v1",
        "model": "meta-llama/llama-3-8b-instruct",
        "name": "OpenRouter"
    },
    "GEMINI_API_KEY": {
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-1.5-flash",
        "name": "Google Gemini"
    },
    "GOOGLE_API_KEY": {
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-1.5-flash",
        "name": "Google AI Studio"
    },
    "GROQ_API_KEY": {
        "url": "https://api.groq.com/openai/v1",
        "model": "llama3-8b-8192",
        "name": "Groq"
    },
    "DEEPSEEK_API_KEY": {
        "url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "name": "DeepSeek"
    },
    "MISTRAL_API_KEY": {
        "url": "https://api.mistral.ai/v1",
        "model": "mistral-tiny",
        "name": "Mistral"
    },
    "TOGETHER_API_KEY": {
        "url": "https://api.together.xyz/v1",
        "model": "togethercomputer/llama-2-70b-chat",
        "name": "Together AI"
    },
    "FIREWORKS_API_KEY": {
        "url": "https://api.fireworks.ai/inference/v1",
        "model": "accounts/fireworks/models/llama-v3-8b-instruct",
        "name": "Fireworks AI"
    },
    "PPLX_API_KEY": {
        "url": "https://api.perplexity.ai",
        "model": "llama-3-sonar-small-32k-chat",
        "name": "Perplexity"
    },
    "OLLAMA_MODEL": {
        "url": "http://localhost:11434/v1",
        "model": "llama3.1:8b",
        "name": "Ollama (Local)"
    }
}

KNOWN_KEYS = [
    "OPENAI_API_KEY",
    "OPENROUTER_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GROQ_API_KEY",
    "DEEPSEEK_API_KEY",
    "MISTRAL_API_KEY",
    "TOGETHER_API_KEY",
    "FIREWORKS_API_KEY",
    "PPLX_API_KEY",
    "OLLAMA_MODEL",
    "ANTHROPIC_API_KEY",
    "COHERE_API_KEY",
    "AI21_API_KEY",
    "REPLICATE_API_TOKEN",
    "HUGGINGFACE_API_KEY",
    "HF_TOKEN",
    "OCTOAI_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "LANGCHAIN_API_KEY",
    "PINECONE_API_KEY",
    "WEAVIATE_API_KEY"
]
