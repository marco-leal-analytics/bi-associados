# Dicionário de Dados

Fonte dos requisitos: `docs/orientações.docx` (Desafio Técnico - Assistente de BI).
Fonte dos dados reais: `data/0_bronze/raw_associados.xlsx` (planilhas `Associados`, `Produtos`, `Movimentacao`, 1000 registros cada).

Todos os dados são fictícios, gerados para fins de avaliação técnica.

## Chave de integração

- **Campo:** `CHAVE`
- **Papel:** chave primária única em cada uma das três bases e chave estrangeira de junção entre elas.
- **Cardinalidade observada:** 1:1:1 — os conjuntos de `CHAVE` das três planilhas são idênticos (1 a 1000), sem órfãos em nenhuma direção. Não é necessário LEFT/RIGHT JOIN defensivo, mas a validação de integridade deve ser mantida no pipeline (ver `qualidade_dados.md`).

---

## 1. Base `Associados` (Bronze)

Informações cadastrais do associado.

| Campo | Tipo (origem) | Tipo (tratado) | Descrição | Domínio / Exemplo | Observações de qualidade |
|---|---|---|---|---|---|
| CHAVE | int64 | int64 | Identificador único do associado | 1 a 1000 | Sem nulos, sem duplicidade |
| NOME | string | string | Nome do associado | "Fernanda Sobrenome" | Apenas 10 nomes distintos para 1000 registros (Interpretação: Coluna criada de forma ficticia: Avaliar em base de dados reais) |
| AGENCIA | int64 | category/int | Código da agência de relacionamento | {1, 2, 3, 4, 5} | Sem nome de agência na fonte; tratar como código categórico. Nome de negócio (levantamento) disponível em `dim_agencia` (seção 6.7) |
| CIDADE | string | category (padronizada) | Cidade do associado | "Pato Branco", "Cascavel", "Chapecó", "Toledo", "Maringá" | **Inconsistência de categoria**: mesma cidade grafada de 3 formas — "Pato Branco", "P. Branco", "PATO BRANCO" — e "Chapeco" sem acentuação. Ver regra de padronização em `qualidade_dados.md` |
| DATA_ASSOCIACAO | datetime | datetime (date) | Data de entrada do associado na cooperativa/instituição | 2018-01-02 a 2026-12-26 | **37 registros com data futura** em relação à data de referência do pipeline — inválido para cálculo de tempo de relacionamento |
| RENDA_MENSAL | float64 | float64 | Renda mensal declarada | R$ 2.010 a R$ 29.972 | **12 registros nulos (1,2%)** |
| DATA_ASSOCIACAO_INVALIDA | — (não existe no Bronze) | bool | Sinaliza `DATA_ASSOCIACAO` futura em relação à `DATA_REFERENCIA` da rodada, sem alterar o valor original do campo | {True, False} | Adicionada em `clean_associados` (`src/cleaning/associados.py`); True para os 37 registros de data futura. Usada para mascarar `TEMPO_RELACIONAMENTO_*` como nulo na Gold |

## 2. Base `Produtos` (Bronze)

Produtos contratados pelo associado. Uma linha por `CHAVE`, colunas binárias de posse.

| Campo | Tipo (origem) | Tipo (tratado) | Descrição | Domínio | Observações |
|---|---|---|---|---|---|
| CHAVE | int64 | int64 | Chave do associado | 1 a 1000 | Sem nulos, sem duplicidade |
| CONTA_CORRENTE | string ("S"/"N") | bool | Possui conta corrente | {S, N} | Domínio limpo |
| CARTAO | string ("S"/"N") | bool | Possui cartão | {S, N} | Domínio limpo |
| CREDITO | string ("S"/"N") | bool | Possui produto de crédito | {S, N} | Domínio limpo |
| INVESTIMENTO | string ("S"/"N") | bool | Possui produto de investimento | {S, N} | Domínio limpo |
| CONSORCIO | string ("S"/"N") | bool | Possui consórcio | {S, N} | Domínio limpo |
| SEGURO | string ("S"/"N") | bool | Possui seguro | {S, N} | Domínio limpo |
| QTD_PRODUTOS | — (não existe no Bronze) | int64 | Contagem de produtos com "S" entre as seis colunas acima | 0 a 6 | Adicionada em `clean_produtos` (`src/cleaning/produtos.py`); mediana 3, 13 associados sem produto ativo, 21 com os 6 produtos |

Nenhum nulo, nenhuma duplicidade de `CHAVE`, nenhum valor fora do domínio {S, N} nas 1000 linhas.

## 3. Base `Movimentacao` (Bronze)

Indicadores de relacionamento financeiro. Uma linha por `CHAVE`.

| Campo | Tipo (origem) | Tipo (tratado) | Descrição | Faixa observada | Observações |
|---|---|---|---|---|---|
| CHAVE | int64 | int64 | Chave do associado | 1 a 1000 | Sem nulos, sem duplicidade |
| SALDO_MEDIO | int64 | float64 | Saldo médio em conta | R$ 744 a R$ 249.864 | Sem nulos, sem negativos |
| PIX_MENSAL | int64 | int64 | Quantidade de PIX realizados no mês | 0 a 100 | Sem nulos, sem negativos |
| COMPRAS_CARTAO | int64 | float64 | Valor de compras no cartão no mês | R$ 50 a R$ 19.994 | Sem nulos, sem negativos |
| SALDO_MEDIO_INVALIDO | — (não existe no Bronze) | bool | Sinaliza `SALDO_MEDIO` negativo, substituído por nulo em `SALDO_MEDIO` | {True, False} | Adicionada em `clean_movimentacao` (`src/cleaning/movimentacao.py`); nenhum registro sinalizado na base atual (sem negativos observados) |
| PIX_MENSAL_INVALIDO | — (não existe no Bronze) | bool | Sinaliza `PIX_MENSAL` negativo, substituído por nulo em `PIX_MENSAL` | {True, False} | Idem, sobre `PIX_MENSAL` |
| COMPRAS_CARTAO_INVALIDO | — (não existe no Bronze) | bool | Sinaliza `COMPRAS_CARTAO` negativo, substituído por nulo em `COMPRAS_CARTAO` | {True, False} | Idem, sobre `COMPRAS_CARTAO` |

---

## 4. Camada Silver

A Silver **não é uma única tabela consolidada** — são três parquets separados, um por entidade, cada um com o schema tratado descrito nas seções 1–3 (incluindo as colunas de sinalização `DATA_ASSOCIACAO_INVALIDA` e `*_INVALIDO`):

| Entidade | Arquivo | Linhas × Colunas |
|---|---|---|
| Associados | `data/1_silver/associados.parquet` | 1000 × 7 |
| Produtos | `data/1_silver/produtos.parquet` | 1000 × 8 |
| Movimentacao | `data/1_silver/movimentacao.parquet` | 1000 × 7 |

Gerados por `run_silver()` (`src/pipeline.py`), que aplica `clean_associados`/`clean_produtos`/`clean_movimentacao` (`src/cleaning/*.py`) sobre a leitura bruta. A junção pela `CHAVE` só acontece na camada Gold (seção 5), via `build_features()` — ver regras de padronização em `qualidade_dados.md`.

## 5. Campos Derivados (Gold / Features)

`data/2_gold/features.parquet` (tabela fato): as três entidades Silver consolidadas pela `CHAVE` (`build_features`, `src/features/consolidado.py`; `validate="one_to_one"` em cada `merge`, impondo a cardinalidade 1:1:1 da seção "Chave de integração") mais os campos abaixo, calculados em sequência (produtos/relacionamento → nível de movimentação → classificação → flags de oportunidade). 1000 linhas × 39 colunas. Metodologia e limiares completos em `regras_negocio.md`.

**Modelagem em estrela**: toda faixa/classe/classificação criada nesta etapa é gravada na fato como um **ID inteiro**, não como texto — o rótulo correspondente vive numa tabela de dimensão separada (seção 6), relacionada pelo ID no Power BI. Isso evita repetir a mesma string em cada uma das 1000 linhas da fato, reduzindo o tamanho do arquivo.

### 5.1 Indicadores de produtos (`src/features/produtos.py`)

| Campo derivado | Fórmula / origem | Tipo | Descrição |
|---|---|---|---|
| QTD_PRODUTOS | Contagem de "S" entre CONTA_CORRENTE, CARTAO, CREDITO, INVESTIMENTO, CONSORCIO, SEGURO | int (0–6) | Total de produtos ativos por associado (já calculado na Silver, seção 2) |
| INDICE_DIVERSIFICACAO | QTD_PRODUTOS / total de produtos possíveis (6) | float (0–1) | Proporção de produtos possuídos sobre o total |
| NIVEL_DIVERSIFICACAO_ID | Faixas de QTD_PRODUTOS (`FAIXAS_DIVERSIFICACAO`) | int64 (0–2) | FK para `dim_nivel_diversificacao` (seção 6.2) |

### 5.2 Tempo de relacionamento e faixa de renda (`src/features/associados.py`)

| Campo derivado | Fórmula / origem | Tipo | Descrição |
|---|---|---|---|
| TEMPO_RELACIONAMENTO_DIAS | DATA_REFERENCIA − DATA_ASSOCIACAO | Int64 (nulo se DATA_ASSOCIACAO_INVALIDA) | Dias desde a associação |
| TEMPO_RELACIONAMENTO_ANOS | TEMPO_RELACIONAMENTO_DIAS / 365,25 | Float64 (nulo se DATA_ASSOCIACAO_INVALIDA) | Anos de relacionamento, arredondado a 2 casas |
| FAIXA_RENDA_ID | Faixa de RENDA_MENSAL (`FAIXAS_RENDA`) | int64 (0–3 ou -1) | FK para `dim_faixa_renda` (seção 6.1); -1 quando RENDA_MENSAL é nula ("Não informado") |
| TEMPO_RELACIONAMENTO_FAIXA_ID | Faixa semestral (6 em 6 meses) de TEMPO_RELACIONAMENTO_ANOS (`FAIXAS_TEMPO_RELACIONAMENTO`) | int64 (0–17 ou -1) | FK para `dim_tempo_relacionamento` (seção 6.2); -1 quando TEMPO_RELACIONAMENTO_ANOS é nulo ("Não disponível", mesmos 37 registros de DATA_ASSOCIACAO_INVALIDA) |

### 5.3 Nível de movimentação (`src/features/movimentacao.py`)

| Campo derivado | Fórmula / origem | Tipo | Descrição |
|---|---|---|---|
| NIVEL_SALDO_MEDIO_ID | Tercis de SALDO_MEDIO (`TERCIS_MOVIMENTACAO`) | int64 (0–2) | FK para `dim_nivel_movimentacao` (seção 6.3) — classificação individual, antes da moda |
| NIVEL_PIX_MENSAL_ID | Tercis de PIX_MENSAL | int64 (0–2) | Idem, sobre PIX_MENSAL |
| NIVEL_COMPRAS_CARTAO_ID | Tercis de COMPRAS_CARTAO | int64 (0–2) | Idem, sobre COMPRAS_CARTAO |
| NIVEL_MOVIMENTACAO_ID | Moda entre NIVEL_SALDO_MEDIO_ID, NIVEL_PIX_MENSAL_ID e NIVEL_COMPRAS_CARTAO_ID; desempate por NIVEL_SALDO_MEDIO_ID | int64 (0–2) | FK para `dim_nivel_movimentacao` — nível final do associado |

### 5.4 Classificação (`src/features/classificacao.py`)

| Campo derivado | Fórmula / origem | Tipo | Descrição |
|---|---|---|---|
| SCORE_PRODUTOS | Percentil (rank pct) de INDICE_DIVERSIFICACAO | float (0–1) | Pilar "Produtos" do índice composto |
| SCORE_RELACIONAMENTO | Percentil de TEMPO_RELACIONAMENTO_ANOS; 0,5 (neutro) se nulo | Float64 (0–1) | Pilar "Relacionamento" |
| SCORE_SALDO | Percentil de SALDO_MEDIO | float (0–1) | Pilar "Saldo" |
| SCORE_PIX_MENSAL | Percentil (rank pct) de PIX_MENSAL | float (0–1) | Pilar "Pix Mensal" (quantidade de transações) |
| SCORE_COMPRAS_CARTAO | Percentil (rank pct) de COMPRAS_CARTAO | float (0–1) | Pilar "Compras no Cartão" (volume financeiro) |
| CLASSIFICACAO_TEMPO_INDISPONIVEL | True quando TEMPO_RELACIONAMENTO_ANOS é nulo (SCORE_RELACIONAMENTO neutralizado) | bool | Sinalização de transparência — mesma lógica de DATA_ASSOCIACAO_INVALIDA |
| INDICE_CLASSIFICACAO | Soma ponderada dos cinco SCORE_* (`CLASSIFICACAO_PESOS`, 20% cada por padrão) | Float64 (0–1) | Índice composto de classificação |
| CLASSIFICACAO_ID | INDICE_CLASSIFICACAO cortado em quartis (`DIM_CLASSIFICACAO`) | int64 (0–3) | FK para `dim_classificacao` (seção 6.4) |

### 5.5 Flags de oportunidade (`src/features/oportunidades.py`)

Não são mutuamente exclusivas — ver `regras_negocio.md` (seção 6).

| Campo derivado | Fórmula / origem | Tipo | Descrição |
|---|---|---|---|
| FLAG_OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS | FAIXA_RENDA_ID = 3 ("Acima de R$ 15.000") E QTD_PRODUTOS ≤ 2 | bool | Alta renda, mas poucos produtos contratados |
| FLAG_OPORTUNIDADE_BAIXA_UTILIZACAO | NIVEL_MOVIMENTACAO_ID = 0 ("Baixa") E QTD_PRODUTOS ≥ 2 | bool | Já é cliente de mais de um produto, mas pouco ativo |
| FLAG_OPORTUNIDADE_POTENCIAL_CRESCIMENTO | CLASSIFICACAO_ID = 1 ("Em Desenvolvimento") E NIVEL_MOVIMENTACAO_ID ∈ {1, 2} ("Média"/"Alta") | bool | Poucos produtos, mas já engajado financeiramente |

### 5.6 Tabela reduzida para o Power BI (`features_dashboard.parquet`)

`data/2_gold/features_dashboard.parquet`: projeção de `features.parquet` (seção 5) só com as colunas que alimentam algum visual das 4 páginas do dashboard (`regras_negocio.md`, seção 7), gerada por `build_dashboard_features` (`src/features/consolidado.py`) a partir de `DASHBOARD_COLUMNS` (`src/config/settings.py`) e persistida por `run_gold` (`src/pipeline.py`). 1000 linhas × 16 colunas, contra 41 colunas da fato completa — os campos deixados de fora são todos intermediários de cálculo (pilares `SCORE_*`, níveis individuais de movimentação, `INDICE_*`, colunas de produto por tipo, flags `*_INVALIDO` de qualidade) que já foram consumidos para produzir `CLASSIFICACAO_ID`/`FLAG_OPORTUNIDADE_*` e não têm visual próprio no desafio. Esta é a tabela recomendada para o import no Power BI (junto das cinco dimensões `dim_*_id`, da `dim_calendario` e da `dim_agencia`, seção 6); `features.parquet` continua disponível como fato completa/auditável.

| Coluna | Página que usa | Papel |
|---|---|---|
| CHAVE | Todas | Chave de linha / contagem de associados (Página 1) |
| AGENCIA | Página 2 | Associados por Agência |
| CIDADE | Página 2 | Associados por Cidade |
| RENDA_MENSAL | Página 1 | Renda Média |
| FAIXA_RENDA_ID | Página 2 | FK para `dim_faixa_renda` |
| SALDO_MEDIO | Página 1 | Saldo Médio |
| QTD_PRODUTOS | Página 1 | Produtos por Associado |
| DATA_ASSOCIACAO | Página 2 | FK para `dim_calendario` (associados por ano/mês de entrada) |
| TEMPO_RELACIONAMENTO_ANOS | Página 2 | Tempo de Relacionamento |
| TEMPO_RELACIONAMENTO_FAIXA_ID | Página 2 | FK para `dim_tempo_relacionamento` |
| DATA_ASSOCIACAO_INVALIDA | Todas (nota de rodapé) | Sinaliza os 37 registros excluídos do cálculo de tempo — ver `insights.md` |
| CLASSIFICACAO_ID | Página 3 | FK para `dim_classificacao` |
| CLASSIFICACAO_TEMPO_INDISPONIVEL | Página 3 (transparência) | Sinaliza score de relacionamento neutralizado |
| FLAG_OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS | Página 4 | Lista de oportunidade |
| FLAG_OPORTUNIDADE_BAIXA_UTILIZACAO | Página 4 | Lista de oportunidade |
| FLAG_OPORTUNIDADE_POTENCIAL_CRESCIMENTO | Página 4 | Lista de oportunidade |

## 6. Dimensões (Gold)

Tabelas auxiliares de de-para ID → descrição, construídas por `build_dimensions()` (`src/features/dimensoes.py`) e persistidas por `run_gold()` (`src/pipeline.py`). Cada uma tem duas colunas — `ID` (int64) e `DESCRICAO` (string) — e se relaciona com a fato (seção 5) pela coluna `*_ID` correspondente. Fonte de verdade dos pares ID/descrição: os `DIM_*` em `src/config/settings.py`.

### 6.1 `dim_faixa_renda.parquet`

| ID | DESCRICAO |
|---|---|
| 0 | Até R$ 3.000 |
| 1 | R$ 3.001 a R$ 8.000 |
| 2 | R$ 8.001 a R$ 15.000 |
| 3 | Acima de R$ 15.000 |
| -1 | Não informado |

### 6.2 `dim_tempo_relacionamento.parquet`

Faixas semestrais (6 em 6 meses) de `TEMPO_RELACIONAMENTO_ANOS`, cobrindo até 9 anos (108 meses) — folga sobre o máximo observado na base atual (~8,7 anos). Fonte de verdade: `DIM_TEMPO_RELACIONAMENTO`/`FAIXAS_TEMPO_RELACIONAMENTO` (`src/config/settings.py`). Calculada por `add_faixa_tempo_relacionamento` (`src/features/associados.py`) a partir de `TEMPO_RELACIONAMENTO_ANOS` já em meses.

| ID | DESCRICAO |
|---|---|
| 0 | 0 a 6 meses |
| 1 | 6 a 12 meses |
| 2 | 12 a 18 meses |
| 3 | 18 a 24 meses |
| 4 | 24 a 30 meses |
| 5 | 30 a 36 meses |
| 6 | 36 a 42 meses |
| 7 | 42 a 48 meses |
| 8 | 48 a 54 meses |
| 9 | 54 a 60 meses |
| 10 | 60 a 66 meses |
| 11 | 66 a 72 meses |
| 12 | 72 a 78 meses |
| 13 | 78 a 84 meses |
| 14 | 84 a 90 meses |
| 15 | 90 a 96 meses |
| 16 | 96 a 102 meses |
| 17 | Acima de 102 meses |
| -1 | Não disponível |

### 6.3 `dim_nivel_diversificacao.parquet`

| ID | DESCRICAO |
|---|---|
| 0 | Baixa |
| 1 | Média |
| 2 | Alta |

### 6.4 `dim_nivel_movimentacao.parquet`

Compartilhada por `NIVEL_SALDO_MEDIO_ID`, `NIVEL_PIX_MENSAL_ID`, `NIVEL_COMPRAS_CARTAO_ID` e `NIVEL_MOVIMENTACAO_ID` (seção 5.3) — mesmo domínio.

| ID | DESCRICAO |
|---|---|
| 0 | Baixa |
| 1 | Média |
| 2 | Alta |

### 6.5 `dim_classificacao.parquet`

| ID | DESCRICAO |
|---|---|
| 0 | Inicial |
| 1 | Em Desenvolvimento |
| 2 | Maduro |
| 3 | Engajado |

A ordem crescente do ID já reflete a ordem de negócio (pior → melhor, ou mais curto → mais longo em `dim_tempo_relacionamento`) em todas as cinco dimensões desta seção — útil para ordenar eixos/legendas no Power BI sem depender de texto.

### 6.6 `dim_calendario.parquet`

Única dimensão da Gold que não vem de `DIM_*` (`src/config/settings.py`) nem de cálculo sobre os dados dos associados: é a projeção de uma fonte externa bruta, `data/0_bronze/raw_Dim_Calendario.xlsx` (aba `Dim_Calendario`, 45 colunas, ~28.850 linhas, anos 2000–2078, mais uma aba `Dim_Feriado` não utilizada neste projeto).

`build_dim_calendario` (`src/features/calendario.py`) lê a fonte bruta e reduz o resultado em duas dimensões:

- **Colunas**: das 45 originais (granularidade de dia da semana, feriado, bimestre, quadrimestre), mantém só as 10 em `DIM_CALENDARIO_COLUNAS` — nenhuma das 4 páginas do dashboard (`regras_negocio.md`, seção 7) precisa de granularidade diária/semanal/feriado; a única necessidade é agrupar `DATA_ASSOCIACAO` por ano/mês/trimestre/semestre (Página 2).
- **Linhas**: das ~79 safras completas (2000–2078), mantém só os anos entre `min(ANO(DATA_ASSOCIACAO), ANO(DATA_REFERENCIA))` e `max(ANO(DATA_ASSOCIACAO), ANO(DATA_REFERENCIA))`, com uma folga de `CALENDARIO_ANOS_BUFFER` (1 ano) para cada lado — evita relacionamento órfão se a base de associados for regenerada com datas um pouco fora do intervalo atual (2018–2026), sem carregar as safras completas do arquivo bruto. A função levanta `ValueError` se a fonte bruta não cobrir algum ano necessário.

| Coluna | Tipo | Descrição |
|---|---|---|
| DATA | datetime (date) | Chave da dimensão — relaciona com `DASHBOARD_COLUMNS.DATA_ASSOCIACAO` na fato (`features_dashboard.parquet`) |
| ANO | int64 | Ano da data |
| MES | int64 | Mês (1–12) — também serve de coluna de ordenação para `NOME_MES` no Power BI |
| NOME_MES | string | Nome do mês por extenso ("Janeiro" ... "Dezembro") |
| NOME_MES_ABREVIADO | string | Nome do mês abreviado ("Jan" ... "Dez") |
| ANO_MES | string | Rótulo "MM/AAAA", útil como eixo contínuo de meses |
| TRIMESTRE | int64 | Trimestre (1–4) — ordenação de `NOME_TRIMESTRE` |
| NOME_TRIMESTRE | string | "T1" a "T4" |
| SEMESTRE | int64 | Semestre (1–2) — ordenação de `NOME_SEMESTRE` |
| NOME_SEMESTRE | string | "S1"/"S2" |

Diferente das quatro dimensões acima (FK por `*_ID` inteiro), o relacionamento desta dimensão com a fato é por data (`DATA` ↔ `DATA_ASSOCIACAO`), padrão usual de tabela calendário no Power BI.

### 6.7 `dim_agencia.parquet`

A Bronze traz só o código da agência (`AGENCIA`, seção 1) — `{1, 2, 3, 4, 5}`, sem nome associado. Diferente das dimensões 6.1–6.4 (calculadas sobre os próprios dados), esta é levantamento de negócio: nomes reais de agências da cooperativa **Sicredi Soma** (contexto do desafio — sede administrativa em Mariópolis-PR, atuação em 33 municípios do sudoeste do Paraná e oeste/meio-oeste de Santa Catarina, ~43 agências ao todo; pesquisa pública no site institucional, ago/2026).

Como o código `{1..5}` do desafio não referencia nenhuma agência real específica (cada código aparece distribuído por todas as cidades da base — não há relação 1:1 código↔cidade nos dados), os 5 códigos foram mapeados às agências confirmadas via pesquisa: 4 unidades em Pato Branco — cidade predominante em `CIDADE` — seguindo a convenção de nomenclatura do Sicredi (cidade + característica: bairro/via/shopping), mais 1 unidade regional para representar a área de atuação além da sede.

| AGENCIA | NOME_AGENCIA |
|---|---|
| 1 | Pato Branco - Centro |
| 2 | Pato Branco - Zona Norte |
| 3 | Pato Branco - Zona Sul |
| 4 | Pato Branco - PB Shopping |
| 5 | Clevelândia - Centro |

Fonte de verdade: `DIM_AGENCIA` (`src/config/settings.py`). Construída por `build_dim_agencia()` (`src/features/dimensoes.py`) e persistida por `run_gold()` (`src/pipeline.py`). Colunas `AGENCIA` (int64) e `NOME_AGENCIA` (string); relaciona-se com a fato diretamente pela coluna `AGENCIA` (mesmo padrão de `dim_calendario` — chave de negócio, não `*_ID` sintético).

## Observação sobre os dados

Todos os dados disponibilizados são fictícios, criados exclusivamente para fins de avaliação técnica, sem relação com pessoas físicas ou jurídicas reais.
