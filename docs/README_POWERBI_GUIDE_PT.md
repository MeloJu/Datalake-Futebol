# 📊 Guia Power BI para Análise de Futebol

> **Para quem vem do QuickSight:** Power BI funciona de forma similar, mas com algumas diferenças importantes em agregações e modelagem de dados. Este guia explica tudo que você precisa saber!

## 🎯 Índice

1. [Entendendo Agregações (Sum, Average, etc.)](#entendendo-agregações)
2. [Colunas vs Medidas](#colunas-vs-medidas)
3. [Como Importar os Dados Corretamente](#importar-dados)
4. [Visualizações Recomendadas](#visualizações-recomendadas)
5. [Erros Comuns e Como Evitar](#erros-comuns)
6. [Comparação QuickSight vs Power BI](#quicksight-vs-powerbi)

---

## 📈 Entendendo Agregações

### O que são agregações?

Quando você arrasta um campo numérico para uma visualização, Power BI **automaticamente aplica uma agregação**. Isso é **SEMPRE** necessário porque:

- Você tem múltiplas linhas (ex: CR7 tem 38 temporadas)
- Power BI precisa decidir como "juntar" esses valores
- Por padrão, usa **SUM (soma)**

### Tipos de Agregações Comuns

| Agregação | Quando Usar | Exemplo no Dataset |
|-----------|-------------|-------------------|
| **Sum** | Totais acumulados ao longo do tempo | Total de gols na carreira: SUM(Performance_Gls) = 603 |
| **Average** | Médias por temporada | Média de gols por temporada: AVERAGE(Performance_Gls) ≈ 16 |
| **Maximum** | Melhor temporada/desempenho | Temporada com mais gols: MAX(Performance_Gls) = 46 (2011-12) |
| **Minimum** | Pior temporada/início carreira | Temporada com menos gols: MIN(Performance_Gls) = 0 |
| **Count** | Quantidade de temporadas | Total de temporadas: COUNT(season) = 38 |
| **Count (Distinct)** | Quantidade de times/ligas | Times jogados: DISTINCTCOUNT(team) = 7 |

### ⚠️ Quando SUM é BOM

✅ **Use SUM para:**
- **Totais de carreira**: gols totais, assistências totais, jogos totais
- **Comparar volumes**: CR7 (603 gols) vs Kaká (XX gols)
- **Visualizar evolução acumulada**: linha do tempo de gols acumulados

**Exemplo:**
```
Card Visual: "Gols na Carreira"
Campo: Performance_Gls
Agregação: Sum
Resultado: 603 ✅ (correto!)
```

### ⚠️ Quando SUM é RUIM

❌ **NÃO use SUM para:**
- **Stats per-90**: `Per_90_Minutes_Gls` já é uma taxa calculada
- **Idades**: `age` não faz sentido somar
- **Percentuais**: `Expected_xG` dividido por jogos não deve ser somado

**Exemplo ERRADO:**
```
Card Visual: "Gols por 90min"
Campo: Per_90_Minutes_Gls
Agregação: Sum
Resultado: 27.3 ❌ (não faz sentido!)
```

**Exemplo CORRETO:**
```
Card Visual: "Média de Gols por 90min"
Campo: Per_90_Minutes_Gls
Agregação: Average
Resultado: 0.72 ✅ (média correta!)
```

---

## 🔢 Colunas vs Medidas

### Colunas (do CSV)
- São os **dados brutos** que você importou
- Cada linha tem um valor específico
- Ex: `Performance_Gls` tem valor diferente para cada temporada

### Medidas (calculadas no Power BI)

Medidas são **cálculos dinâmicos** que você cria. São mais poderosas que agregações simples!

#### Como Criar uma Medida

1. Clique com botão direito na tabela (painel direito)
2. Selecione "Nova Medida"
3. Digite a fórmula DAX

#### Medidas Essenciais para seu Dataset

```dax
// Total de Gols na Carreira
Total Gols = SUM('cristiano_ronaldo_enriched'[Performance_Gls])

// Média de Gols por Temporada
Média Gols Temporada = AVERAGE('cristiano_ronaldo_enriched'[Performance_Gls])

// Gols por 90min (Média Ponderada Correta)
Gols por 90min = 
    DIVIDE(
        SUM('cristiano_ronaldo_enriched'[Performance_Gls]),
        SUM('cristiano_ronaldo_enriched'[Playing_Time_Min]) / 90,
        0
    )

// Total de Temporadas
Total Temporadas = DISTINCTCOUNT('cristiano_ronaldo_enriched'[season])

// Total de Times
Total Times = DISTINCTCOUNT('cristiano_ronaldo_enriched'[team])

// Melhor Temporada (Nome + Gols)
Melhor Temporada = 
    VAR MelhorAno = 
        CALCULATE(
            MAX('cristiano_ronaldo_enriched'[season_period]),
            TOPN(1, ALL('cristiano_ronaldo_enriched'), [Performance_Gls], DESC)
        )
    VAR GolsMelhor = 
        CALCULATE(
            MAX('cristiano_ronaldo_enriched'[Performance_Gls]),
            'cristiano_ronaldo_enriched'[season_period] = MelhorAno
        )
    RETURN
        MelhorAno & ": " & FORMAT(GolsMelhor, "0") & " gols"

// Eficiência de Finalização (Goals / Shots)
Eficiência Finalização = 
    DIVIDE(
        SUM('cristiano_ronaldo_enriched'[Performance_Gls]),
        SUM('cristiano_ronaldo_enriched'[Performance_Sh]),
        0
    ) * 100 & "%"

// Taxa de Conversão xG
Taxa Conversão xG = 
    VAR GoalsReal = SUM('cristiano_ronaldo_enriched'[Performance_Gls])
    VAR GoalsEsperado = SUM('cristiano_ronaldo_enriched'[Expected_xG])
    RETURN
        DIVIDE(GoalsReal, GoalsEsperado, 0)
```

---

## 📥 Como Importar os Dados Corretamente

### Passo a Passo

1. **Abra Power BI Desktop**
2. **Home → Obter Dados → Texto/CSV**
3. **Selecione:** `datalake/processed/enriched/cristiano_ronaldo_enriched.csv`
4. **Na prévia, clique em "Transformar Dados"** (importante!)

### Transformações Essenciais no Power Query

No editor Power Query, faça essas alterações:

#### 1. Configurar Tipos de Dados Corretos

```
// Campos de Texto
- player: Texto
- team: Texto
- league: Texto
- nation: Texto
- pos: Texto
- season: Texto (não número!)
- season_period: Texto

// Campos Numéricos
- age: Número Decimal
- Performance_Gls: Número Decimal
- Performance_Ast: Número Decimal
- Playing_Time_MP: Número Inteiro
- Playing_Time_Min: Número Inteiro
- (todos os stats): Número Decimal

// Campos de Metadata
- meta_*: Texto
```

#### 2. Criar Colunas Calculadas Úteis

No Power Query, adicione:

```m
// Época (para agrupar temporadas)
Época = 
    if [season] <= "0910" then "Início de Carreira (até 2010)"
    else if [season] <= "1718" then "Auge (2010-2018)"
    else "Fase Atual (2018+)"

// Tipo de Competição
Tipo Competição = 
    if Text.Contains([league], "INT-") then "Seleção"
    else if Text.Contains([league], "Taça") or Text.Contains([league], "Supertaça") then "Copa"
    else "Liga"

// Liga Principal (simplificado)
Liga Principal = 
    if Text.Contains([league], "Premier League") then "Premier League"
    else if Text.Contains([league], "La Liga") then "La Liga"
    else if Text.Contains([league], "Serie A") then "Serie A"
    else if Text.Contains([league], "Pro League") then "Saudi Pro League"
    else "Outras"
```

#### 3. Clique em "Fechar e Aplicar"

---

## 📊 Visualizações Recomendadas

### 1. Card de Estatísticas Principais

**Visual:** Card (ou Card de Múltiplas Linhas)

```
Campos:
- Total Gols (medida SUM)
- Média Gols/Temporada (medida AVERAGE)
- Total Temporadas (medida DISTINCTCOUNT)
- Total Times (medida DISTINCTCOUNT)
```

**Como fazer:**
1. Arraste visual "Card" para a página
2. Arraste campo `Performance_Gls` para o card
3. Clique na seta ao lado de `Performance_Gls` → Agregação → Soma
4. Renomeie para "Total de Gols"

### 2. Gráfico de Linha: Evolução de Gols

**Visual:** Gráfico de Linhas

```
Eixo X: season_period (ordenar cronologicamente)
Eixo Y: Performance_Gls (Sum)
Legenda: team (para ver mudanças de time)
```

**Insight:** Veja os picos (2011-12: 46 gols) e transições entre times.

### 3. Gráfico de Barras: Gols por Liga

**Visual:** Gráfico de Barras Horizontais

```
Eixo Y: Liga Principal (ou league)
Eixo X: Performance_Gls (Sum)
Dica de Ferramenta: Total Temporadas (COUNT)
```

**Insight:** La Liga: 311 gols em 9 temporadas vs Premier League: 103 em 8 temporadas.

### 4. Tabela Comparativa: Estatísticas Avançadas

**Visual:** Tabela

```
Linhas: season_period
Valores:
- Performance_Gls (Sum) - renomear "Gols"
- Performance_Ast (Sum) - renomear "Assistências"  
- Playing_Time_MP (Sum) - renomear "Jogos"
- Per_90_Minutes_Gls (Average) - renomear "Gols/90"
- Expected_xG (Sum) - renomear "xG"
```

### 5. Gráfico de Dispersão: Gols vs xG

**Visual:** Gráfico de Dispersão

```
Eixo X: Expected_xG (Sum)
Eixo Y: Performance_Gls (Sum)
Legenda: team
Tamanho: Playing_Time_Min (Sum)
```

**Insight:** Pontos acima da linha diagonal = superou expectativa (mais gols que xG).

### 6. Dashboard de Comparação (Kaká vs CR7)

Para comparar dois jogadores:

1. **Importe ambos CSVs** (kaka_enriched.csv + cristiano_ronaldo_enriched.csv)
2. **No Power Query, combine as tabelas:**
   - Home → Acrescentar Consultas → Acrescentar Consultas como Nova
   - Selecione as duas tabelas
   - Isso cria uma tabela combinada

3. **Crie visuais com filtro de jogador:**
   ```
   Gráfico de Barras Agrupadas:
   Eixo X: player
   Eixo Y: Performance_Gls (Sum)
   ```

4. **Ou use segmentação de dados:**
   - Adicione visual "Segmentação de Dados"
   - Campo: player
   - Usuário pode alternar entre Kaká e CR7

---

## 🚫 Erros Comuns e Como Evitar

### Erro 1: Somar Médias (Per-90 Stats)

❌ **Errado:**
```
SUM(Per_90_Minutes_Gls) = 27.3
```

✅ **Correto:**
```
AVERAGE(Per_90_Minutes_Gls) = 0.72
```

### Erro 2: Duplicar Dados ao Importar

❌ **Problema:** Importar o mesmo arquivo duas vezes

✅ **Solução:** Use `deduplicate_player_data.py` antes de importar!

### Erro 3: Filtrar Temporadas Erradas

❌ **Problema:** Esquecer de filtrar copas/competições secundárias

✅ **Solução:** Use filtro no visual:
```
Filtros → Tipo Competição → "Liga" (se quiser apenas ligas domésticas)
```

### Erro 4: Comparar Números Absolutos de Épocas Diferentes

❌ **Problema:** Comparar gols de 2003 com 2023 (futebol mudou)

✅ **Solução:** Use métricas normalizadas:
- Gols por 90min
- xG overperformance
- Percentuais (assistências / chances criadas)

### Erro 5: Não Formatar Números

❌ **Problema:** Mostrar 0.7234567890 em visual

✅ **Solução:** 
1. Selecione o campo no visual
2. Formato → Casas Decimais → 2
3. Para percentuais: Formato → Percentual

---

## 🔄 QuickSight vs Power BI

| Aspecto | QuickSight | Power BI | Para seu Projeto |
|---------|-----------|----------|------------------|
| **Agregações** | Explícitas em cada campo | Automáticas (SUM padrão) | Sempre verifique qual agregação está ativa! |
| **Medidas** | Campos Calculados | Medidas DAX | Use DAX para cálculos complexos (melhor) |
| **Relacionamentos** | Menos comum | Essencial para múltiplas tabelas | Se comparar jogadores, crie tabela de dimensão |
| **Filtros** | Filtros visuais | Segmentações + Filtros página | Use segmentação para jogador/time |
| **Drilldown** | Limitado | Hierarquias nativas | Crie hierarquia: Época → Temporada → Time |
| **Performance** | Serverless (AWS) | Desktop local | Arquivos CSV pequenos = sem problema |

---

## 🎨 Template de Dashboard Recomendado

### Página 1: Visão Geral da Carreira

```
┌─────────────────────────────────────────────────┐
│  [Segmentação: Jogador]  [Filtro: Liga]        │
├──────────────┬──────────────┬───────────────────┤
│ TOTAL GOLS   │ TEMPORADAS   │ MÉDIA GOLS/TEMP   │
│    603       │      38      │      15.9         │
├──────────────┴──────────────┴───────────────────┤
│                                                  │
│     [Gráfico Linha: Evolução de Gols]          │
│                                                  │
├──────────────────────────────────────────────────┤
│  [Barras: Gols por Liga]  │ [Tabela: Top 10]   │
│                            │  Temporadas        │
└────────────────────────────┴────────────────────┘
```

### Página 2: Análise Avançada

```
┌─────────────────────────────────────────────────┐
│  [Dispersão: Gols vs xG]    │ [KPI: Conversão]  │
│                              │   +12% acima xG   │
├──────────────────────────────┴──────────────────┤
│                                                  │
│     [Matriz: Stats por Time/Temporada]         │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Página 3: Comparação (Kaká vs CR7)

```
┌─────────────────────────────────────────────────┐
│           KAKÁ           vs      CRISTIANO      │
├──────────────────────────────────────────────────┤
│  [Barras Agrupadas: Gols, Assists, Jogos]      │
├──────────────────────────────────────────────────┤
│  [Linha Dupla: Evolução Paralela]              │
├──────────────────────────────────────────────────┤
│  [Cards Lado a Lado: Stats Principais]         │
└─────────────────────────────────────────────────┘
```

---

## 🎓 Dicas Finais

### 1. Sempre Verifique a Agregação

Quando adicionar um campo numérico:
1. Veja a tag "(Sum)" ao lado do nome
2. Pergunte-se: "Faz sentido SOMAR isso?"
3. Se não, mude para Average, Max, ou crie medida

### 2. Use Medidas para Cálculos Importantes

Não confie em agregações simples para métricas críticas. Crie medidas!

### 3. Teste com Filtros

Sempre teste seus visuais com:
- Um jogador apenas
- Uma temporada apenas
- Uma liga apenas

Se os números não fizerem sentido, revise a agregação.

### 4. Documentação DAX

Para aprender mais DAX:
- https://dax.guide/
- Procure "DAX patterns" no Google
- Comece simples (SUM, AVERAGE) e evolua

### 5. Salve Versões

Salve `.pbix` com nomes descritivos:
- `futebol_dashboard_v1.pbix`
- `futebol_dashboard_v2_com_kaka.pbix`

---

## 📚 Recursos Adicionais

### Tutoriais em Português
- [Microsoft Learn - Power BI](https://learn.microsoft.com/pt-br/power-bi/)
- [DAX Basics - Português](https://www.daxpatterns.com/)

### Comunidade
- [Power BI Community (Inglês)](https://community.powerbi.com/)
- Procure "Power BI Brasil" no YouTube

### Datasets Deste Projeto

- `kaka_enriched.csv` - 18 temporadas, 49 colunas
- `cristiano_ronaldo_enriched.csv` - 38 temporadas, 603 gols (ligas domésticas)
- Todos têm **mesmo schema** (49 colunas) para fácil comparação

---

## ✅ Checklist Antes de Importar

- [ ] Rodou `deduplicate_player_data.py` para limpar duplicatas
- [ ] Arquivo CSV está em `datalake/processed/enriched/`
- [ ] Vai usar "Transformar Dados" (não "Carregar" direto)
- [ ] Vai configurar tipos de dados corretos (season = Texto!)
- [ ] Vai criar medidas essenciais (Total Gols, Média por Temporada)
- [ ] Sabe quando usar Sum vs Average vs outras agregações

---

**Dúvidas?** Teste importando o CSV e criando um Card simples com "Total Gols". Se mostrar 603 ✅, está correto! Se mostrar 11k ❌, tem duplicatas ou agregação errada.

Boa sorte com seu dashboard! 🚀⚽
