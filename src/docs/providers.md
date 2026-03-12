# Provedores de IA

A ferramenta e compativel com multiplos provedores.

## Provedores Nativos

Os seguintes provedores possuem configuracao direta de endpoint e modelo:

| Provedor | Variavel | Endpoint Padrao | Modelo |
| :--- | :--- | :--- | :--- |
| OpenAI | OPENAI_API_KEY | api.openai.com | gpt-3.5-turbo |
| OpenRouter | OPENROUTER_API_KEY | openrouter.ai | llama-3-8b-instruct |
| Gemini | GEMINI_API_KEY | googleapis.com | gemini-1.5-flash |
| Groq | GROQ_API_KEY | api.groq.com | llama3-8b-8192 |
| Ollama | OLLAMA_MODEL | localhost:11434 | (definido por variavel) |

## Uso com Ollama (Local)

Para utilizar o Ollama:
1. Exporte a variavel `OLLAMA_MODEL` com o nome do modelo (ex: `llama3.1:8b`).
2. O timeout para modelos locais e de 300 segundos para acomodar processamentos mais lentos.

## Fallback

Caso uma chave desconhecida seja detectada (ex: `ANTHROPIC_API_KEY`), a ferramenta tentara utilizar o OpenRouter como ponte de compatibilidade.
