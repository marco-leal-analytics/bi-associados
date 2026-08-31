# Regras de Negócio

Metodologia de cálculo dos indicadores, classificação de associados e critérios de oportunidade. Baseado nos exemplos do desafio técnico (`docs/orientações.docx`) e nos limiares (quartis/tercis) observados no profiling da base real — ver `qualidade_dados.md`. Os limiares fixos abaixo (tercis de movimentação, faixas de renda e diversificação) foram calculados sobre a base Bronze e **validados sobre a Silver tratada** (`TERCIS_MOVIMENTACAO`, `src/config/settings.py`) — a limpeza não altera `SALDO_MEDIO`/`PIX_MENSAL`/`COMPRAS_CARTAO` (nenhum registro negativo foi encontrado, ver `qualidade_dados.md`), então os tercis recalculados sobre a Silver coincidem com os observados no Bronze. Já `CLASSIFICACAO` (seção 5) não usa limiar fixo: é recalculada dinamicamente a cada execução (percentil sobre a base corrente), continuando válida mesmo se a distribuição dos dados mudar.

## 1. Quantidade de Produtos

**Fórmula:** contagem de "S" entre as colunas `CONTA_CORRENTE, CARTAO, CREDITO, INVESTIMENTO, CONSORCIO, SEGURO`.

- Intervalo: 0 a 6 produtos.
- Distribuição observada na base: mediana em 3 produtos; 13 associados sem nenhum produto ativo; 21 associados com os 6 produtos.

## 2. Tempo de Relacionamento

**Fórmula:** `DATA_REFERENCIA − DATA_ASSOCIACAO`, em dias e convertido para anos (`dias / 365,25`).

- `DATA_REFERENCIA` = data de execução do pipeline (não uma data fixa no código, para o indicador continuar válido a cada nova rodada). Capturada uma única vez em `run_pipeline()` (`src/pipeline.py`) e propagada tanto para a sinalização de `DATA_ASSOCIACAO_INVALIDA` (Silver) quanto para o cálculo de `TEMPO_RELACIONAMENTO_*` (Gold), garantindo que as duas etapas usem o mesmo "hoje" dentro de uma mesma rodada; pode ser fixada explicitamente (`reference_date`) para reexecução reprodutível.
- Registros com `DATA_ASSOCIACAO` futura (37 na base atual) têm tempo de relacionamento tratado como nulo/inválido (ver `qualidade_dados.md`) e não entram no cálculo de médias nem na classificação por tempo.

## 3. Faixa de Renda

Faixas fixas definidas no desafio técnico (não são quartis calculados, são os cortes solicitados):

| Faixa | Intervalo |
|---|---|
| Até R$ 3.000 | RENDA_MENSAL ≤ 3.000 |
| R$ 3.001 a R$ 8.000 | 3.000 < RENDA_MENSAL ≤ 8.000 |
| R$ 8.001 a R$ 15.000 | 8.000 < RENDA_MENSAL ≤ 15.000 |
| Acima de R$ 15.000 | RENDA_MENSAL > 15.000 |

Registros com `RENDA_MENSAL` nula não recebem faixa (categoria "Não informado") e são excluídos do denominador em análises percentuais de renda.

Na implementação, a Gold não grava o rótulo da faixa em texto: `FAIXA_RENDA_ID` guarda o ID (0 a 3, na mesma ordem da tabela acima; -1 para "Não informado") e o rótulo vive na dimensão `dim_faixa_renda.parquet` (`DIM_FAIXA_RENDA`, `src/config/settings.py`; ver `dicionario_dados.md`, seção 6.1) — os intervalos e a regra de negócio são os mesmos da tabela acima, só a representação física muda (ID em vez de string, reduzindo o tamanho da fato).

## 4. Nível de Movimentação (indicador de apoio à classificação)

Como os três indicadores de movimentação (`SALDO_MEDIO`, `PIX_MENSAL`, `COMPRAS_CARTAO`) têm escalas muito diferentes, cada um é primeiro classificado em Baixa/Média/Alta pelos seus próprios tercis (33º e 66º percentil), e o `NIVEL_MOVIMENTACAO` do associado é a **moda** (classificação mais frequente) entre os três; em caso de empate, prevalece a classificação de `SALDO_MEDIO` (indicador mais estável de relacionamento financeiro).

Tercis de referência (`TERCIS_MOVIMENTACAO`, `src/config/settings.py`), calculados sobre a base Bronze e confirmados idênticos sobre a Silver tratada (ver nota introdutória):

| Indicador | Baixa (≤ P33) | Média (P33–P66) | Alta (> P66) |
|---|---|---|---|
| SALDO_MEDIO | ≤ 78.900 | 78.900 – 163.530 | > 163.530 |
| PIX_MENSAL | ≤ 32 | 32 – 66 | > 66 |
| COMPRAS_CARTAO | ≤ 6.745 | 6.745 – 13.131 | > 13.131 |

## 5. Classificação dos Associados

### 5.1 Técnicas avaliadas

As regras sequenciais manuais descritas na primeira versão deste documento (top-down, "primeira regra satisfeita vence") serviam apenas como exemplo do desafio técnico. Testadas sobre a base Gold real (`data/2_gold/features.parquet`, 1000 associados), elas jogavam **83,1%** dos associados na regra de fallback ("Em Desenvolvimento"), porque as regras 1–4 exigem AND de 2–3 condições simultâneas e cobrem poucas combinações — um resultado pouco informativo para o gráfico de distribuição da Página 3 do dashboard. Por isso a metodologia foi revista:

| Abordagem | Avaliação |
|---|---|
|
| **Índice composto por percentil, com corte em quartis** *(adotada)* | Cada associado recebe uma pontuação de 0 a 1 combinando as dimensões pedidas no desafio (Produtos, Relacionamento, Saldo, Utilização — esta última desdobrada em Pix Mensal e Compras no Cartão, ver seção 5.2); a base inteira é então dividida em quartis dessa pontuação. Solução determinística entre execuções (sem aleatoriedade, sem variável-alvo a definir a priori), e por construção produz quatro grupos de tamanho comparável — resolvendo o desbalanceamento das regras sequenciais e sendo diretamente interpretável ao negócio. Avaliar com stakeholders, e verificar se alguma dimensão possui algum peso maior ou preferencial, isso produzirá estimativas e quebras de regra mais aderentes às estratégias da Cooperativa. |

### 5.2 Metodologia adotada — Índice de Classificação

Cada associado recebe uma pontuação por **percentil (rank percentual, 0 a 1)** em cada uma das cinco dimensões:

| Dimensão | Indicador-base | Coluna do pilar |
|---|---|---|
| Produtos | `INDICE_DIVERSIFICACAO` (item 1) | `SCORE_PRODUTOS` |
| Relacionamento | `TEMPO_RELACIONAMENTO_ANOS` (item 2) | `SCORE_RELACIONAMENTO` |
| Saldo | `SALDO_MEDIO` | `SCORE_SALDO` |
| Pix Mensal | percentil de `PIX_MENSAL` | `SCORE_PIX_MENSAL` |
| Compras no Cartão | percentil de `COMPRAS_CARTAO` | `SCORE_COMPRAS_CARTAO` |

A dimensão "Utilização" do desafio original foi desdobrada em dois pilares independentes — Pix Mensal e Compras no Cartão — em vez de um único score médio entre os dois. `PIX_MENSAL` é uma métrica de **quantidade** (número de transações no mês) e `COMPRAS_CARTAO` é uma métrica de **volume financeiro** (valor movimentado no cartão); são bases de naturezas distintas, e uma média entre percentis de bases distintas mascarava a contribuição individual de cada uma ao índice.

`INDICE_CLASSIFICACAO` = soma ponderada dos cinco pilares, pesos em `CLASSIFICACAO_PESOS` (`src/config/settings.py`) — 20% cada por padrão, já que nenhuma das cinco dimensões tem prioridade documentada sobre as demais no desafio.

Associados com `TEMPO_RELACIONAMENTO_ANOS` nulo (data futura inválida, 37 registros — ver seção 2) recebem `SCORE_RELACIONAMENTO = 0,5` (mediana neutra), para não penalizar nem favorecer artificialmente o índice, com sinalização `CLASSIFICACAO_TEMPO_INDISPONIVEL = True` para transparência no dashboard — mesma lógica de transparência já usada em `DATA_ASSOCIACAO_INVALIDA`.

`CLASSIFICACAO` é obtida dividindo `INDICE_CLASSIFICACAO` em quartis (25% cada), rotulados em ordem crescente de pontuação, do domínio `DIM_CLASSIFICACAO`:

**Inicial** (Q1) → **Em Desenvolvimento** (Q2) → **Maduro** (Q3) → **Engajado** (Q4)

Na implementação, `CLASSIFICACAO_ID` guarda o ID de 0 (Inicial) a 3 (Engajado) — mesma ordem de negócio da lista acima — e o rótulo vive na dimensão `dim_classificacao.parquet` (`DIM_CLASSIFICACAO`, `src/config/settings.py`; ver `dicionario_dados.md`, seção 6.4), mesmo padrão de `FAIXA_RENDA_ID` (seção 3).

### 5.3 Validação sobre a base Gold real

Sobre os mesmos 1000 registros: distribuição exatamente 250/250/250/250 entre as quatro categorias (por construção dos quartis), e as médias dos cinco indicadores brutos crescem monotonicamente de Inicial para Engajado — evidência de que o índice composto captura uma progressão de relacionamento coerente, não é um artefato da fórmula:

| Classificação | QTD_PRODUTOS (méd.) | TEMPO_RELACIONAMENTO_ANOS (méd.) | SALDO_MEDIO (méd.) | PIX_MENSAL (méd.) | COMPRAS_CARTAO (méd.) |
|---|---|---|---|---|---|
| Inicial | 2,1 | 2,7 | 70.643 | 38,9 | 7.952 |
| Em Desenvolvimento | 2,9 | 3,7 | 109.010 | 48,2 | 9.615 |
| Maduro | 3,2 | 4,9 | 137.643 | 53,9 | 10.364 |
| Engajado | 3,8 | 6,0 | 176.164 | 60,0 | 12.229 |

## 6. Critérios de Oportunidade

| Oportunidade | Critério (rótulo de negócio) | Critério (implementação, por ID) | Coluna na Gold |
|---|---|---|---|
| Alta renda e poucos produtos | FAIXA_RENDA = "Acima de R$ 15.000" **E** QTD_PRODUTOS ≤ 2 | `FAIXA_RENDA_ID = 3` **E** `QTD_PRODUTOS ≤ 2` | `FLAG_OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS` |
| Baixa utilização dos serviços | NIVEL_MOVIMENTACAO = Baixa **E** QTD_PRODUTOS ≥ 2 (já é cliente, mas pouco ativo — diferente de "Inicial") | `NIVEL_MOVIMENTACAO_ID = 0` **E** `QTD_PRODUTOS ≥ 2` | `FLAG_OPORTUNIDADE_BAIXA_UTILIZACAO` |
| Potencial de crescimento | CLASSIFICACAO = "Em Desenvolvimento" **E** NIVEL_MOVIMENTACAO ∈ {Média, Alta} (produtos ainda poucos, mas já engajado financeiramente) | `CLASSIFICACAO_ID = 1` **E** `NIVEL_MOVIMENTACAO_ID ∈ {1, 2}` | `FLAG_OPORTUNIDADE_POTENCIAL_CRESCIMENTO` |

Essas flags não são mutuamente exclusivas: um associado pode aparecer em mais de uma lista de oportunidade simultaneamente. Implementadas em `add_flags_oportunidade` (`src/features/oportunidades.py`), parametrizadas em `OPORTUNIDADE_*` (`src/config/settings.py`) — esses parâmetros comparam diretamente os IDs das dimensões (seções 3, 4 e 5.2; `dicionario_dados.md`, seção 6), não texto.

## 7. Uso nas páginas do Power BI

- **Página 1 (Visão Geral):** Total de Associados, Renda Média, Saldo Médio, Produtos por Associado (médias e totais gerais, calculados sobre a base Gold).
- **Página 2 (Relacionamento):** Associados por Agência, por Cidade (usando `CIDADE` já padronizada), por Faixa de Renda, por Tempo de Relacionamento.
- **Página 3 (Classificação):** Distribuição percentual e quantitativa entre Inicial / Em Desenvolvimento / Maduro / Engajado.
- **Página 4 (Oportunidades):** As três listas de oportunidade da seção 6.

Nenhuma das quatro páginas usa os campos intermediários de cálculo (pilares `SCORE_*`, níveis individuais de movimentação, `INDICE_*`, colunas de produto por tipo, flags `*_INVALIDO`) — por isso o import recomendado no Power BI é `data/2_gold/features_dashboard.parquet`, a projeção de `features.parquet` só com as colunas da tabela acima (`build_dashboard_features`, `src/features/consolidado.py`; lista completa em `dicionario_dados.md`, seção 5.6), relacionada às quatro dimensões por ID (`dim_*.parquet`, seção 6 de `dicionario_dados.md`) e à `dim_calendario.parquet` (seção 6.5, relacionada por data via `DATA_ASSOCIACAO`) em modelo estrela.
