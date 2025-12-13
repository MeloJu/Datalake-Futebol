# 📚 Exemplos de Uso

## Caso 1: Análise de Carreira do Cristiano Ronaldo

### Gerar Dataset

```bash
python scripts/enrich_player.py "Cristiano Ronaldo"
```

### Resultados

```
✅ Gerado: datalake/processed/enriched/cristiano_ronaldo_enriched.csv

📊 Estatísticas:
- 35 temporadas (24 ligas domésticas + 11 internacionais)
- 565 gols em ligas domésticas
- 0.89 gols por 90 minutos (média da carreira)
- Período: 2003-2004 até 2025-2026
```

### Visualizações no Power BI

**1. Gols por Temporada**
```dax
Total_Gols = SUM([Performance_Gls])
```
- Eixo Y: `league` (categoria)
- Eixo X: `Total_Gols` (medida)
- Filtro: `is_domestic_league = TRUE`

**2. Eficiência (Gols/90min) por Liga**
```dax
Gols_por_90 = 
DIVIDE(
    SUM([Performance_Gls]) * 90,
    SUM([Playing_Time_Min])
)
```

**3. Progressão da Carreira**
```dax
Media_Movel_3_Temporadas = 
AVERAGEX(
    TOPN(3, 
        FILTER(
            ALL([season_period]),
            [season_period] <= MAX([season_period])
        ),
        [season_period],
        DESC
    ),
    [Performance_Gls]
)
```

---

## Caso 2: Comparação Multi-Jogador

### Gerar Múltiplos Datasets

```bash
python scripts/enrich_player.py "Cristiano Ronaldo"
python scripts/enrich_player.py "Lionel Messi"
python scripts/enrich_player.py "Kaká"
python scripts/enrich_player.py "Neymar"
```

### Combinar no Power BI

1. **Importar todos os CSVs**
2. **Append Queries** (Combinar tabelas)
3. **Criar coluna calculada:**

```dax
Jogador_Categoria = 
SWITCH(
    TRUE(),
    [player] = "Cristiano Ronaldo", "GOAT Tier",
    [player] = "Lionel Messi", "GOAT Tier",
    [player] = "Kaká", "World Class",
    [player] = "Neymar", "World Class",
    "Other"
)
```

### Análises Possíveis

- **Pico de Performance:** Qual temporada cada jogador teve maior gols/90?
- **Longevidade:** Quantas temporadas com >15 gols?
- **Adaptação:** Performance no primeiro ano em nova liga
- **Declínio:** Taxa de queda após os 30 anos

---

## Caso 3: Análise de Liga

### Filtrar por Liga Específica

```python
import pandas as pd

df = pd.read_csv('datalake/processed/enriched/cristiano_ronaldo_enriched.csv')

# Premier League apenas
premier = df[df['league'] == 'ENG-Premier League']
print(f"Goals in PL: {premier['Performance_Gls'].sum()}")

# La Liga apenas
laliga = df[df['league'] == 'ESP-La Liga']
print(f"Goals in La Liga: {laliga['Performance_Gls'].sum()}")

# Comparar médias
print(f"PL: {premier['Per_90_Minutes_Gls'].mean():.2f} goals/90")
print(f"La Liga: {laliga['Per_90_Minutes_Gls'].mean():.2f} goals/90")
```

### Visualização: Matriz de Comparação

| Liga | Temporadas | Gols | Gols/90 | Assistências |
|------|-----------|------|---------|--------------|
| Premier League | 6 | 103 | 0.66 | 27 |
| La Liga | 9 | 311 | 1.08 | 92 |
| Serie A | 3 | 81 | 0.86 | 15 |
| Saudi Pro League | 3 | 70 | 0.96 | 16 |

---

## Caso 4: Análise Avançada com xG

### Dados Disponíveis (2017+)

```python
# Expected Goals (xG) disponível para temporadas recentes
recent = df[df['season_period'] >= '2017-2018']

# Overperformance vs xG
recent['xG_diff'] = recent['Performance_Gls'] - recent['Expected_xG']

print("Seasons where CR7 overperformed xG:")
print(recent[recent['xG_diff'] > 5][['season_period', 'team', 'Performance_Gls', 'Expected_xG', 'xG_diff']])
```

### DAX Measure

```dax
xG_Overperformance = 
IF(
    NOT(ISBLANK([Expected_xG])),
    [Performance_Gls] - [Expected_xG],
    BLANK()
)
```

---

## Caso 5: Dashboards Prontos

### Dashboard 1: Overview da Carreira

**Visuais:**
1. **Card:** Total de Gols (só ligas)
2. **Card:** Total de Assistências
3. **Card:** Média Gols/90min
4. **Gráfico de Barras:** Gols por Time
5. **Gráfico de Linha:** Gols por Temporada
6. **Tabela:** Top 10 temporadas (ordenado por gols)

**Filtros:**
- `is_domestic_league = TRUE`
- Slicer: `season_period`

### Dashboard 2: Análise de Eficiência

**Visuais:**
1. **Scatter Plot:** Minutos vs Gols (tamanho = Gols/90)
2. **Matriz:** Liga × Temporada (valores = Gols/90)
3. **Área Chart:** Evolução de xG, npxG, Gols
4. **KPI:** 
   - Atual: `Gols/90` da última temporada
   - Target: `Gols/90` da melhor temporada
   - Trend: Últimas 3 temporadas

**Filtros:**
- `age >= 25 AND age <= 35` (pico de carreira)

### Dashboard 3: Internacional vs Clubes

**Medidas DAX:**

```dax
Gols_Clubes = 
CALCULATE(
    SUM([Performance_Gls]),
    [is_domestic_league] = TRUE
)

Gols_Selecao = 
CALCULATE(
    SUM([Performance_Gls]),
    [is_domestic_league] = FALSE
)

Ratio_Clube_Selecao = 
DIVIDE([Gols_Clubes], [Gols_Selecao], 0)
```

**Visuais:**
- Gauge: % de gols em clubes vs seleção
- Donut: Distribuição Clubes/Internacional
- Tabela: Competições internacionais com >3 gols

---

## 🔧 Scripts Úteis

### Exportar para Excel com Formatação

```python
import pandas as pd

df = pd.read_csv('datalake/processed/enriched/cristiano_ronaldo_enriched.csv')

# Filtrar apenas ligas
leagues_only = df[df['is_domestic_league'] == True]

# Exportar com formatação
with pd.ExcelWriter('CR7_Leagues.xlsx', engine='openpyxl') as writer:
    leagues_only.to_excel(writer, sheet_name='Leagues', index=False)
    
    # Formatar
    workbook = writer.book
    worksheet = writer.sheets['Leagues']
    
    # Auto-width
    for column in worksheet.columns:
        max_length = 0
        column = [cell for cell in column]
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        worksheet.column_dimensions[column[0].column_letter].width = adjusted_width

print("✅ Excel exportado: CR7_Leagues.xlsx")
```

### Estatísticas por Década

```python
df['decade'] = (df['season_period'].str[:4].astype(int) // 10) * 10

stats_by_decade = df.groupby('decade').agg({
    'Performance_Gls': 'sum',
    'Performance_Ast': 'sum',
    'Playing_Time_Min': 'sum',
    'season_period': 'count'
}).rename(columns={'season_period': 'seasons'})

stats_by_decade['goals_per_90'] = (stats_by_decade['Performance_Gls'] * 90 / 
                                    stats_by_decade['Playing_Time_Min']).round(2)

print(stats_by_decade)
```

---

## 📖 Próximos Passos

1. **Automatizar coleta:** Agendar scraping semanal do FBref
2. **API REST:** Expor dados via Flask/FastAPI
3. **Machine Learning:** Prever declínio de performance
4. **Dashboard Web:** Criar versão Streamlit/Dash
5. **Comparador interativo:** App para comparar 2-4 jogadores lado a lado

---

**Dúvidas?** Consulte [docs/POWERBI_GUIDE.md](../POWERBI_GUIDE.md) ou abra uma issue!
