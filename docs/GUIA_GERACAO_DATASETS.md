# 📘 Guia Rápido: Como Gerar Dataset de Qualquer Jogador

## 🎯 Objetivo
Gerar dataset enriquecido, pronto para Power BI, de qualquer jogador do banco de dados.

---

## 🚀 Uso Básico

### 1. Gerar dataset de um jogador

```bash
python scripts/enrich_player_complete_v2.py "Nome do Jogador"
```

**Exemplos:**
```bash
# Cristiano Ronaldo
python scripts/enrich_player_complete_v2.py "Cristiano Ronaldo"

# Lionel Messi
python scripts/enrich_player_complete_v2.py "Lionel Messi"

# Kaká
python scripts/enrich_player_complete_v2.py "Kaká"

# Neymar
python scripts/enrich_player_complete_v2.py "Neymar"

# Romário
python scripts/enrich_player_complete_v2.py "Romário"
```

---

## 📊 O Que o Script Faz?

### ✅ Automaticamente:
1. **Busca o jogador** no banco de dados local
2. **Filtra apenas ligas domésticas** (remove Copas do Mundo, Eurocopas, etc)
3. **Agrega temporadas** quando jogador atuou em múltiplos times
4. **Calcula estatísticas corretas** (evita duplicação no Power BI)
5. **Gera arquivo CSV** pronto para importar

### 📁 Saída:
```
datalake/processed/enriched/jogador_powerbi_enriched.csv
```

Exemplo: `cristiano_ronaldo_powerbi_enriched.csv`

---

## ⚙️ Opções Avançadas

### Incluir competições internacionais
```bash
python scripts/enrich_player_complete_v2.py "Cristiano Ronaldo" --include-intl
```
Inclui Copa do Mundo, Eurocopa, Champions League, etc.

### Não agregar temporadas (manter múltiplas linhas)
```bash
python scripts/enrich_player_complete_v2.py "Cristiano Ronaldo" --no-aggregate
```
Útil se você quiser ver cada competição separadamente.

### Combinar opções
```bash
python scripts/enrich_player_complete_v2.py "Lionel Messi" --include-intl --no-aggregate
```

---

## 🔍 Problemas Resolvidos

### ❌ Problema Antigo:
- Dataset tinha múltiplas linhas por temporada
- Power BI somava gols de Liga + Copa + Champions
- Gols inflados (ex: 200+ gols em uma temporada ❌)

### ✅ Solução Nova (V2):
- **1 linha = 1 temporada**
- Apenas ligas domésticas (por padrão)
- Quando jogador mudou de time, combina estatísticas
- Power BI mostra valores corretos (ex: 48 gols máximo ✅)

---

## 📝 Passo a Passo Completo

### Exemplo: Gerar dataset do Kaká

```bash
# 1. Gerar dataset
python scripts/enrich_player_complete_v2.py "Kaká"
```

**Saída do script:**
```
✅ Found: Kaká
   Seasons in database: 45
   Teams: Milan, Real Madrid, Orlando City, ...

✅ Filtered out 12 international competition seasons
✅ Kept 33 domestic league seasons

✅ Aggregated to 15 unique seasons (was 33)
   
✅ Saved: datalake/processed/enriched/kaka_powerbi_enriched.csv
   Rows: 15
   Columns: 52
   Total goals: 104
   Total assists: 89
```

### 2. (Opcional) Editar metadata

O script cria automaticamente:
```
datalake/raw/metadata/kaka_metadata.json
```

Edite com informações do jogador:
```json
{
  "date_of_birth": "1982-04-22",
  "place_of_birth": "Brasília, Brazil",
  "height": "1.86m",
  "nationality": "Brazil",
  "position_detail": "Attacking Midfield",
  "foot": "Left",
  "honors": [
    "FIFA World Cup: 2002",
    "Ballon d'Or: 2007",
    "UEFA Champions League: 2006-07"
  ],
  "transfermarkt_url": "https://www.transfermarkt.com/kaka/profil/spieler/3368",
  "notes": "One of the best attacking midfielders of his generation"
}
```

### 3. Re-executar para incluir metadata

```bash
python scripts/enrich_player_complete_v2.py "Kaká"
```

Agora o CSV terá colunas `meta_*` preenchidas!

### 4. Importar no Power BI

1. Abra Power BI Desktop
2. **Obter Dados** → **Texto/CSV**
3. Selecione: `datalake/processed/enriched/kaka_powerbi_enriched.csv`
4. Clique **Carregar**

---

## 🎨 Criar Gráficos no Power BI

### Scatter Chart (Gols por Idade)

**Configuração:**
- **X Axis:** `age`
- **Y Axis:** `SUM(Performance_Gls)`
- **Size:** `SUM(Playing_Time_Min)`
- **Legend:** `team`

### Line Chart (Evolução Temporal)

**Configuração:**
- **X Axis:** `season_period` (ordenar cronologicamente)
- **Y Axis:** `SUM(Performance_Gls)`
- **Legend:** `team`

### Card (Total de Gols)

**Medida:**
```dax
Total Goals = SUM('Table'[Performance_Gls])
```

### Card (Gols por 90 Minutos)

**Medida:**
```dax
Goals per 90 = AVERAGE('Table'[Per_90_Minutes_Gls])
```

---

## 📊 Colunas Disponíveis

### Performance (principais)
- `Performance_Gls` - Gols marcados
- `Performance_Ast` - Assistências
- `Performance_G+A` - Gols + Assistências
- `Performance_PK` - Pênaltis marcados

### Playing Time
- `Playing_Time_MP` - Partidas jogadas
- `Playing_Time_Min` - Minutos totais
- `Playing_Time_90s` - Jogos de 90 minutos

### Per 90 Minutes (médias)
- `Per_90_Minutes_Gls` - Gols por 90min
- `Per_90_Minutes_Ast` - Assistências por 90min
- `Per_90_Minutes_G+A` - Gols+Assistências por 90min

### Info
- `season_period` - Temporada (ex: "2011-2012")
- `age` - Idade do jogador
- `team` - Time(s) na temporada
- `league` - Liga
- `player` - Nome do jogador
- `nation` - Nacionalidade

### Metadata (se preenchido)
- `meta_date_of_birth`
- `meta_place_of_birth`
- `meta_height`
- `meta_honors`
- `meta_notes`

---

## 🔥 Jogadores Populares no Database

Execute este comando para ver jogadores disponíveis:

```bash
python -c "import pandas as pd; df = pd.read_csv('datalake/processed/players_complete_1995_2025.csv'); print('\nJogadores com mais temporadas:'); print(df.groupby('player').size().sort_values(ascending=False).head(20))"
```

**Alguns disponíveis:**
- Cristiano Ronaldo
- Lionel Messi
- Kaká
- Neymar
- Zlatan Ibrahimović
- Robert Lewandowski
- Sergio Ramos
- Luka Modrić
- etc.

---

## 🆚 Comparar Múltiplos Jogadores

### 1. Gerar datasets individuais

```bash
python scripts/enrich_player_complete_v2.py "Cristiano Ronaldo"
python scripts/enrich_player_complete_v2.py "Lionel Messi"
python scripts/enrich_player_complete_v2.py "Kaká"
```

### 2. Combinar no Power BI

**Opção A: Importar múltiplos arquivos**
1. Importar cada CSV separadamente
2. Combinar com **Append Queries** no Power Query

**Opção B: Criar script de merge**

```python
import pandas as pd

# Ler datasets
cr7 = pd.read_csv('datalake/processed/enriched/cristiano_ronaldo_powerbi_enriched.csv')
messi = pd.read_csv('datalake/processed/enriched/lionel_messi_powerbi_enriched.csv')
kaka = pd.read_csv('datalake/processed/enriched/kaka_powerbi_enriched.csv')

# Combinar
combined = pd.concat([cr7, messi, kaka], ignore_index=True)

# Salvar
combined.to_csv('datalake/processed/enriched/comparison_cr7_messi_kaka.csv', index=False)
```

Depois importar `comparison_cr7_messi_kaka.csv` no Power BI!

---

## ❓ Troubleshooting

### Erro: "Player not found"
- Verifique se o nome está correto
- Tente busca parcial: `"Ronaldo"` em vez de `"Cristiano Ronaldo"`
- Veja lista de jogadores disponíveis (comando acima)

### Erro: "No data after filtering"
- Jogador pode não ter atuado em ligas domésticas principais
- Use `--include-intl` para incluir competições internacionais

### Dataset com valores estranhos
- Re-execute com `--no-aggregate` para debug
- Verifique se há temporadas duplicadas

### Metadata não aparece no CSV
- Edite o arquivo JSON em `datalake/raw/metadata/`
- Re-execute o script após editar

---

## 📚 Scripts Relacionados

### Script Antigo (V1)
```bash
scripts/enrich_player_complete.py
```
❌ Não use mais! Gera duplicatas.

### Script Novo (V2) - Recomendado
```bash
scripts/enrich_player_complete_v2.py
```
✅ Use este! Power BI ready.

### Agregação Manual
```bash
scripts/aggregate_by_season.py
```
Para corrigir datasets já gerados com V1.

---

## 🎓 Resumo

### Comando Padrão (Recomendado)
```bash
python scripts/enrich_player_complete_v2.py "Nome do Jogador"
```

### Resultado
- ✅ 1 linha = 1 temporada
- ✅ Apenas ligas domésticas
- ✅ Gols/Assistências corretos
- ✅ Pronto para Power BI

### Importar no Power BI
1. **Obter Dados** → **CSV**
2. Selecionar arquivo `*_powerbi_enriched.csv`
3. Criar visuais usando `SUM()` e `AVERAGE()`

---

**🚀 Boa análise!**
