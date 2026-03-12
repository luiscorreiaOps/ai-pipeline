# Uso Pratico

O fluxo de trabalho da ferramenta e dividido em analise e geracao.

## Analise de Repositorio

O comando `analyze` realiza uma varredura passiva para identificar a stack tecnologica.

```bash
ai-pipeline-tool analyze
```

### O que e detectado:
- Linguagem e versao (ex: Node v18, Python 3.x).
- Frameworks de teste (Jest, Pytest, Mocha).
- Ferramentas de seguranca (Snyk, Bandit, Trivy).
- Uso de containers (Dockerfile).
- Infraestrutura (Terraform, Cloud Providers).

## Geracao de Pipeline

O comando `generate` cria o arquivo de workflow para o GitHub Actions.

```bash
ai-pipeline-tool generate
```

### Comportamento do Arquivo:
- **Localizacao**: O arquivo e criado em `.github/workflows/ci.yml`.
- **Sobrescrita**: Se o arquivo `ci.yml` ja existir, ele sera sobrescrito com a nova versao gerada pela IA.
- **Diretorio**: Caso a pasta `.github/workflows` nao exista, ela sera criada automaticamente.

### Regras de Geracao:
- Pipelines Python incluem instalacao editavel (`pip install -e .`) e configuracao de PYTHONPATH.
- Pipelines Node incluem instalacao de dependencias e execucao de scripts detectados.
- Passos de Docker sao fail-safe (nao quebram se os secrets de login estiverem ausentes).
