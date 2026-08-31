# Qualidade dos Dados

Estratégia de validação, profiling inicial (camada Bronze) e regras de tratamento/validação pós-transformação para as bases `Associados`, `Produtos` e `Movimentacao`.

## 1. Estratégia de qualidade

Validações em dois pontos do pipeline (Bronze → Validation → Cleaning → Silver → Features → Classification → Validation → Gold):

1. **Validação de entrada (pré-tratamento)**: garante que a base bruta está estruturalmente íntegra antes de qualquer transformação.
2. **Validação de saída (pós-tratamento)**: garante que a limpeza/enriquecimento não introduziu inconsistências e que a base está pronta para o Power BI.

Critérios de controle em ambos os pontos: **chave** (unicidade/integridade referencial), **duplicidades**, **nulos**, **tipos** e **cardinalidade/domínio** de categorias.

## 2. Avaliação inicial (Bronze) — resultado observado

Levantado sobre `data/0_bronze/raw_associados.xlsx` (1000 registros por planilha).

### Associados
- Nulos: `RENDA_MENSAL` com **12 registros nulos (1,2%)**. Demais campos sem nulos.
- Duplicidade: 0 `CHAVE` duplicada, 0 linha duplicada.
- Tipos: `CHAVE`/`AGENCIA` inteiros, `RENDA_MENSAL` float, `DATA_ASSOCIACAO` datetime — todos consistentes com o esperado.
- Cardinalidade/categorias:
  - `AGENCIA`: domínio fechado {1, 2, 3, 4, 5}, distribuição equilibrada (182 a 214 registros por agência).
  - `CIDADE`: **inconsistência de categoria** — 7 valores distintos representando 5 cidades reais:
    - "Pato Branco" (136) / "P. Branco" (165) / "PATO BRANCO" (132) → mesma cidade, 3 grafias (433 registros, 43% da base).
    - "Chapeco" (145) → sem acentuação (deveria ser "Chapecó").
    - "Cascavel" (150), "Toledo" (137), "Maringa" (135) → sem acento em "Maringá", mas sem outras variantes.
  - `NOME`: apenas 10 valores distintos para 1000 registros — esperado, é dado sintético (não indica erro de qualidade, mas não deve ser usado como dimensão de análise).
- Intervalo de datas: `DATA_ASSOCIACAO` entre 2018-01-02 e 2026-12-26. **37 registros (3,7%) com data de associação futura** em relação à data de execução do pipeline — logicamente inválido (associado não pode ter tempo de relacionamento negativo).

### Produtos
- Nulos: nenhum em nenhuma coluna.
- Duplicidade: 0 `CHAVE` duplicada.
- Domínio: todas as 6 colunas de produto restritas a {"S", "N"} — sem valores fora do domínio.

### Movimentação
- Nulos: nenhum em nenhuma coluna.
- Duplicidade: 0 `CHAVE` duplicada.
- Faixas de valor: `SALDO_MEDIO` [744, 249.864], `PIX_MENSAL` [0, 100], `COMPRAS_CARTAO` [50, 19.994] — sem negativos, sem outliers estruturais evidentes.

### Integridade referencial entre bases
- Conjunto de `CHAVE` idêntico (1 a 1000) nas três planilhas — **sem órfãos** em nenhuma direção. A junção pelas três chaves não deve gerar perda de linhas nem `NaN` por ausência de correspondência.

## 3. Regras de validação — pré-tratamento (Bronze)

| Regra | Critério de aprovação |
|---|---|
| Schema | Colunas esperadas presentes em cada planilha, com os tipos declarados no dicionário de dados |
| Unicidade de chave | `CHAVE` sem duplicidade em cada uma das três bases |
| Integridade referencial | Conjunto de `CHAVE` de `Produtos` e `Movimentacao` deve estar contido no conjunto de `Associados` (checar órfãos antes do merge) |
| Domínio binário | Colunas de produto (`CONTA_CORRENTE`...`SEGURO`) restritas a {"S", "N"} |
| Domínio numérico | `AGENCIA` ∈ {1,2,3,4,5}; `PIX_MENSAL`, `SALDO_MEDIO`, `COMPRAS_CARTAO`, `RENDA_MENSAL` ≥ 0 |
| Data plausível | `DATA_ASSOCIACAO` ≤ data de referência do pipeline (execução) |

## 4. Regras de tratamento (Limpeza)

| Campo | Problema | Regra de tratamento |
|---|---|---|
| CIDADE | Grafias múltiplas para a mesma cidade | Padronizar: `strip` + `title case` + normalização de acentuação, e aplicar dicionário de equivalência explícito (`"P. BRANCO"/"P. Branco"` → `"Pato Branco"`; `"Chapeco"` → `"Chapecó"`; `"Maringa"` → `"Maringá"`). Resultado: 5 categorias únicas. |
| NOME | Espaços/caixa inconsistentes em potencial | `strip` + capitalização padrão (`standardize_text`), sem alterar o conteúdo semântico. Sem teste de regressão dedicado — dado sintético (10 valores para 1000 registros, seção 2) não usado como dimensão de análise. |
| RENDA_MENSAL | 12 nulos | **Decisão adotada**: manter como nulo (sem imputação) e sinalizar com a categoria `FAIXA_RENDA = "Não informado"` na Gold, excluindo esses registros do denominador em análises percentuais de renda — evita viés de imputação sobre dado sintético. Ver `docs/regras_negocio.md` (seção 3). |
| DATA_ASSOCIACAO | 37 datas futuras | Não editar o dado de origem silenciosamente: sinalizar os registros com `DATA_ASSOCIACAO_INVALIDA = True` e excluí-los do cálculo de `TEMPO_RELACIONAMENTO` (tratado como nulo), mantendo o registro no restante da análise. Justificar no relatório de qualidade a decisão adotada. |
| CHAVE | Tipo | Garantir `int` em todas as bases antes do merge |
| Colunas de produto | "S"/"N" | Converter para booleano (`S` → `True`, `N` → `False`) para uso em cálculos (`QTD_PRODUTOS`) |

## 5. Validações — pós-tratamento (Silver/Gold)

| Regra | Critério de aprovação |
|---|---|
| Unicidade | Base consolidada com 1 linha por `CHAVE`, sem duplicidade |
| Completude de categorias | `CIDADE` com exatamente as categorias canônicas esperadas (nenhuma variante remanescente) |
| Nulos residuais | Apenas os campos com decisão explícita de manter nulo (ex.: `RENDA_MENSAL` não imputada) — qualquer nulo fora da lista aprovada reprova a validação |
| Datas | Nenhuma `TEMPO_RELACIONAMENTO_ANOS` negativa na base final (registros inválidos tratados conforme regra acima) |
| Domínio dos derivados | `QTD_PRODUTOS` ∈ [0,6]; `FAIXA_RENDA`, `NIVEL_MOVIMENTACAO`, `CLASSIFICACAO` sempre preenchidos com um valor do domínio definido em `regras_negocio.md` (sem categoria "Outro"/residual) |
| Contagem de linhas | Base Gold com o mesmo número de associados da base Bronze (1000), salvo exclusão documentada e justificada |

### 5.1 Resultado observado (pipeline implementado)

Todas as regras acima são hoje impostas em tempo de execução — via `ValueError` nas funções de `src/cleaning/*.py` e `validate="one_to_one"` no `merge` de `src/features/consolidado.py` (nenhuma passa silenciosamente) — e confirmadas por `tests/test_silver.py` e `tests/test_features.py`. Resultado medido sobre a execução atual do pipeline (`data/1_silver/*.parquet`, `data/2_gold/features.parquet`):

| Regra | Resultado observado |
|---|---|
| Unicidade de `CHAVE` | 1000 linhas, `CHAVE` única em Associados, Produtos, Movimentacao e na Gold consolidada |
| Categorias de `CIDADE` | Exatamente as 5 categorias canônicas na Silver (`Cascavel`, `Chapecó`, `Maringá`, `Pato Branco`, `Toledo`) — as 7 variantes de origem (seção 2) foram reduzidas a 5, sem sobra |
| Nulos residuais | `RENDA_MENSAL`: 12 nulos (únicos nulos herdados do Bronze). Na Gold, os nulos de `TEMPO_RELACIONAMENTO_DIAS`/`_ANOS` (37, um por `DATA_ASSOCIACAO_INVALIDA`) somam-se aos 12 de `RENDA_MENSAL` — todos os demais campos, incluindo os derivados, sem nulo |
| `DATA_ASSOCIACAO_INVALIDA` | 37 registros sinalizados (mesmos 37 da avaliação Bronze, seção 2) |
| `*_INVALIDO` (Movimentacao) | 0 registros sinalizados em `SALDO_MEDIO_INVALIDO`, `PIX_MENSAL_INVALIDO` e `COMPRAS_CARTAO_INVALIDO` — nenhum valor negativo na base real, regra preventiva sem ocorrência |
| `QTD_PRODUTOS` | Intervalo observado 0–6, dentro do domínio esperado |
| `FAIXA_RENDA = "Não informado"` | 12 registros (os mesmos de `RENDA_MENSAL` nula) |
| `CLASSIFICACAO_TEMPO_INDISPONIVEL` | 37 registros (os mesmos de `DATA_ASSOCIACAO_INVALIDA`) |
| Contagem de linhas | 1000 em cada Silver (Associados, Produtos, Movimentacao) e 1000 na Gold — nenhuma perda no `merge` pela `CHAVE` |

## 6. Métricas de qualidade a registrar no pipeline (log/relatório)

- % de nulos por campo, antes e depois do tratamento.
- Nº de duplicidades removidas (esperado: 0, mas o pipeline deve reportar mesmo quando zero).
- Nº de categorias de `CIDADE` antes/depois da padronização (7 → 5).
- Nº de registros com `DATA_ASSOCIACAO` inválida sinalizados.
- Nº de registros com `RENDA_MENSAL` nula (tratados ou preservados, conforme decisão adotada).

**Status:** `src/utils/logging.py` (`get_logger`) e `src/pipeline.py` já registram a observabilidade estrutural da execução — início/fim de cada etapa (ingestão, Silver, Gold), contagem de linhas por entidade, caminhos gerados e tempo total (ver README, item 13.04). As métricas de qualidade específicas listadas acima (nulos por campo, duplicidades removidas, categorias de `CIDADE` antes/depois etc.) ainda não são logadas individualmente — hoje são garantidas via `ValueError` nas funções de `src/cleaning/*.py` (que interrompem o pipeline em caso de violação) e cobertas pelos testes (`tests/test_silver.py`, `tests/test_features.py`), não por um relatório de métricas dedicado.
