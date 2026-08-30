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

Nenhum nulo, nenhuma duplicidade de `CHAVE`, nenhum valor fora do domínio {S, N} nas 1000 linhas.

## 3. Base `Movimentacao` (Bronze)

Indicadores de relacionamento financeiro. Uma linha por `CHAVE`.

| Campo | Tipo (origem) | Tipo (tratado) | Descrição | Faixa observada | Observações |
|---|---|---|---|---|---|
| CHAVE | int64 | int64 | Chave do associado | 1 a 1000 | Sem nulos, sem duplicidade |
| SALDO_MEDIO | int64 | float64 | Saldo médio em conta | R$ 744 a R$ 249.864 | Sem nulos, sem negativos |
| PIX_MENSAL | int64 | int64 | Quantidade de PIX realizados no mês | 0 a 100 | Sem nulos, sem negativos |
| COMPRAS_CARTAO | int64 | float64 | Valor de compras no cartão no mês | R$ 50 a R$ 19.994 | Sem nulos, sem negativos |

---

## 4. Base Consolidada (Silver)

Resultado do `merge` das três bases por `CHAVE` (inner join — conjuntos de chave idênticos, então equivale a full match).

`CHAVE, NOME, AGENCIA, CIDADE, DATA_ASSOCIACAO, RENDA_MENSAL, CONTA_CORRENTE, CARTAO, CREDITO, INVESTIMENTO, CONSORCIO, SEGURO, SALDO_MEDIO, PIX_MENSAL, COMPRAS_CARTAO`

Regras de padronização aplicadas antes da consolidação: ver `qualidade_dados.md`.

## 5. Campos Derivados (Gold / Features)

Calculados a partir da base Silver — ver metodologia e limiares completos em `regras_negocio.md`.

| Campo derivado | Fórmula / origem | Tipo | Descrição |
|---|---|---|---|
| QTD_PRODUTOS | Contagem de "S" entre CONTA_CORRENTE, CARTAO, CREDITO, INVESTIMENTO, CONSORCIO, SEGURO | int (0–6) | Total de produtos ativos por associado |
| TEMPO_RELACIONAMENTO_DIAS | DATA_REFERENCIA − DATA_ASSOCIACAO | int | Dias desde a associação |
| TEMPO_RELACIONAMENTO_ANOS | TEMPO_RELACIONAMENTO_DIAS / 365,25 | float | Anos de relacionamento (arredondado para exibição) |
| FAIXA_RENDA | Faixa de RENDA_MENSAL (ver regras de negócio) | category | Até R$3.000 / R$3.001–R$8.000 / R$8.001–R$15.000 / Acima de R$15.000 |
| NIVEL_MOVIMENTACAO | Moda entre os tercis de SALDO_MEDIO, PIX_MENSAL e COMPRAS_CARTAO, desempate por SALDO_MEDIO | category | Baixa / Média / Alta |
| CLASSIFICACAO | Índice composto por percentil (INDICE_CLASSIFICACAO) das quatro dimensões — Produtos, Relacionamento, Saldo, Utilização — cortado em quartis | category (ordenada) | "A - Inicial" / "B - Em Desenvolvimento" / "C - Maduro" / "D - Engajado" (prefixo alfabético para ordenação no Power BI) |
| FLAG_OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS | FAIXA_RENDA = "Acima de R$ 15.000" E QTD_PRODUTOS ≤ 2 | bool | Ver `regras_negocio.md` (seção 6) |
| FLAG_OPORTUNIDADE_BAIXA_UTILIZACAO | NIVEL_MOVIMENTACAO = Baixa E QTD_PRODUTOS ≥ 2 | bool | Ver `regras_negocio.md` (seção 6) |
| FLAG_OPORTUNIDADE_POTENCIAL_CRESCIMENTO | CLASSIFICACAO = "Em Desenvolvimento" E NIVEL_MOVIMENTACAO ∈ {Média, Alta} | bool | Ver `regras_negocio.md` (seção 6) |

## Observação sobre os dados

Todos os dados disponibilizados são fictícios, criados exclusivamente para fins de avaliação técnica, sem relação com pessoas físicas ou jurídicas reais.
