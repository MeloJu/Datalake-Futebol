# 🎯 GUIA RÁPIDO: Power BI com Novo Dataset

## ✅ Seu Dataset Está Atualizado!

**Arquivo:** `cristiano_ronaldo_enriched.csv`
- ✅ 32 temporadas (todas as competições)
- ✅ Classificação por tipo: `competition_type`
- ✅ Flag de filtro: `is_domestic_league`

---

## 🔄 1. Refresh no Power BI

### Opção A: Reimportar (Recomendado)

1. **Deletar** fonte de dados antiga do CR7
2. **Início** → **Obter Dados** → **Texto/CSV**
3. Selecionar: `datalake\processed\enriched\cristiano_ronaldo_enriched.csv`
4. Clicar **Carregar**

### Opção B: Atualizar Fonte

1. **Transformar Dados** → **Editor do Power Query**
2. Clicar na fonte de dados
3. **Configurações da Fonte** → Atualizar caminho
4. **Atualizar Visualização**

---

## 📊 2. Criar Medidas DAX

Clique em **Nova Medida** e adicione:

### Medida 1: Gols em Ligas Domésticas

```dax
Domestic Goals = 
CALCULATE(
    SUM('cristiano_ronaldo_enriched'[Performance_Gls]), 
    'cristiano_ronaldo_enriched'[is_domestic_league] = TRUE()
)
```

### Medida 2: Gols Totais

```dax
Total Goals = SUM('cristiano_ronaldo_enriched'[Performance_Gls])
```

### Medida 3: Gols por 90 Minutos

```dax
Goals per 90 = AVERAGE('cristiano_ronaldo_enriched'[Per_90_Minutes_Gls])
```

### Medida 4: Gols Internacionais

```dax
International Goals = 
CALCULATE(
    SUM('cristiano_ronaldo_enriched'[Performance_Gls]), 
    'cristiano_ronaldo_enriched'[competition_type] = "International Competition"
)
```

---

## 📈 3. Criar/Atualizar Gráfico

### Scatter Chart (Gols vs Idade)

**Configuração:**
- **X Axis:** `age`
- **Y Axis:** `Domestic Goals` (medida DAX) OU `Total Goals`
- **Size:** `SUM(Playing_Time_Min)`
- **Legend:** `team`
- **Tooltips:** Adicione `competition_type`, `Performance_Ast`

**Filtros (opcional):**
- Adicione `is_domestic_league` ao painel de filtros
- Marque `TRUE` para mostrar apenas ligas

---

## 🎨 4. Adicionar Filtro de Competição

### Slicer (Segmentação de Dados)

1. **Inserir** → **Segmentação de Dados**
2. Selecionar campo: `competition_type`
3. Marque as competições que quer incluir:
   - ☑️ Domestic League
   - ☑️ International Competition
   - ☐ Continental Cup (se tivesse)
   - ☐ Domestic Cup (se tivesse)

**Resultado:**
- Gráfico atualiza automaticamente
- Você controla quais competições incluir!

---

## 🔥 5. Exemplos de Análise

### Análise 1: Apenas Ligas Domésticas

**Filtro:** `is_domestic_league = TRUE`

**Resultado esperado:**
- Total: 495 gols
- Pico: 46 gols (2011-2012, Real Madrid)
- Idade do pico: 26 anos

### Análise 2: Todas as Competições

**Filtro:** Nenhum

**Resultado esperado:**
- Total: 517 gols
- Inclui 22 gols pela seleção (Copas e Eurocopas)

### Análise 3: Só Seleção

**Filtro:** `competition_type = "International Competition"`

**Resultado esperado:**
- Total: 22 gols
- Idades: 18-37 anos

---

## 📊 6. Card com Estatísticas

**Card 1 - Gols em Ligas:**
- Medida: `Domestic Goals`
- Formato: Número inteiro

**Card 2 - Gols Totais:**
- Medida: `Total Goals`
- Formato: Número inteiro

**Card 3 - Gols por 90:**
- Medida: `Goals per 90`
- Formato: Decimal (2 casas)

**Card 4 - Temporadas:**
- Medida: `DISTINCTCOUNT(season_period)`

---

## 🎯 7. Tabela Detalhada

**Colunas:**
- `season_period`
- `age`
- `team`
- `competition_type`
- `Performance_Gls`
- `Performance_Ast`
- `Playing_Time_MP`

**Ordenar por:** `season_period` (crescente)

---

## 💡 Dicas

### Colorir por Tipo de Competição

No gráfico:
- **Legend:** Mudar de `team` para `competition_type`
- **Cores:**
  - Azul: Domestic League
  - Verde: International Competition

### Tooltip Customizado

Adicionar aos Tooltips:
- `competition_type`
- `Performance_Ast` (assistências)
- `Per_90_Minutes_Gls` (gols/90)
- `league` (nome da liga)

### Drill-down

Criar hierarquia:
1. `season_period` (ano)
2. `competition_type` (tipo)
3. `team` (time)

---

## ✅ Validação Rápida

**Valores esperados para CR7:**

| Métrica | Valor |
|---------|-------|
| Total gols (tudo) | 517 |
| Gols em ligas | 495 |
| Gols internacionais | 22 |
| Temporadas | 32 |
| Pico (ligas) | 46 gols (2011-2012) |

Se os valores estiverem diferentes, verifique:
1. Arquivo importado está correto?
2. Medidas DAX estão corretas?
3. Filtros aplicados?

---

## 🆚 Comparar com Outros Jogadores

**Gerar dataset do Messi:**
```bash
python scripts/enrich_player_v3.py "Lionel Messi"
```

**No Power BI:**
1. Importar `lionel_messi_enriched.csv`
2. **Transformar Dados** → **Acrescentar Consultas**
3. Combinar CR7 + Messi
4. Gráfico agora mostra ambos!

---

## 📝 Checklist Final

- [ ] Dataset reimportado no Power BI
- [ ] Medidas DAX criadas (`Domestic Goals`, `Total Goals`)
- [ ] Gráfico Scatter atualizado
- [ ] Filtro `competition_type` adicionado
- [ ] Valores validados (495 gols em ligas)
- [ ] Tooltip customizado
- [ ] Cards com estatísticas

---

**🎉 Pronto! Agora você tem controle total sobre a análise!**
