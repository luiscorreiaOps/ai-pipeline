# Configuracao

A ferramenta utiliza variaveis de ambiente e arquivos .env para gerenciar as credenciais dos provedores de IA.

## Variaveis de Ambiente

As seguintes variaveis sao escaneadas automaticamente:

- OPENAI_API_KEY
- OPENROUTER_API_KEY
- GEMINI_API_KEY
- GOOGLE_API_KEY
- GROQ_API_KEY
- DEEPSEEK_API_KEY
- OLLAMA_MODEL (para uso local)

## Comando Init

O comando `init` permite configurar uma chave padrao para o diretorio atual.

```bash
ai-pipeline-tool init
```

Ao executar este comando:
1. A ferramenta escaneia o ambiente em busca de chaves existentes.
2. Exibe uma lista numerada para selecao.
3. Cria ou atualiza um arquivo `.env` local com as variaveis `AI_PROVIDER_KEY` e `AI_API_KEY`.

## Persistencia

As configuracoes salvas via `init` tem prioridade sobre as variaveis globais de ambiente durante a execucao dos comandos `analyze` e `generate`.
