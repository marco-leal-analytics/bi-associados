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
| AGENCIA | int64 | category/int | Código da agência de relacionamento | {1, 2, 3, 4, 5} | Sem nome de agência associado; tratar como código categórico |
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

`data/2_gold/features.parquet`: as três entidades Silver consolidadas pela `CHAVE` (`build_features`, `src/features/consolidado.py`; `validate="one_to_one"` em cada `merge`, impondo a cardinalidade 1:1:1 da seção "Chave de integração") mais os campos abaixo, calculados em sequência (produtos/relacionamento → nível de movimentação → classificação → flags de oportunidade). 1000 linhas × 39 colunas. Metodologia e limiares completos em `regras_negocio.md`.

### 5.1 Indicadores de produtos (`src/features/produtos.py`)

| Campo derivado | Fórmula / origem | Tipo | Descrição |
|---|---|---|---|
| QTD_PRODUTOS | Contagem de "S" entre CONTA_CORRENTE, CARTAO, CREDITO, INVESTIMENTO, CONSORCIO, SEGURO | int (0–6) | Total de produtos ativos por associado (já calculado na Silver, seção 2) |
| INDICE_DIVERSIFICACAO | QTD_PRODUTOS / total de produtos possíveis (6) | float (0–1) | Proporção de produtos possuídos sobre o total |
| NIVEL_DIVERSIFICACAO | Faixas de QTD_PRODUTOS (`FAIXAS_DIVERSIFICACAO`) | category (ordenada) | "0 - Baixa" / "1 - Média" / "2 - Alta" (prefixo numérico para ordenação no Power BI) |

### 5.2 Tempo de relacionamento e faixa de renda (`src/features/associados.py`)

| Campo derivado | Fórmula / origem | Tipo | Descrição |
|---|---|---|---|
| TEMPO_RELACIONAMENTO_DIAS | DATA_REFERENCIA − DATA_ASSOCIACAO | Int64 (nulo se DATA_ASSOCIACAO_INVALIDA) | Dias desde a associação |
| TEMPO_RELACIONAMENTO_ANOS | TEMPO_RELACIONAMENTO_DIAS / 365,25 | Float64 (nulo se DATA_ASSOCIACAO_INVALIDA) | Anos de relacionamento, arredondado a 2 casas |
| FAIXA_RENDA | Faixa de RENDA_MENSAL (`FAIXAS_RENDA`) | category | "A - Até R$ 3.000" / "B - R$ 3.001 a R$ 8.000" / "C - R$ 8.001 a R$ 15.000" / "D - Acima de R$ 15.000" / "Não informado" (RENDA_MENSAL nula) |

### 5.3 Nível de movimentação (`src/features/movimentacao.py`)

| Campo derivado | Fórmula / origem | Tipo | Descrição |
|---|---|---|---|
| NIVEL_SALDO_MEDIO | Tercis de SALDO_MEDIO (`TERCIS_MOVIMENTACAO`) | category (ordenada) | Baixa / Média / Alta — classificação individual, antes da moda |
| NIVEL_PIX_MENSAL | Tercis de PIX_MENSAL | category (ordenada) | Idem, sobre PIX_MENSAL |
| NIVEL_COMPRAS_CARTAO | Tercis de COMPRAS_CARTAO | category (ordenada) | Idem, sobre COMPRAS_CARTAO |
| NIVEL_MOVIMENTACAO | Moda entre NIVEL_SALDO_MEDIO, NIVEL_PIX_MENSAL e NIVEL_COMPRAS_CARTAO; desempate por NIVEL_SALDO_MEDIO | category (ordenada) | Baixa / Média / Alta — nível final do associado |

### 5.4 Classificação (`src/features/classificacao.py`)

| Campo derivado | Fórmula / origem | Tipo | Descrição |
|---|---|---|---|
| SCORE_PRODUTOS | Percentil (rank pct) de INDICE_DIVERSIFICACAO | float (0–1) | Pilar "Produtos" do índice composto |
| SCORE_RELACIONAMENTO | Percentil de TEMPO_RELACIONAMENTO_ANOS; 0,5 (neutro) se nulo | Float64 (0–1) | Pilar "Relacionamento" |
| SCORE_SALDO | Percentil de SALDO_MEDIO | float (0–1) | Pilar "Saldo" |
| SCORE_UTILIZACAO | Média dos percentis de PIX_MENSAL e COMPRAS_CARTAO | float (0–1) | Pilar "Utilização" |
| CLASSIFICACAO_TEMPO_INDISPONIVEL | True quando TEMPO_RELACIONAMENTO_ANOS é nulo (SCORE_RELACIONAMENTO neutralizado) | bool | Sinalização de transparência — mesma lógica de DATA_ASSOCIACAO_INVALIDA |
| INDICE_CLASSIFICACAO | Soma ponderada dos quatro SCORE_* (`CLASSIFICACAO_PESOS`, 25% cada por padrão) | Float64 (0–1) | Índice composto de classificação |
| CLASSIFICACAO | INDICE_CLASSIFICACAO cortado em quartis (`CLASSIFICACAO_LABELS`) | category (ordenada) | "A - Inicial" / "B - Em Desenvolvimento" / "C - Maduro" / "D - Engajado" (prefixo alfabético para ordenação no Power BI) |

### 5.5 Flags de oportunidade (`src/features/oportunidades.py`)

Não são mutuamente exclusivas — ver `regras_negocio.md` (seção 6).

| Campo derivado | Fórmula / origem | Tipo | Descrição |
|---|---|---|---|
| FLAG_OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS | FAIXA_RENDA = "D - Acima de R$ 15.000" E QTD_PRODUTOS ≤ 2 | bool | Alta renda, mas poucos produtos contratados |
| FLAG_OPORTUNIDADE_BAIXA_UTILIZACAO | NIVEL_MOVIMENTACAO = Baixa E QTD_PRODUTOS ≥ 2 | bool | Já é cliente de mais de um produto, mas pouco ativo |
| FLAG_OPORTUNIDADE_POTENCIAL_CRESCIMENTO | CLASSIFICACAO = "B - Em Desenvolvimento" E NIVEL_MOVIMENTACAO ∈ {Média, Alta} | bool | Poucos produtos, mas já engajado financeiramente |

## Observação sobre os dados

Todos os dados disponibilizados são fictícios, criados exclusivamente para fins de avaliação técnica, sem relação com pessoas físicas ou jurídicas reais.
