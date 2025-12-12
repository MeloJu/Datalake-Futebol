# 📊 Dicionário de Variáveis - Dataset de Futebol

> **Guia completo das 49 colunas** nos arquivos enriched (ex: `cristiano_ronaldo_enriched.csv`)

## 🎯 Para sua análise: Gols x Idade x Performance

### Variáveis Principais

| Variável | Tipo | Descrição | Exemplo | Usar para |
|----------|------|-----------|---------|-----------|
| `age` | Decimal | Idade do jogador na temporada | 23.5 | **Eixo X** - analisar evolução por idade |
| `Performance_Gls` | Decimal | **Gols marcados** na temporada | 46 | **Eixo Y** - métrica principal |
| `Per_90_Minutes_Gls` | Decimal | **Gols por 90 minutos** | 0.95 | **Performance normalizada** - melhor que total! |
| `Playing_Time_Min` | Inteiro | Minutos jogados | 3.270 | Contexto - quanto jogou |
| `Playing_Time_MP` | Inteiro | Jogos (matches played) | 38 | Contexto - quantidade de jogos |

### 🎨 Visualizações Recomendadas

#### 1. Gráfico de Dispersão: Gols vs Idade
```
Eixo X: age
Eixo Y: Performance_Gls
Tamanho da Bolha: Playing_Time_Min (quanto jogou)
Cor: team (para ver mudanças de time)
```
**Insight:** Veja o pico de performance (geralmente 27-31 anos para atacantes).

#### 2. Linha Dupla: Gols e Gols/90 por Idade
```
Eixo X: age
Eixo Y Primário: Performance_Gls (barras)
Eixo Y Secundário: Per_90_Minutes_Gls (linha)
```
**Insight:** Às vezes gols totais caem (menos jogos), mas eficiência (gols/90) continua alta!

#### 3. Gráfico de Área: Performance ao Longo da Carreira
```
Eixo X: season_period (ordenado)
Eixo Y: Performance_Gls + Performance_Ast (empilhado)
Marcador: age (rótulo de dados)
```
**Insight:** Veja gols + assists combinados com idade anotada.

---

## 📋 Todas as 49 Colunas Explicadas

### 🔑 Identificadores (5 colunas)

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `player` | Texto | Nome do jogador | "Cristiano Ronaldo" |
| `team` | Texto | Time que jogou | "Real Madrid" |
| `league` | Texto | Liga/competição | "ESP-La Liga" |
| `season` | Texto | Código da temporada | "1112" (2011-12) |
| `season_period` | Texto | Temporada legível | "2011-2012" |

### 👤 Informações Pessoais (3 colunas)

| Coluna | Tipo | Descrição | Exemplo | Usar para |
|--------|------|-----------|---------|-----------|
| `nation` | Texto | Nacionalidade (3 letras) | "POR" | Filtrar por país |
| `pos` | Texto | Posição principal | "FW" (atacante) | Comparar por posição |
| `age` | Decimal | Idade na temporada | 26.5 | **Análise por idade!** |

**Códigos de Posição:**
- `FW` = Forward (Atacante)
- `MF` = Midfielder (Meio-campo)
- `DF` = Defender (Defensor)
- `GK` = Goalkeeper (Goleiro)
- Combinações: `FW,MF` = pode jogar nas duas

---

### ⏱️ Tempo de Jogo (4 colunas - Prefixo `Playing_Time_`)

| Coluna | Tipo | Descrição | Exemplo | Usar para |
|--------|------|-----------|---------|-----------|
| `Playing_Time_MP` | Inteiro | **Matches Played** - Jogos disputados | 38 | Quantidade de jogos |
| `Playing_Time_Starts` | Inteiro | Jogos como titular | 35 | Titular vs reserva |
| `Playing_Time_Min` | Inteiro | **Minutos jogados** | 3.270 | Volume de jogo |
| `Playing_Time_90s` | Decimal | Equivalente a jogos de 90min | 36.3 | Normalizar stats |

**Exemplo de uso:**
```dax
// Taxa de Titularidade
Taxa Titular = 
    DIVIDE(
        SUM(Playing_Time_Starts),
        SUM(Playing_Time_MP),
        0
    ) * 100
```

---

### ⚽ Performance Ofensiva (9 colunas - Prefixo `Performance_`)

| Coluna | Tipo | Descrição | Exemplo | Usar para |
|--------|------|-----------|---------|-----------|
| `Performance_Gls` | Decimal | **GOLS MARCADOS** 🎯 | 46 | **Métrica principal!** |
| `Performance_Ast` | Decimal | **Assistências** 🎁 | 12 | Contribuição criativa |
| `Performance_G+A` | Decimal | Gols + Assistências | 58 | Participação total |
| `Performance_G-PK` | Decimal | Gols exceto pênaltis | 38 | Gols "puros" |
| `Performance_PK` | Decimal | Pênaltis convertidos | 8 | Especialista em pênaltis |
| `Performance_PKatt` | Decimal | Pênaltis tentados | 10 | Cobrou quantos |
| `Performance_CrdY` | Decimal | Cartões amarelos | 4 | Disciplina |
| `Performance_CrdR` | Decimal | Cartões vermelhos | 0 | Expulsões |
| `Performance_Sh` | Decimal | **Finalizações totais** | 200 | Volume de chutes |

**Exemplo de cálculo:**
```dax
// Eficiência de Finalização
Eficiência Chute = 
    DIVIDE(
        SUM(Performance_Gls),
        SUM(Performance_Sh),
        0
    ) * 100 & "%"
    
// Resultado: 23% (46 gols / 200 chutes)
```

---

### 🎯 Expected Goals - xG (4 colunas - Prefixo `Expected_`)

**O que é xG?** Probabilidade de um chute virar gol baseado em posição, ângulo, tipo de passe, etc.

| Coluna | Tipo | Descrição | Exemplo | Usar para |
|--------|------|-----------|---------|-----------|
| `Expected_xG` | Decimal | **Expected Goals** - Gols esperados | 38.5 | Comparar com gols reais |
| `Expected_npxG` | Decimal | xG excluindo pênaltis | 32.0 | xG "puro" |
| `Expected_xAG` | Decimal | Expected Assisted Goals | 10.2 | Qualidade das assistências |
| `Expected_npxG+xAG` | Decimal | Soma dos dois acima | 42.2 | Contribuição esperada total |

**Análise importante:**
```dax
// Overperformance de xG (marcar mais que o esperado)
xG Overperformance = 
    SUM(Performance_Gls) - SUM(Expected_xG)
    
// Se positivo = finalizador acima da média
// Se negativo = teve sorte ou baixa eficiência
```

**Exemplo CR7 temporada 2011-12:**
- Gols reais: 46
- xG esperado: 38.5
- Overperformance: +7.5 (20% acima do esperado!) 🔥

---

### 🏃 Progressão de Bola (5 colunas - Prefixo `Progression_`)

**Como o jogador avança a bola pelo campo.**

| Coluna | Tipo | Descrição | Exemplo | Usar para |
|--------|------|-----------|---------|-----------|
| `Progression_PrgC` | Decimal | **Progressões com bola** (dribles) | 45 | Habilidade de drible |
| `Progression_PrgP` | Decimal | **Passes progressivos** | 89 | Criação de jogo |
| `Progression_PrgR` | Decimal | **Recepções progressivas** | 120 | Movimentação sem bola |
| `Progression_Carries` | Decimal | Conduções totais | 200 | Volume de dribles |
| `Progression_TotDist` | Decimal | Distância total conduzida (yards) | 1.500 | Quanto carrega a bola |

**Para Wingers/Atacantes:**
- `Progression_PrgC` alto = dribla muito
- `Progression_PrgR` alto = sabe se posicionar

**Para Meio-campistas:**
- `Progression_PrgP` alto = cria jogadas
- `Progression_Carries` alto = carrega o time

---

### 📏 Stats por 90 Minutos (13 colunas - Prefixo `Per_90_Minutes_`)

**IMPORTANTE:** Essas são **taxas/médias**, não totais!

| Coluna | Tipo | Descrição | Exemplo | Como Agregar |
|--------|------|-----------|---------|--------------|
| `Per_90_Minutes_Gls` | Decimal | **Gols por 90min** | 0.95 | **AVERAGE** (não SUM!) |
| `Per_90_Minutes_Ast` | Decimal | Assistências por 90min | 0.28 | AVERAGE |
| `Per_90_Minutes_G+A` | Decimal | Gols+Assists por 90min | 1.23 | AVERAGE |
| `Per_90_Minutes_G-PK` | Decimal | Gols sem pênaltis por 90min | 0.78 | AVERAGE |
| `Per_90_Minutes_G+A-PK` | Decimal | G+A sem pênaltis por 90min | 1.06 | AVERAGE |
| `Per_90_Minutes_xG` | Decimal | xG por 90min | 0.79 | AVERAGE |
| `Per_90_Minutes_xAG` | Decimal | xAG por 90min | 0.21 | AVERAGE |
| `Per_90_Minutes_xG+xAG` | Decimal | xG+xAG por 90min | 1.00 | AVERAGE |
| `Per_90_Minutes_npxG` | Decimal | xG sem pênaltis por 90min | 0.66 | AVERAGE |
| `Per_90_Minutes_npxG+xAG` | Decimal | Soma acima | 0.87 | AVERAGE |
| `Per_90_Minutes_PrgC` | Decimal | Progressões por 90min | 0.93 | AVERAGE |
| `Per_90_Minutes_PrgP` | Decimal | Passes progressivos por 90min | 1.84 | AVERAGE |
| `Per_90_Minutes_PrgR` | Decimal | Recepções progressivas por 90min | 2.48 | AVERAGE |

**⚠️ NUNCA USE SUM nesses campos!**

```dax
// ERRADO ❌
Total Gols por 90 = SUM(Per_90_Minutes_Gls) // = 27.3 (não faz sentido!)

// CORRETO ✅
Média Gols por 90 = AVERAGE(Per_90_Minutes_Gls) // = 0.72 (correto!)
```

**Para calcular corretamente na carreira inteira:**
```dax
// Gols por 90min (toda carreira)
Gols por 90min Carreira = 
    DIVIDE(
        SUM(Performance_Gls),
        SUM(Playing_Time_90s),
        0
    )
```

---

### 🏆 Metadata (10 colunas - Prefixo `meta_`)

**Informações biográficas e contextuais do jogador.**

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `meta_date_of_birth` | Texto | Data de nascimento | "05/02/1985" |
| `meta_place_of_birth` | Texto | Local de nascimento | "Funchal, Portugal" |
| `meta_height` | Texto | Altura | "1,87 m" |
| `meta_nationality` | Texto | Nacionalidade completa | "Portugal" |
| `meta_position_detail` | Texto | Posição detalhada | "Left Winger" |
| `meta_foot` | Texto | Pé preferido | "Ambos" / "Direito" / "Esquerdo" |
| `meta_transfermarkt_url` | Texto | URL perfil Transfermarkt | "https://..." |
| `meta_notes` | Texto | Notas adicionais | "5× Ballon d'Or" |
| `meta_missing_seasons` | Texto | Temporadas não cobertas | "Saudi Pro League 2023-2025" |
| `meta_honors` | Texto | Títulos principais (JSON) | Lista de conquistas |

---

## 🎯 Exemplos de Análises: Gols x Idade x Performance

### Análise 1: Curva de Idade

**Pergunta:** Em que idade o jogador atinge o pico?

**Medidas DAX:**
```dax
// Gols por Idade
Gols por Idade = 
    CALCULATE(
        SUM(Performance_Gls),
        ALLEXCEPT('cristiano_ronaldo_enriched', 'cristiano_ronaldo_enriched'[age])
    )

// Eficiência por Idade
Eficiência por Idade = 
    CALCULATE(
        AVERAGE(Per_90_Minutes_Gls),
        ALLEXCEPT('cristiano_ronaldo_enriched', 'cristiano_ronaldo_enriched'[age])
    )
```

**Visual:**
- Gráfico de Linha
- Eixo X: `age` (agrupado por inteiro: 18, 19, 20...)
- Eixo Y: `Performance_Gls` (Sum)
- Linha 2: `Per_90_Minutes_Gls` (Average)

**Insight esperado:** Pico geralmente aos 27-29 anos para atacantes.

---

### Análise 2: Performance vs Volume de Jogo

**Pergunta:** Ele mantém eficiência quando joga muito?

**Visual: Dispersão**
```
Eixo X: Playing_Time_Min (volume de jogo)
Eixo Y: Per_90_Minutes_Gls (eficiência)
Tamanho: Performance_Gls (resultado absoluto)
Cor: age (idade)
```

**Insight:** 
- Bolhas grandes no canto superior direito = jogou muito E foi eficiente
- Cores quentes (vermelho = mais velho) concentradas onde? (mantém nível?)

---

### Análise 3: Gols Reais vs Esperados por Fase da Carreira

**Medidas:**
```dax
// Fase da Carreira
Fase Carreira = 
    SWITCH(
        TRUE(),
        'cristiano_ronaldo_enriched'[age] < 23, "Revelação",
        'cristiano_ronaldo_enriched'[age] < 28, "Desenvolvimento",
        'cristiano_ronaldo_enriched'[age] < 33, "Auge",
        "Veterano"
    )

// xG Overperformance
xG Over = SUM(Performance_Gls) - SUM(Expected_xG)
```

**Visual: Barras Agrupadas**
```
Eixo X: Fase Carreira
Barra 1: Performance_Gls (Sum) - Gols Reais
Barra 2: Expected_xG (Sum) - Gols Esperados
Rótulo de dados: xG Over (diferença)
```

**Insight:** Ele supera xG mais no auge ou quando jovem?

---

### Análise 4: Matriz Idade x Liga

**Pergunta:** Performance varia por idade E liga?

**Visual: Matriz**
```
Linhas: age (agrupado: 18-22, 23-27, 28-32, 33+)
Colunas: league
Valores: 
  - Performance_Gls (Sum)
  - Per_90_Minutes_Gls (Average)
  - Playing_Time_MP (Sum) - contexto
```

**Formatação condicional:**
- Maior que 0.8 gols/90 = verde
- 0.5-0.8 = amarelo
- Menor que 0.5 = vermelho

**Insight:** Ele teve queda de rendimento na mudança de liga? Ou foi apenas idade?

---

### Análise 5: Contribuição Total por Temporada

**Medida:**
```dax
// Participação em Gols (Gols + Assistências)
Participação Total = 
    SUM(Performance_Gls) + SUM(Performance_Ast)

// Participação por 90min
Participação por 90 = 
    DIVIDE(
        [Participação Total],
        SUM(Playing_Time_90s),
        0
    )
```

**Visual: Gráfico de Área Empilhada**
```
Eixo X: season_period
Área 1: Performance_Gls (gols)
Área 2: Performance_Ast (assistências)
Marcador de Linha: age (rótulo superior)
```

**Insight:** Quando ele começou a dar mais assistências? Mudança de estilo com a idade?

---

## 📊 Tabela Resumo: Qual Variável Usar?

| O que você quer mostrar | Variável Principal | Agregação | Contexto Adicional |
|--------------------------|-------------------|-----------|-------------------|
| **Total de gols na carreira** | `Performance_Gls` | SUM | `Playing_Time_MP` (jogos) |
| **Eficiência por jogo** | `Per_90_Minutes_Gls` | AVERAGE | `Playing_Time_Min` (minutos) |
| **Pico de performance** | `Performance_Gls` + `age` | SUM por idade | `season_period` (quando) |
| **Evolução ao longo do tempo** | `Performance_Gls` | SUM por temporada | `team` (mudanças) |
| **Qualidade vs Quantidade** | `Expected_xG` vs `Performance_Gls` | SUM ambos | Diferença = qualidade |
| **Assistências + Gols** | `Performance_G+A` | SUM | `Per_90_Minutes_G+A` (média) |
| **Performance sem pênaltis** | `Performance_G-PK` | SUM | `Performance_PK` (quantos) |
| **Contribuição criativa** | `Expected_xAG` | SUM | `Performance_Ast` (real) |
| **Habilidade de drible** | `Progression_PrgC` | SUM | `Progression_Carries` (volume) |
| **Disciplina** | `Performance_CrdY` + `Performance_CrdR` | SUM | Por 90min (taxa) |

---

## 🎨 Template de Dashboard: Gols x Idade x Performance

### Layout Sugerido

```
┌─────────────────────────────────────────────────┐
│ [TÍTULO] Análise: Gols x Idade x Performance    │
│ [Filtro: Liga] [Filtro: Fase Carreira]         │
├──────────────┬──────────────┬───────────────────┤
│ Pico Idade   │ Gols no Auge │ Média Gols/90     │
│    27 anos   │     46       │     0.95          │
├──────────────┴──────────────┴───────────────────┤
│                                                  │
│  [Dispersão] Gols vs Idade                      │
│  - Tamanho: Minutos jogados                     │
│  - Cor: Time (ver mudanças)                     │
│                                                  │
├──────────────────────────────────────────────────┤
│  [Linha Dupla]          │ [Barras Agrupadas]    │
│  - Gols (barras)        │ - Gols Reais          │
│  - Gols/90 (linha)      │ - xG (esperado)       │
│  Eixo X: age            │ Eixo X: Fase Carreira │
├──────────────────────────────────────────────────┤
│  [Matriz] Idade x Liga                          │
│  - Linhas: Faixa Etária (18-22, 23-27...)      │
│  - Colunas: Liga                                │
│  - Valores: Gols/90 (formatação condicional)    │
└─────────────────────────────────────────────────┘
```

---

## ⚠️ Armadilhas Comuns

### 1. Somar Per-90 Stats
```
❌ SUM(Per_90_Minutes_Gls) = 27.3 (sem sentido!)
✅ AVERAGE(Per_90_Minutes_Gls) = 0.72
```

### 2. Comparar Idades em Ligas Diferentes
```
❌ "CR7 aos 35 na Itália = menos gols que aos 25 na Inglaterra"
⚠️ Liga diferente, time diferente, contexto diferente
✅ Use Per_90_Minutes para normalizar
```

### 3. Ignorar Minutos Jogados
```
❌ "Temporada X ele marcou só 18 gols"
✅ "Mas jogou apenas 1.800 minutos (20 jogos) = 0.9 gols/90"
```

### 4. Misturar Temporadas de Seleção
```
⚠️ World Cup = 6 jogos, Liga = 38 jogos
✅ Filtre por Tipo Competição (liga vs seleção)
```

---

## 🚀 Próximos Passos

1. **Importe o CSV** no Power BI
2. **Crie as medidas DAX** da seção "Análises"
3. **Monte o dashboard** com os visuais sugeridos
4. **Teste filtros** por idade, liga, time
5. **Compare jogadores** (Kaká vs CR7)

**Dúvida sobre alguma variável?** Teste assim:
```dax
// Medida de Teste
Teste Variavel = 
    CONCATENATEX(
        TOPN(5, 'cristiano_ronaldo_enriched', [season], ASC),
        [season] & ": " & [SUA_VARIAVEL],
        UNICHAR(10)
    )
```

Boa análise! 📊⚽
