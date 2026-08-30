# Regras de Negócio

Metodologia de cálculo dos indicadores, classificação de associados e critérios de oportunidade. Baseado nos exemplos do desafio técnico (`docs/orientações.docx`) e nos limiares (quartis/tercis) observados no profiling da base real — ver `qualidade_dados.md`. Os limiares abaixo são valores de referência calculados sobre a base Bronze e devem ser **recalculados sobre a base Silver/Gold já tratada** quando o pipeline for implementado.

## 1. Quantidade de Produtos

**Fórmula:** contagem de "S" entre as colunas `CONTA_CORRENTE, CARTAO, CREDITO, INVESTIMENTO, CONSORCIO, SEGURO`.

- Intervalo: 0 a 6 produtos.
- Distribuição observada na base: mediana em 3 produtos; 13 associados sem nenhum produto ativo; 21 associados com os 6 produtos.

## 2. Tempo de Relacionamento

**Fórmula:** `DATA_REFERENCIA − DATA_ASSOCIACAO`, em dias e convertido para anos (`dias / 365,25`).

- `DATA_REFERENCIA` = data de execução do pipeline (não uma data fixa no código, para o indicador continuar válido a cada nova rodada).
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

## 4. Nível de Movimentação (indicador de apoio à classificação)

Como os três indicadores de movimentação (`SALDO_MEDIO`, `PIX_MENSAL`, `COMPRAS_CARTAO`) têm escalas muito diferentes, cada um é primeiro classificado em Baixa/Média/Alta pelos seus próprios tercis (33º e 66º percentil), e o `NIVEL_MOVIMENTACAO` do associado é a **moda** (classificação mais frequente) entre os três; em caso de empate, prevalece a classificação de `SALDO_MEDIO` (indicador mais estável de relacionamento financeiro).

Tercis de referência (calculados sobre a base Bronze — recalcular após tratamento):

| Indicador | Baixa (< P33) | Média (P33–P66) | Alta (> P66) |
|---|---|---|---|
| SALDO_MEDIO | < 78.900 | 78.900 – 163.530 | > 163.530 |
| PIX_MENSAL | < 32 | 32 – 66 | > 66 |
| COMPRAS_CARTAO | < 6.745 | 6.745 – 13.131 | > 13.131 |

## 5. Classificação dos Associados

Avaliação **sequencial top-down**: a primeira regra satisfeita define a classificação. Isso evita sobreposição entre os critérios de exemplo do desafio (ex.: "4+ produtos" aparece tanto em Maduro quanto em Engajado).

| Ordem | Classificação | Critério |
|---|---|---|
| 1 | **Engajado** | QTD_PRODUTOS ≥ 5 **E** TEMPO_RELACIONAMENTO_ANOS > 3 **E** NIVEL_MOVIMENTACAO = Alta |
| 2 | **Maduro** | QTD_PRODUTOS ≥ 4 **E** TEMPO_RELACIONAMENTO_ANOS > 3 **E** NIVEL_MOVIMENTACAO ∈ {Média, Alta} |
| 3 | **Em Desenvolvimento** | QTD_PRODUTOS ∈ {2, 3} **E** TEMPO_RELACIONAMENTO_ANOS ≥ 2 |
| 4 | **Inicial** | QTD_PRODUTOS ≤ 1 **E** TEMPO_RELACIONAMENTO_ANOS < 2 |
| 5 | **Em Desenvolvimento** (regra de fallback) | Qualquer combinação não coberta pelas regras 1–4 (ex.: poucos produtos mas relacionamento antigo, ou muitos produtos mas movimentação baixa) |

A regra 5 é explícita para garantir que **todo** associado receba uma classificação do domínio {Inicial, Em Desenvolvimento, Maduro, Engajado}, sem categoria residual "Outro" no dashboard.

Associados com `TEMPO_RELACIONAMENTO_ANOS` nulo (data futura inválida) são classificados usando apenas `QTD_PRODUTOS` e `NIVEL_MOVIMENTACAO`, com sinalização `CLASSIFICACAO_TEMPO_INDISPONIVEL = True` para transparência no dashboard.

## 6. Critérios de Oportunidade

| Oportunidade | Critério proposto |
|---|---|
| Alta renda e poucos produtos | FAIXA_RENDA = "Acima de R$ 15.000" **E** QTD_PRODUTOS ≤ 2 |
| Baixa utilização dos serviços | NIVEL_MOVIMENTACAO = Baixa **E** QTD_PRODUTOS ≥ 2 (já é cliente, mas pouco ativo — diferente de "Inicial") |
| Potencial de crescimento | CLASSIFICACAO = "Em Desenvolvimento" **E** NIVEL_MOVIMENTACAO ∈ {Média, Alta} (produtos ainda poucos, mas já engajado financeiramente) |

Essas flags não são mutuamente exclusivas: um associado pode aparecer em mais de uma lista de oportunidade simultaneamente.

## 7. Uso nas páginas do Power BI

- **Página 1 (Visão Geral):** Total de Associados, Renda Média, Saldo Médio, Produtos por Associado (médias e totais gerais, calculados sobre a base Gold).
- **Página 2 (Relacionamento):** Associados por Agência, por Cidade (usando `CIDADE` já padronizada), por Faixa de Renda, por Tempo de Relacionamento.
- **Página 3 (Classificação):** Distribuição percentual e quantitativa entre Inicial / Em Desenvolvimento / Maduro / Engajado.
- **Página 4 (Oportunidades):** As três listas de oportunidade da seção 6.
