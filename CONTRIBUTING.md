# 🤝 Guia de Contribuição

Obrigado por considerar contribuir com o Football Data Lake! Este documento fornece diretrizes para contribuir com o projeto.

## 🎯 Como Você Pode Contribuir

### 1. Reportar Bugs 🐛

Encontrou um bug? Abra uma [issue](https://github.com/seu-usuario/datalake/issues/new) com:

- **Título claro**: "Bug: erro ao fazer scraping de jogadores com acento"
- **Descrição detalhada**: passos para reproduzir
- **Ambiente**: SO, versão Python, versão das libs
- **Logs/Screenshots**: se aplicável
- **Comportamento esperado vs real**

### 2. Sugerir Features 💡

Tem uma ideia? Abra uma issue com tag `enhancement`:

- Descreva o problema que resolve
- Proponha uma solução (opcional)
- Explique o caso de uso

### 3. Melhorar Documentação 📚

- Corrigir typos
- Adicionar exemplos
- Traduzir para outros idiomas
- Melhorar explicações

### 4. Contribuir com Código 💻

## 📋 Processo de Contribuição

### 1. Fork o Repositório

```bash
# Clone seu fork
git clone https://github.com/SEU-USUARIO/datalake.git
cd datalake

# Adicione upstream
git remote add upstream https://github.com/AUTOR-ORIGINAL/datalake.git
```

### 2. Crie uma Branch

```bash
# Atualize main
git checkout main
git pull upstream main

# Crie branch para sua feature
git checkout -b feature/nome-da-feature
# ou
git checkout -b fix/nome-do-bug
```

**Convenção de nomes:**
- `feature/` - novas funcionalidades
- `fix/` - correções de bugs
- `docs/` - mudanças em documentação
- `refactor/` - refatoração de código
- `test/` - adição/correção de testes

### 3. Faça Suas Mudanças

**Boas práticas:**

✅ **DO:**
- Mantenha commits pequenos e focados
- Escreva mensagens de commit claras
- Adicione docstrings nas funções
- Teste seu código localmente
- Siga o estilo de código existente
- Atualize documentação se necessário

❌ **DON'T:**
- Misturar múltiplas features em um PR
- Fazer commits diretamente na main
- Adicionar arquivos gerados (`.pyc`, `__pycache__`)
- Incluir dados sensíveis (`.env`, credenciais)

### 4. Commit e Push

```bash
# Stage mudanças
git add .

# Commit com mensagem descritiva
git commit -m "feat: adiciona suporte para Understat API"

# Push para seu fork
git push origin feature/nome-da-feature
```

**Formato de mensagens de commit:**
```
tipo: descrição curta (max 50 chars)

Descrição mais detalhada se necessário (max 72 chars por linha)

Refs #123 (número da issue, se aplicável)
```

**Tipos de commit:**
- `feat`: nova funcionalidade
- `fix`: correção de bug
- `docs`: mudanças em documentação
- `style`: formatação, ponto e vírgula, etc
- `refactor`: refatoração de código
- `test`: adição de testes
- `chore`: tarefas de manutenção

### 5. Abra um Pull Request

1. Vá para seu fork no GitHub
2. Clique em "Compare & pull request"
3. Preencha o template do PR:

```markdown
## Descrição
Breve descrição das mudanças.

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova feature
- [ ] Breaking change
- [ ] Documentação

## Como Testar
1. Execute `python scripts/...`
2. Verifique que...
3. Compare com...

## Checklist
- [ ] Código segue o estilo do projeto
- [ ] Adicionei testes (se aplicável)
- [ ] Documentação atualizada
- [ ] Todos os testes passam
- [ ] Sem warnings ou erros
```

## 🧪 Rodando Testes

```bash
# Instale dependências de dev
pip install -r requirements.txt

# Execute testes (quando implementados)
pytest tests/

# Lint
flake8 scripts/
black scripts/ --check
```

## 📏 Padrões de Código

### Python Style Guide

Seguimos [PEP 8](https://pep8.org/) com algumas exceções:

- **Line length:** 100 caracteres (não 79)
- **Imports:** Organize em 3 grupos (stdlib, third-party, local)
- **Docstrings:** Obrigatórias em funções públicas

**Exemplo de função bem documentada:**

```python
def fetch_transfermarkt_seasons(player_id: int, player_name: str) -> pd.DataFrame:
    """
    Faz scraping das temporadas de um jogador no Transfermarkt.
    
    Args:
        player_id: ID numérico do jogador no Transfermarkt (ex: 8198 para CR7)
        player_name: Nome do jogador formatado para URL (ex: "cristiano-ronaldo")
        
    Returns:
        DataFrame com colunas: season, team, league, appearances, goals, assists
        
    Raises:
        requests.HTTPError: Se página não existir (404)
        ValueError: Se player_id inválido
        
    Example:
        >>> df = fetch_transfermarkt_seasons(8198, "cristiano-ronaldo")
        >>> print(df.shape)
        (98, 6)
    """
    # Implementação...
```

### Naming Conventions

- **Variables:** `snake_case`
- **Functions:** `snake_case`
- **Classes:** `PascalCase`
- **Constants:** `UPPER_CASE`
- **Private:** `_leading_underscore`

### Imports

```python
# 1. Standard library
import os
import sys
from datetime import datetime

# 2. Third-party
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 3. Local
from utils.http import get_session
from utils.io import save_csv
```

## 🔍 Code Review

Seu PR passará por code review. Espere feedback sobre:

- **Lógica:** A solução faz sentido?
- **Performance:** É eficiente?
- **Legibilidade:** Código é claro?
- **Manutenibilidade:** Fácil de manter?
- **Testes:** Adequadamente testado?

**Como responder a feedback:**

✅ **Bom:**
> "Ótimo ponto! Mudei para usar list comprehension. Commit abc123."

❌ **Ruim:**
> "Funcionou no meu computador."

## 🚀 Áreas Prioritárias

Estamos especialmente interessados em contribuições nas seguintes áreas:

### 1. **Fontes de Dados Adicionais**
- [ ] Understat API integration
- [ ] Whoscored scraper
- [ ] StatsBomb open data
- [ ] API Futebol Brasileiro

### 2. **Testes**
- [ ] Unit tests para functions core
- [ ] Integration tests para pipeline ETL
- [ ] Mock data para testes rápidos

### 3. **Performance**
- [ ] Paralelização de scraping
- [ ] Caching mais inteligente
- [ ] Otimização de pandas operations

### 4. **Features**
- [ ] API REST com FastAPI
- [ ] Dashboard web com Streamlit
- [ ] Export para Parquet/SQLite
- [ ] Suporte a análise de partidas individuais

### 5. **Documentação**
- [ ] Tradução para inglês
- [ ] Tutoriais em vídeo
- [ ] Jupyter notebooks de exemplo
- [ ] API documentation (Sphinx)

## 📦 Estrutura de um Novo Script

Se estiver adicionando um novo script em `scripts/`, use este template:

```python
"""
Breve descrição do script (1-2 linhas).

Descrição mais detalhada se necessário.

Usage:
    python scripts/seu_script.py [args]
    
Example:
    python scripts/seu_script.py "Lionel Messi"
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

# Adicione root ao path para imports locais
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


def main_function(arg1: str, arg2: int = 10) -> pd.DataFrame:
    """
    Função principal com docstring clara.
    
    Args:
        arg1: Descrição do argumento
        arg2: Descrição com valor padrão
        
    Returns:
        DataFrame processado
    """
    # Implementação
    pass


def main():
    """Entry point quando executado como script."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('arg1', help='Descrição do argumento')
    parser.add_argument('--arg2', type=int, default=10, help='Argumento opcional')
    
    args = parser.parse_args()
    
    result = main_function(args.arg1, args.arg2)
    print(f"✅ Processado com sucesso: {len(result)} linhas")


if __name__ == '__main__':
    main()
```

## 🙏 Reconhecimento

Contribuidores serão adicionados ao README.md na seção de créditos!

## ❓ Dúvidas?

- Abra uma [issue de discussão](https://github.com/seu-usuario/datalake/issues/new?labels=question)
- Entre em contato: seu@email.com
- LinkedIn: [seu perfil]

---

**Obrigado por contribuir! 🎉⚽**
