# Arquitetura do Sistema

O ai-pipeline-tool foi projetado seguindo principios de modularidade e desacoplamento.

## Componentes Internos

### 1. Scanner (`scanner.py`)
Responsavel pela varredura do sistema de arquivos. Utiliza a biblioteca `pathlib` para localizar arquivos especificos de configuracao sem ler conteudos pesados inicialmente.

### 2. Detector (`detector.py`)
Nucleo de inteligencia de dados. Le o conteudo de arquivos como `package.json` ou `Dockerfile` para extrair metadados tecnicos. Utiliza Regex para limpeza de strings e extracao de versoes.

### 3. Generator (`generator.py`)
Integra o sistema com as APIs de IA.
- **Prompt Engineering**: Estrutura os dados do Detector em um prompt rigido.
- **Post-processing**: Limpa a resposta da IA corrigindo erros comuns de sintaxe do GitHub Actions (ex: chaves triplas ou variaveis de ambiente mal formadas).

### 4. Config (`config.py`)
Gerencia o carregamento de variaveis via `python-dotenv` e prioriza configuracoes locais em relacao a globais.

### 5. Providers (`providers.py`)
Centraliza as URLs e modelos de cada provedor, facilitando a expansao para novas IAs sem alterar a logica de geracao.

## Fluxo de Execucao

`CLI Input` -> `Scanner` -> `Detector` -> `Config/Providers` -> `IA API` -> `Post-processor` -> `File System (.github/)`
