# 🚀 Comandos Git para Publicar no GitHub

## 📋 Checklist Antes de Publicar

- [ ] README.md atualizado
- [ ] .gitignore configurado
- [ ] requirements.txt completo
- [ ] LICENSE adicionado
- [ ] Arquivos temporários removidos (check_*.py, __pycache__)
- [ ] Dados sensíveis removidos (.env não commitado)
- [ ] Documentação completa (guias Power BI, LinkedIn, etc)

## 🎯 Setup Inicial

### 1. Inicializar Git (se ainda não fez)

```bash
cd C:\Users\juan_\OneDrive\Desktop\datalake

# Inicializar repositório
git init

# Verificar status
git status
```

### 2. Adicionar Arquivos

```bash
# Adicionar todos os arquivos (respeitando .gitignore)
git add .

# Verificar o que será commitado
git status

# Ver diff do que mudou
git diff --cached
```

### 3. Primeiro Commit

```bash
# Commit inicial
git commit -m "feat: initial commit - football datalake with ETL pipeline"

# Verificar histórico
git log --oneline
```

## 🌐 Publicar no GitHub

### Opção 1: Via GitHub Web (Recomendado para Iniciantes)

1. **Crie repo no GitHub:**
   - Vá para https://github.com/new
   - Nome: `football-datalake` ou `datalake`
   - Descrição: "⚽ Pipeline ETL de dados de futebol com Python e Power BI"
   - Público ou Privado: **Público** (para portfolio)
   - **NÃO** marque "Initialize with README" (já temos um!)

2. **Conecte repo local:**

```bash
# Adicione remote (substitua SEU-USUARIO)
git remote add origin https://github.com/SEU-USUARIO/football-datalake.git

# Verifique
git remote -v

# Push inicial
git branch -M main
git push -u origin main
```

3. **Resultado:**
   - Acesse: `https://github.com/SEU-USUARIO/football-datalake`
   - README renderizado na página inicial ✅

### Opção 2: Via GitHub CLI

```bash
# Instale GitHub CLI: https://cli.github.com/

# Login
gh auth login

# Criar repo e publicar
gh repo create football-datalake --public --source=. --push

# Abrir no browser
gh repo view --web
```

## 📝 Workflow de Atualizações

### Fazer Mudanças e Atualizar

```bash
# 1. Fazer mudanças nos arquivos
# ...

# 2. Ver o que mudou
git status
git diff

# 3. Adicionar mudanças
git add arquivo_modificado.py
# ou adicionar tudo
git add .

# 4. Commit com mensagem descritiva
git commit -m "feat: adiciona support para Messi dataset"

# 5. Push para GitHub
git push origin main
```

### Convenções de Mensagens de Commit

```bash
# Nova feature
git commit -m "feat: adiciona scraping de Understat"

# Bug fix
git commit -m "fix: corrige duplicatas em CR7 dataset"

# Documentação
git commit -m "docs: atualiza guia Power BI com scatter chart"

# Refatoração
git commit -m "refactor: simplifica lógica de merge"

# Testes
git commit -m "test: adiciona testes para enrich_player"
```

## 🔄 Sincronizar Mudanças

### Baixar Mudanças do GitHub

```bash
# Pull (fetch + merge)
git pull origin main

# Ou fetch primeiro (ver o que mudou)
git fetch origin
git log HEAD..origin/main
git merge origin/main
```

## 🌿 Branches (Para Features Grandes)

```bash
# Criar branch para nova feature
git checkout -b feature/messi-vs-cr7

# Fazer mudanças...
git add .
git commit -m "feat: adiciona comparação Messi vs CR7"

# Push branch
git push origin feature/messi-vs-cr7

# No GitHub, criar Pull Request
# Após aprovação, merge para main
```

## 🏷️ Tags e Releases

```bash
# Criar tag de versão
git tag -a v1.0.0 -m "Release v1.0.0: pipeline ETL completo"

# Push tags
git push origin v1.0.0

# Ou push todas tags
git push origin --tags

# No GitHub: Releases → Create new release
```

## 🔍 Comandos Úteis

### Ver Histórico

```bash
# Log completo
git log

# Log resumido
git log --oneline

# Log com gráfico de branches
git log --oneline --graph --all

# Ver mudanças em commit específico
git show abc123
```

### Desfazer Mudanças

```bash
# Desfazer mudanças não commitadas
git checkout -- arquivo.py

# Desfazer último commit (mantém mudanças)
git reset HEAD~1

# Desfazer último commit (descarta mudanças) - CUIDADO!
git reset --hard HEAD~1

# Desfazer push (criar commit reverso)
git revert abc123
git push origin main
```

### Verificar Status

```bash
# Status detalhado
git status

# Ver remote configurado
git remote -v

# Ver branches
git branch -a

# Ver diff antes de commit
git diff
```

## 🚨 Resolver Problemas Comuns

### Problema 1: "Permission denied" ao fazer push

```bash
# Configurar credenciais
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"

# Usar token de acesso pessoal (PAT)
# GitHub Settings → Developer Settings → Personal Access Tokens
# Crie token e use no lugar da senha
```

### Problema 2: Arquivos grandes (>100MB)

```bash
# Adicionar ao .gitignore
echo "arquivo_grande.csv" >> .gitignore

# Remover do tracking
git rm --cached arquivo_grande.csv
git commit -m "fix: remove arquivo grande do tracking"
git push origin main
```

### Problema 3: Commitou arquivo sensível (.env)

```bash
# Remover do histórico (CUIDADO!)
git rm --cached .env
git commit -m "fix: remove .env do tracking"

# Adicionar ao .gitignore
echo ".env" >> .gitignore
git add .gitignore
git commit -m "fix: adiciona .env ao gitignore"

# Push
git push origin main

# IMPORTANTE: Troque credenciais expostas!
```

### Problema 4: Conflitos de merge

```bash
# Pull gerou conflitos
git pull origin main

# Edite arquivos conflitados (<<<<<<< HEAD)
# Após resolver:
git add arquivo_resolvido.py
git commit -m "fix: resolve conflitos de merge"
git push origin main
```

## 📊 GitHub Pages (Para Hospedar Docs)

```bash
# Criar branch gh-pages
git checkout -b gh-pages

# Adicionar index.html ou usar Jekyll
# ...

# Push
git push origin gh-pages

# Habilitar no GitHub:
# Settings → Pages → Source: gh-pages
# Acesse: https://SEU-USUARIO.github.io/football-datalake
```

## 🎯 Comandos Rápidos (Cheat Sheet)

```bash
# Setup inicial
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/USER/REPO.git
git push -u origin main

# Workflow diário
git pull origin main          # Baixar mudanças
# ... fazer mudanças ...
git add .                     # Stage mudanças
git commit -m "mensagem"      # Commit
git push origin main          # Publicar

# Verificação
git status                    # Ver estado
git log --oneline            # Ver histórico
git diff                     # Ver mudanças
git remote -v                # Ver remote

# Desfazer
git checkout -- arquivo      # Desfazer mudanças não commitadas
git reset HEAD~1             # Desfazer último commit
```

## ✅ Verificar se Está Tudo Certo

```bash
# Verificar remote
git remote -v
# Deve mostrar:
# origin  https://github.com/SEU-USUARIO/football-datalake.git (fetch)
# origin  https://github.com/SEU-USUARIO/football-datalake.git (push)

# Verificar branch
git branch
# Deve mostrar:
# * main

# Verificar último commit
git log -1
# Deve mostrar seu commit mais recente

# Verificar gitignore funciona
git status
# NÃO deve mostrar: __pycache__, .env, check_*.py
```

## 🎉 Pronto!

Seu repositório está no GitHub em: `https://github.com/SEU-USUARIO/football-datalake`

### Próximos passos:

1. ✅ Adicione topics no GitHub: `python`, `data-science`, `power-bi`, `football`, `etl`
2. ✅ Ative Issues e Discussions no Settings
3. ✅ Adicione badges no README (build status, license, etc)
4. ✅ Compartilhe no LinkedIn!

---

💡 **Dica:** Salve este arquivo como `GIT_COMMANDS.md` no repositório para referência futura!
