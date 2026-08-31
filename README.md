# bi-associados
Associados 360 | Business Intelligence &amp; Relationship Analytics — Solução completa de BI desenvolvida com Python, Excel, Parquet e Power BI para tratamento e qualidade de dados, análise de relacionamento, classificação de associados, identificação de oportunidades e geração de insights, com arquitetura Bronze → Silver → Gold e versionamento Git.

## Objetivo do Projeto

Construir um pipeline analítico completo (Bronze → Silver → Gold) para consolidar as bases de Associados, Produtos e Movimentação em uma visão única — "Associados 360" —, tratando e validando a qualidade dos dados, calculando indicadores de relacionamento e diversificação de produtos, classificando os associados por um índice de percentil e identificando oportunidades comerciais (ex.: alta renda com baixa utilização de produtos), com o resultado final consumido em um dashboard Power BI.

## Tecnologias Utilizadas

- **Python** — linguagem principal do pipeline (ingestão, limpeza, features, classificação e orquestração).
- **Pandas** — manipulação e transformação dos dados nas camadas Bronze, Silver e Gold.
- **PyArrow / Parquet** — formato de armazenamento colunar das camadas Silver e Gold.
- **Openpyxl** — leitura das planilhas Excel de origem (camada Bronze).
- **Power BI** — dashboard final de visualização e análise de insights.
- **Git** — versionamento do código e documentação do projeto.

## Regras de Classificação e Score de Utilização de Produtos

O `INDICE_CLASSIFICACAO` é um índice composto por percentil (0 a 1). Cada associado recebe uma pontuação percentual (rank 0–1) em cinco pilares, combinados por soma ponderada (20% cada, `CLASSIFICACAO_PESOS`):

| Dimensão | Indicador-base | Coluna do pilar |
|---|---|---|
| Produtos | `INDICE_DIVERSIFICACAO` | `SCORE_PRODUTOS` |
| Relacionamento | `TEMPO_RELACIONAMENTO_ANOS` | `SCORE_RELACIONAMENTO` |
| Saldo | `SALDO_MEDIO` | `SCORE_SALDO` |
| Pix Mensal | percentil de `PIX_MENSAL` | `SCORE_PIX_MENSAL` |
| Compras no Cartão | percentil de `COMPRAS_CARTAO` | `SCORE_COMPRAS_CARTAO` |

A dimensão "Utilização" pedida no desafio foi desdobrada em **Pix Mensal** (quantidade de transações) e **Compras no Cartão** (volume financeiro) em vez de um único score médio, por serem métricas de naturezas diferentes.

O `INDICE_CLASSIFICACAO` é então dividido em quartis, gerando `CLASSIFICACAO_ID` (0–3) em ordem crescente de pontuação:

**Inicial** (Q1) → **Em Desenvolvimento** (Q2) → **Maduro** (Q3) → **Engajado** (Q4)

A distribuição resultante é balanceada (250/250/250/250 em 1000 associados), com progressão monotônica dos indicadores brutos entre as categorias — evidência de que o índice reflete uma progressão real de relacionamento. Metodologia completa, em `docs/regras_negocio.md` (seção 5).

## Metodologia de Oportunidades

Três flags de oportunidade são calculadas na camada Gold (`FLAG_OPORTUNIDADE_*`, não mutuamente exclusivas):

| Oportunidade | Critério de negócio |
|---|---|
| Alta renda e poucos produtos | Faixa de renda "Acima de R$ 15.000" **e** até 2 produtos |
| Baixa utilização dos serviços | Nível de movimentação Baixa **e** 2+ produtos (já é cliente, mas pouco ativo) |
| Potencial de crescimento | Classificação "Em Desenvolvimento" **e** movimentação Média/Alta (poucos produtos, mas já engajado financeiramente) |

Complementarmente, a Página 4 do Power BI usa uma abordagem exploratória sobre o mesmo `INDICE_CLASSIFICACAO`: uma **matriz Faixa de Renda × Classificação**, com o score médio em cada célula — renda alta e score baixo aponta visualmente o quadrante de maior oportunidade, sem exigir um limiar fixo. A matriz filtra interativamente uma tabela de associados ordenada de forma ascendente pelo score, detalhando os cinco pilares `SCORE_*` de cada um. Sobre a base atual, a célula "Acima de R$ 15.000" × "Inicial" concentra 133 associados (13,3% da base) com o menor score médio (0,33) — o mesmo público identificado pela flag `FLAG_OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS`, agora navegável interativamente. Detalhes em `docs/regras_negocio.md` (seções 6–7) e `docs/insights.md`.

## Passo a Passo para Execução

1. **Pré-requisitos**: Python 3.10+ instalado e disponível no PATH (`python --version`), e Git para clonar/versionar o repositório.
2. **Obter o projeto**: clone ou copie o repositório e abra um terminal na **raiz do projeto** (a pasta que contém a pasta `src/`) — todos os comandos abaixo assumem esse diretório.
3. **Criar o ambiente virtual** (isola as dependências do projeto do Python global):
   ```
   python -m venv .venv
   ```
4. **Ativar o ambiente virtual**:
   - Windows (cmd/PowerShell): `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

   O prompt do terminal passa a exibir `(.venv)` quando a ativação funciona.
5. **Instalar as dependências** listadas em `requirements.txt` (`pandas`, `openpyxl`, `pyarrow`, `pytest`):
   ```
   pip install -r requirements.txt
   ```
6. **Conferir os dados de origem**: os arquivos Excel brutos devem existir em `data/0_bronze/` (`raw_associados.xlsx` com as abas Associados/Produtos/Movimentacao, e `raw_Dim_Calendario.xlsx`) — essa camada não é gerada pelo pipeline, é o ponto de partida.
7. **Executar o pipeline completo** (ingestão → Silver → Gold), sempre com `-m` para o Python resolver os imports absolutos do pacote `src`:
   ```
   python -m src.pipeline
   ```
   Nunca execute com `python src/pipeline.py` nem `cd src && python pipeline.py` — sem o `-m`, o Python não encontra o pacote `src` e falha com `ModuleNotFoundError: No module named 'src'`.
8. **Acompanhar a execução**: o log no terminal mostra timestamp, etapa (ingestão/Silver/Gold), contagem de linhas processadas e tempo total, via `src/utils/logging.py`.
9. **Conferir os resultados gerados**, em ordem:
   - `data/1_silver/associados.parquet`, `produtos.parquet`, `movimentacao.parquet` — camada Silver, dados tratados e validados.
   - `data/2_gold/features.parquet` — tabela fato completa (features, score e classificação consolidados).
   - `data/2_gold/features_dashboard.parquet` — projeção reduzida, só com as colunas usadas no Power BI.
   - `data/2_gold/dim_faixa_renda.parquet`, `dim_tempo_relacionamento.parquet`, `dim_nivel_diversificacao.parquet`, `dim_nivel_movimentacao.parquet`, `dim_classificacao.parquet`, `dim_calendario.parquet`, `dim_agencia.parquet` — tabelas de dimensão para o modelo em estrela.
10. **Rodar os testes automatizados** (valida qualidade, integridade referencial e regras de negócio sobre os dados gerados):
    ```
    pytest tests/ -q
    ```
11. **Abrir o dashboard**: com `data/2_gold/features_dashboard.parquet` e as dimensões `dim_*.parquet` gerados, abra o Power BI e importe/atualize essas tabelas (relacionadas por ID/data/agência conforme `docs/dicionario_dados.md`, seção 6).
12. **Reexecutar após mudanças**: qualquer alteração nos dados brutos (`data/0_bronze/`) ou no código em `src/` exige rodar novamente o passo 7 para atualizar Silver e Gold — o pipeline sempre reprocessa do zero, não é incremental.

## Estrutura dos Scripts Python

- **`src/pipeline.py`** — ponto de entrada do projeto (`python -m src.pipeline`); orquestra `run_ingestion` → `run_silver` → `run_gold` em `run_pipeline()`, captura `DATA_REFERENCIA` uma única vez por rodada e registra o log de cada etapa.
- **`src/config/settings.py`** — configuração central do projeto: caminhos (`PROJECT_ROOT`, `DATA_DIR`, `BRONZE_DIR`, `SILVER_DIR`, `GOLD_DIR`), nomes de abas/colunas esperadas, parâmetros de negócio (`FAIXAS_RENDA`, `TERCIS_MOVIMENTACAO`, `CLASSIFICACAO_PESOS`, `OPORTUNIDADE_*`) e os pares `DIM_*` usados nas tabelas de dimensão.
- **`src/io/excel.py`** — leitura genérica das planilhas Excel de origem (`read_sheet`, `load_sources`); único ponto do projeto que lê a camada Bronze.
- **`src/cleaning/common.py`** — funções de limpeza reutilizadas pelas três entidades: padronização de texto/categorias, validação de domínio, tratamento de nulos e duplicidades, conversão de tipos.
- **`src/cleaning/associados.py`** — limpeza da entidade Associados: padroniza `CIDADE`, sinaliza `DATA_ASSOCIACAO` futura (`DATA_ASSOCIACAO_INVALIDA`) e trata `RENDA_MENSAL`.
- **`src/cleaning/produtos.py`** — limpeza da entidade Produtos: valida domínio S/N, converte para booleano, valida `CHAVE` e calcula `QTD_PRODUTOS`.
- **`src/cleaning/movimentacao.py`** — limpeza da entidade Movimentação: converte métricas numéricas e sinaliza valores inválidos por coluna.
- **`src/features/produtos.py`** — calcula `INDICE_DIVERSIFICACAO` e `NIVEL_DIVERSIFICACAO_ID` a partir da quantidade de produtos.
- **`src/features/associados.py`** — calcula `TEMPO_RELACIONAMENTO_DIAS/ANOS`, `FAIXA_RENDA_ID` e `TEMPO_RELACIONAMENTO_FAIXA_ID`.
- **`src/features/movimentacao.py`** — calcula `NIVEL_MOVIMENTACAO_ID` (tercis de saldo, Pix e compras no cartão, combinados pela moda).
- **`src/features/classificacao.py`** — calcula o `INDICE_CLASSIFICACAO` (score de utilização de produtos) e `CLASSIFICACAO_ID`, conforme a metodologia descrita acima.
- **`src/features/oportunidades.py`** — calcula as três `FLAG_OPORTUNIDADE_*` a partir dos indicadores já consolidados.
- **`src/features/calendario.py`** — projeta a dimensão de calendário a partir da fonte externa bruta (`raw_Dim_Calendario.xlsx`), recortando apenas o intervalo de anos necessário.
- **`src/features/dimensoes.py`** — monta as tabelas de dimensão ID → descrição (`dim_faixa_renda`, `dim_tempo_relacionamento`, `dim_nivel_diversificacao`, `dim_nivel_movimentacao`, `dim_classificacao`) e a dimensão `dim_agencia`.
- **`src/features/consolidado.py`** — consolida Associados, Produtos e Movimentação pela `CHAVE` (`build_features`) e monta a projeção reduzida para o dashboard (`build_dashboard_features`).
- **`src/utils/logging.py`** — configuração central de logging (`get_logger`), usada por `src/pipeline.py` para registrar início/fim de cada etapa com contagem de linhas e tempo de execução.

## Status do Projeto (atualizado em 2026-08-31)

Legenda: **Concluído** | **Parcial** (existe, mas incompleto/divergente) | **Pendente** (não iniciado)

### 01 — Planejamento e Preparação do Projeto
| Item | Status | Observação |
|---|---|---|
| 01.01 Revisar escopo e requisitos | **Parcial** | Objetivos, entregáveis e requisitos técnicos (Python, dados tratados, Git, Power BI, README) foram levantados e estão refletidos em `docs/dicionario_dados.md`, `docs/qualidade_dados.md`, `docs/regras_negocio.md` e `docs/insights.md`, mas não há um documento dedicado de escopo (commit `docs(plan): define project scope` não foi feito como tal). |
| 01.02 Definir arquitetura | **Pendente** | O fluxo Bronze → IO → Validation → Cleaning → Silver → Features → Classification → Validation → Gold → Power BI → Insights ainda não foi documentado formalmente em arquivo próprio. |
| 01.03 Criar backlog técnico | **Pendente** | O backlog por fases (este cronograma) ainda não foi versionado como documento no repositório. |
| 01.04 Definir estratégia de qualidade | **Concluído** | Critérios de chave, duplicidade, nulos, tipos e cardinalidade definidos em `docs/qualidade_dados.md`. |

### 02 — Configuração Inicial do Repositório
| Item | Status | Observação |
|---|---|---|
| 02.01 Inicializar Git | **Concluído** | Repositório Git inicializado (`Initial commit`, `chore(estrutura): inicializar estrutura do projeto`). |
| 02.02 Configurar .gitignore | **Parcial** | `.gitignore` ignora `.venv`, `__pycache__`, caches de teste, `.ipynb_checkpoints` e `.env`; ainda não há regras para artefatos locais do Power BI (workspace `powerbi/` ainda não existe). |
| 02.03 Configurar dependências | **Concluído** | `requirements.txt` com `pandas`, `openpyxl`, `pyarrow` e `pytest` — cobre leitura Excel, Parquet e testes. |
| 02.04 Criar baseline | **Concluído** | Estrutura inicial registrada nos commits iniciais antes da implementação funcional. |

### 03 — Estruturação da Arquitetura
| Item | Status | Observação |
|---|---|---|
| 03.01 Estruturar camadas de dados | **Parcial** | Camadas existem como `data/0_bronze`, `data/1_silver`, `data/2_gold` — nomenclatura numerada, diferente do padrão `bronze/silver/gold` do cronograma. `data/2_gold` já contém `features.parquet` (ver item 10.04). |
| 03.02 Estruturar módulos Python | **Parcial** | `src/config`, `src/io`, `src/cleaning` implementados e em uso; `src/features` iniciado (`produtos.py`, `associados.py` ainda vazio). `src/validation` **não existe como módulo dedicado** — validações hoje estão embutidas em `src/cleaning/common.py` e nos testes. Há também `src/utils` (`logging.py`, `get_logger`), não previsto no cronograma original, usado por `src/pipeline.py` para observabilidade da execução (ver 13.04). |
| 03.03 Estruturar testes e documentação | **Concluído** | `docs/` com conteúdo substancial; `tests/test_silver.py` e `tests/test_features.py` implementados e passando. |
| 03.04 Preparar Power BI | **Pendente** | `powerbi/Associados360.pbip` ainda não criado. |

### 04 — Camada Bronze
| Item | Status | Observação |
|---|---|---|
| 04.01 Preservar fonte original | **Parcial** | Arquivo bruto presente em `data/0_bronze/raw_associados.xlsx` (nome diferente do especificado no cronograma, `teste_bi_base_crua.xlsx`); nenhuma transformação foi aplicada a ele até o momento — imutabilidade respeitada na prática. |
| 04.02 Inventariar fonte | **Concluído** | Abas `Associados`, `Produtos` e `Movimentacao`, seus campos e tipos mapeados em `docs/dicionario_dados.md`; profiling completo em `docs/qualidade_dados.md`. |
| 04.03 Documentar imutabilidade | **Pendente** | A regra de que a camada Bronze não pode ser alterada pelo pipeline ainda não está documentada explicitamente em nenhum arquivo do projeto. |

### 05 — Implementação da Leitura de Dados
| Item | Status | Observação |
|---|---|---|
| 05.01 Criar leitor Excel | **Concluído** | `src/io/excel.py`: `read_sheet` e `load_sources`, funções genéricas e reutilizáveis. |
| 05.02 Implementar leitura de Associados | **Concluído** | Lida via `load_sources()` (`src/io/excel.py`), chamada por `run_ingestion()` (`src/pipeline.py`) — os `read_*` antes duplicados em `src/cleaning/*.py` foram removidos; leitura agora exclusiva de `src/io`. |
| 05.03 Implementar leitura de Produtos | **Concluído** | Mesma leitura genérica via `load_sources()`, chave `SHEET_PRODUTOS`. |
| 05.04 Implementar leitura de Movimentacao | **Concluído** | Mesma leitura genérica via `load_sources()`, chave `SHEET_MOVIMENTACAO`. |

### 06 — Configurações Centrais
| Item | Status | Observação |
|---|---|---|
| 06.01 Centralizar paths | **Concluído** | `src/config/settings.py`: `PROJECT_ROOT`, `DATA_DIR`, `DOCS_DIR`, `BRONZE_DIR`, `SILVER_DIR`, `GOLD_DIR`, `RAW_ASSOCIADOS_PATH`. |
| 06.02 Centralizar schema | **Concluído** | `SHEET_ASSOCIADOS/PRODUTOS/MOVIMENTACAO`, `KEY_COLUMN`, `EXPECTED_COLUMNS_*`, `PRODUCT_COLUMNS`. |
| 06.03 Centralizar parâmetros | **Concluído** | `DIAS_POR_ANO`, `FAIXAS_RENDA`, `TERCIS_MOVIMENTACAO`, `CLASSIFICACAO_*`, `OPORTUNIDADE_*` e `FAIXAS_DIVERSIFICACAO` (indicadores de produtos). |

### 07 — Desenvolvimento das Rotinas de Limpeza
| Item | Status | Observação |
|---|---|---|
| 07.01 Criar funções comuns | **Concluído** | `src/cleaning/common.py`: `standardize_text`, `normalize_categories`, `validate_domain`, `null_report`, `flag_nulls`, `cast_types`, `convert_sn_to_bool`, entre outras. |
| 07.02 Limpar Associados | **Concluído** | `src/cleaning/associados.py`: padronização de `CIDADE`, sinalização de `DATA_ASSOCIACAO` futura (`DATA_ASSOCIACAO_INVALIDA`) sem alterar o dado de origem, tratamento de `RENDA_MENSAL`. |
| 07.03 Limpar Produtos | **Concluído** | `src/cleaning/produtos.py`: validação de domínio S/N, conversão para bool, validação de `CHAVE`, cálculo de `QTD_PRODUTOS`. |
| 07.04 Limpar Movimentacao | **Concluído** | `src/cleaning/movimentacao.py`: conversão de métricas numéricas e sinalização de inválidos por coluna (`*_INVALIDO`). |
| 07.05 Tratar duplicidades | **Concluído** | `handle_duplicate_keys` em `common.py`, aplicado em `clean_associados`/`clean_produtos`; diferencia duplicata real (levanta erro) de duplicidade de linha completa (remove). |
| 07.06 Tratar nulos | **Concluído** | `assert_allowed_nulls`, `flag_nulls` em `common.py`, aplicados por entidade. |
| 07.07 Padronizar textos e categorias | **Concluído** | `standardize_text`, `normalize_categories` aplicados em `CIDADE` (`src/cleaning/associados.py`). |
| 07.08 Padronizar tipos | **Concluído** | Tipos canônicos aplicados via `astype`/`cast_types` (`CHAVE` int64, `AGENCIA` int64, `RENDA_MENSAL` float64, datas em datetime), validados em `tests/test_silver.py`. |

### 08 — Validações de Qualidade
| Item | Status | Observação |
|---|---|---|
| 08.01 Validar Bronze | **Pendente** | `EXPECTED_COLUMNS_*` estão centralizadas em `settings.py`, mas não há validação explícita de schema executada sobre a leitura da fonte Bronze (não existe `quality.py`/`src/validation`). |
| 08.02 Validar CHAVE | **Parcial** | Unicidade e cardinalidade de `CHAVE` são garantidas em `handle_duplicate_keys` (cleaning) e confirmadas em `tests/test_silver.py`, mas não em um módulo de validação dedicado. |
| 08.03 Validar nulos, categorias e tipos | **Parcial** | Cobertas por `validate_domain`/`assert_allowed_nulls` (cleaning) e por `tests/test_silver.py`, sem módulo `quality.py`/`validation` próprio. |
| 08.04 Validar camadas | **Parcial** | Integridade referencial entre Associados/Produtos/Movimentacao validada em `tests/test_silver.py` (`test_chaves_identicas_entre_entidades`). A consolidação Silver → Gold (`data/2_gold/features.parquet`) é validada em `tests/test_features.py` (chave única e completa, colunas esperadas presentes), mas sem módulo de validação dedicado. |

### 09 — Construção da Silver
| Item | Status | Observação |
|---|---|---|
| 09.01 Gerar Associados | **Concluído** | `data/1_silver/associados.parquet`, gerado por `run_silver()` (`src/pipeline.py`), que aplica `clean_associados`. |
| 09.02 Gerar Produtos | **Concluído** | `data/1_silver/produtos.parquet`, gerado por `run_silver()`, que aplica `clean_produtos`. |
| 09.03 Gerar Movimentacao | **Concluído** | `data/1_silver/movimentacao.parquet`, gerado por `run_silver()`, que aplica `clean_movimentacao`. |
| 09.04 Validar Silver | **Concluído** | `tests/test_silver.py`: unicidade de chave, domínios, tipos, nulos residuais e integridade referencial entre as três entidades (1 a 1000 registros cada). |

### 10 — Features Analíticas
| Item | Status | Observação |
|---|---|---|
| 10.01 Indicadores de produtos | **Concluído** | `src/features/produtos.py` (`add_indicadores_produtos`): `INDICE_DIVERSIFICACAO` (proporção de produtos possuídos sobre o total possível) e `NIVEL_DIVERSIFICACAO_ID` (int 0–2, FK para `dim_nivel_diversificacao`, ver 12.03 — faixas em `FAIXAS_DIVERSIFICACAO`, `src/config/settings.py`), calculados sobre `QTD_PRODUTOS` já existente na Silver. Testado em `tests/test_features.py`. |
| 10.02 Tempo de relacionamento | **Concluído** | `src/features/associados.py` (`add_indicadores_relacionamento`): `TEMPO_RELACIONAMENTO_DIAS` e `TEMPO_RELACIONAMENTO_ANOS` (`dias / DIAS_POR_ANO`) a partir de `DATA_REFERENCIA − DATA_ASSOCIACAO`. Ver decisão sobre datas futuras abaixo. Testado em `tests/test_features.py`. |
| 10.03 Faixas de renda | **Concluído** | `src/features/associados.py` (`add_faixa_renda`): categoriza `RENDA_MENSAL` em `FAIXA_RENDA_ID` (int 0–3, ou -1 para "Não informado"; FK para `dim_faixa_renda`, ver 12.03), faixas definidas em `FAIXAS_RENDA` (`src/config/settings.py`). Os 12 registros com `RENDA_MENSAL` nula recebem o ID -1, conforme `docs/regras_negocio.md` (seção 3), em vez de serem excluídos ou imputados. `add_faixa_tempo_relacionamento` (mesmo módulo) categoriza `TEMPO_RELACIONAMENTO_ANOS` em `TEMPO_RELACIONAMENTO_FAIXA_ID` (int 0–3, faixas trienais, ou -1 para "Não disponível"; FK para `dim_tempo_relacionamento`, ver 12.03), faixas em `FAIXAS_TEMPO_RELACIONAMENTO` (`src/config/settings.py`). Testado em `tests/test_features.py`. |
| 10.04 Consolidar features | **Concluído** | `src/features/consolidado.py` (`build_features`): aplica os indicadores de produtos e relacionamento sobre as respectivas entidades e faz `merge` por `CHAVE` das três bases Silver (`associados` ⋈ `produtos` ⋈ `movimentacao`), com `validate="one_to_one"` em cada junção para impor a cardinalidade 1:1:1 definida em `docs/dicionario_dados.md` — qualquer duplicidade futura em uma das entidades interrompe o pipeline em vez de inflar a base silenciosamente. Orquestrado em `src/pipeline.py` (`run_gold`), persistido em `data/2_gold/features.parquet`. Testado em `tests/test_features.py`. |

#### Tratamento de datas futuras em TEMPO_RELACIONAMENTO

37 registros da base têm `DATA_ASSOCIACAO` futura em relação à data de execução do pipeline (ver `docs/qualidade_dados.md`) — um problema de qualidade da fonte, não um valor de negócio válido. Alternativas avaliadas para o cálculo de `TEMPO_RELACIONAMENTO_DIAS`/`TEMPO_RELACIONAMENTO_ANOS`:

| Abordagem | Por que foi descartada |
|---|---|
| Zerar/clipar em 0 | Insere um valor factualmente falso (associado não entrou "hoje"); distorce médias e classificações por tempo para baixo. |
| Excluir o associado da base de features | Quebra a integridade 1:1:1 entre Associados/Produtos/Movimentacao (`test_chaves_identicas_entre_entidades`) e o remove de indicadores que não dependem de tempo. |
| Imputar com média/mediana | Cria dado sintético para mascarar um problema de qualidade, em vez de sinalizá-lo — contraria a estratégia definida no item 01.04. |
| **Nulo (NaN), preservando o registro** *(adotada)* | Não fabrica valor, mantém o associado íntegro na base e o problema visível/auditável. |

Solução adotada: a camada Silver (`src/cleaning/associados.py`) sinaliza a inconsistência em `DATA_ASSOCIACAO_INVALIDA`, sem alterar `DATA_ASSOCIACAO` na origem. A camada Features usa essa flag para mascarar `TEMPO_RELACIONAMENTO_DIAS`/`TEMPO_RELACIONAMENTO_ANOS` como nulos apenas nesses 37 registros, mantendo a decisão já formalizada em `docs/regras_negocio.md` (seção 2) — o registro segue disponível para as demais análises, mas nulo para tempo de relacionamento; a Classificação (`src/features/classificacao.py`) trata esses casos com a flag `CLASSIFICACAO_TEMPO_INDISPONIVEL`.

### 11 — Classificação dos Associados
| Item | Status | Observação |
|---|---|---|
| 11.01 Definir metodologia | **Concluído** | `src/features/classificacao.py` (`add_classificacao`): índice composto por percentil (`INDICE_CLASSIFICACAO`), combinando cinco pilares — Produtos (`SCORE_PRODUTOS`), Relacionamento (`SCORE_RELACIONAMENTO`), Saldo (`SCORE_SALDO`), Pix Mensal (`SCORE_PIX_MENSAL`) e Compras no Cartão (`SCORE_COMPRAS_CARTAO`) —, cortado em quartis para gerar `CLASSIFICACAO_ID` (int 0–3, FK para `dim_classificacao`, ver 12.03), domínio em `DIM_CLASSIFICACAO` (`src/config/settings.py`). A dimensão "Utilização" pedida no desafio foi desdobrada em Pix Mensal e Compras no Cartão em vez de um único score médio, por serem bases de naturezas diferentes — quantidade de transações contra volume financeiro no cartão. Substitui as regras sequenciais de exemplo do desafio, que produziam 83,1% dos associados em uma única categoria de fallback; a nova metodologia produz quatro grupos de tamanho comparável (250/250/250/250) com progressão monotônica nos indicadores brutos. Comparação com árvore de decisão e clustering (K-Means), e justificativa completa, em `docs/regras_negocio.md` (seção 5). Testado em `tests/test_features.py`. |

### 12 — Construção da Gold
| Item | Status | Observação |
|---|---|---|
| 12.01 Consolidar entidades pela CHAVE | **Concluído** | `src/features/consolidado.py` (`build_features`): junção de Associados, Produtos e Movimentacao por `CHAVE` com `validate="one_to_one"`, respeitando a cardinalidade 1:1:1 documentada em `docs/dicionario_dados.md` (ver 10.04). |
| 12.02 Adicionar features e classificação | **Concluído** | Além de `CLASSIFICACAO_ID` (11.01), a Gold recebe `NIVEL_MOVIMENTACAO_ID` (`src/features/movimentacao.py`, `add_nivel_movimentacao`): `SALDO_MEDIO`, `PIX_MENSAL` e `COMPRAS_CARTAO` classificados por tercis próprios (`TERCIS_MOVIMENTACAO`) em Baixa/Média/Alta (IDs 0–2), combinados pela moda entre os três, com desempate por `SALDO_MEDIO` em caso de empate triplo — conforme `docs/regras_negocio.md` (seção 4). E as três `FLAG_OPORTUNIDADE_*` (`src/features/oportunidades.py`, `add_flags_oportunidade`): alta renda com poucos produtos, baixa utilização e potencial de crescimento, parametrizadas em `OPORTUNIDADE_*` (`src/config/settings.py`, comparando IDs) — ver `docs/regras_negocio.md` (seção 6). Testado em `tests/test_features.py`. |
| 12.03 Modelagem em estrela (dimensões) | **Concluído** | Toda faixa/classe/classificação criada na Gold (`FAIXA_RENDA_ID`, `TEMPO_RELACIONAMENTO_FAIXA_ID`, `NIVEL_DIVERSIFICACAO_ID`, `NIVEL_*_MOVIMENTACAO_ID`, `CLASSIFICACAO_ID`) é gravada como ID inteiro, não como texto — o rótulo vive em tabelas de dimensão separadas (`data/2_gold/dim_faixa_renda.parquet`, `dim_tempo_relacionamento.parquet`, `dim_nivel_diversificacao.parquet`, `dim_nivel_movimentacao.parquet`, `dim_classificacao.parquet`), construídas por `build_dimensions()` (`src/features/dimensoes.py`) e persistidas em `run_gold()` (`src/pipeline.py`). Pares ID/descrição centralizados em `DIM_*` (`src/config/settings.py`). Reduz o tamanho da fato (int em vez de string repetida por linha) e permite relacionar fato + dimensões pelo ID no Power BI. Duas dimensões adicionais não seguem esse padrão de ID sintético — `dim_calendario.parquet` (data ↔ `DATA_ASSOCIACAO`) e `dim_agencia.parquet` (código `AGENCIA` ↔ nome de agência) — ver `docs/dicionario_dados.md` (seções 6.6–6.7). Testado em `tests/test_features.py` (schema, unicidade de ID e integridade referencial fato → dimensão). |

#### Metodologia de identificação de oportunidades (Página 4 do Power BI)

A Gold calcula as três `FLAG_OPORTUNIDADE_*` (12.02) como critérios discretos e fixos (ex.: renda > R$ 15.000 **E** produtos ≤ 2). No dashboard, a Página 4 usa uma abordagem complementar e mais exploratória, construída sobre o mesmo `INDICE_CLASSIFICACAO` (11.01):

- **Matriz Faixa de Renda × Classificação**, com o valor médio de `INDICE_CLASSIFICACAO` em cada célula — como o índice é percentual (0–1, maior é melhor), célula com **renda alta e score baixo** identifica visualmente o quadrante de maior oportunidade, sem precisar fixar um limiar de corte a priori.
- A matriz funciona como **filtro interativo** (interação nativa do Power BI) para uma **tabela de associados**, ordenada de forma ascendente pelo mesmo índice — quanto menor o score, maior a oportunidade — trazendo os cinco pilares `SCORE_*` (`INDICE_CLASSIFICACAO`, 11.01) como diagnóstico de composição do score de cada associado.
- Sobre a base atual, a célula "Acima de R$ 15.000" × "Inicial" concentra 133 associados (13,3% da base) com o menor score médio (0,33) dentro da faixa de renda mais alta — o mesmo público de maior potencial de receita incremental identificado pela flag `FLAG_OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS`, agora navegável de forma interativa em vez de uma lista estática.

As três colunas de flag continuam na Gold e disponíveis no modelo (medidas de contagem em `_Medidas` no Power BI) para quem preferir os critérios fixos. Achado completo, com números e ação sugerida, em `docs/insights.md` (seção "Página 4 — Oportunidades"); metodologia da matriz em `docs/regras_negocio.md` (seção 7).

### 13 — Pipeline Principal
| Item | Status | Observação |
|---|---|---|
| 13.01 Orquestrar ingestão | **Concluído** | `src/pipeline.py` (`run_ingestion`): lê as três planilhas Bronze via `load_sources()` (`src/io/excel.py`), sem transformação — apenas orquestra o módulo de leitura. Os `read_*` até então duplicados em `src/cleaning/*.py` foram removidos (ver 05.02–05.04). |
| 13.02 Orquestrar Silver | **Concluído** | `src/pipeline.py` (`run_silver`): chama `clean_associados`/`clean_produtos`/`clean_movimentacao` (`src/cleaning/*.py`), cada um já validando o domínio/tipos antes e depois da limpeza (`assert_exact_categories`, `assert_allowed_nulls`, `handle_duplicate_keys` em `src/cleaning/common.py`) e levantando `ValueError` em caso de violação, e persiste os três parquets em `data/1_silver/`. `pipeline.py` não contém regra de limpeza própria, apenas orquestra. |
| 13.03 Orquestrar Gold | **Concluído** | `src/pipeline.py` (`run_gold`): chama `build_features()` (`src/features/consolidado.py`), que consolida as entidades pela `CHAVE` (validando a cardinalidade 1:1:1), adiciona os indicadores analíticos e a classificação (12.01–12.02), e persiste `data/2_gold/features.parquet` (tabela fato); chama também `build_dimensions()` (`src/features/dimensoes.py`) e persiste as quatro tabelas `dim_*.parquet` (12.03). `run_pipeline()` encadeia as três etapas (ingestão → Silver → Gold) e é o único ponto de entrada do `python -m src.pipeline`. |
| 13.04 Logging e execução | **Concluído** | `src/utils/logging.py` (`get_logger`): logger configurado com timestamp, nível e nome do módulo, usado em cada etapa de `src/pipeline.py` (início/fim de ingestão, Silver e Gold, com contagem de linhas e tempo total). `run_pipeline()` captura `DATA_REFERENCIA` (`pd.Timestamp.now()`) uma única vez no início da execução e a propaga para `run_silver`/`run_gold` — em vez de cada etapa consultar "agora" de forma independente —, garantindo que a sinalização de datas futuras (`DATA_ASSOCIACAO_INVALIDA`) e o cálculo de `TEMPO_RELACIONAMENTO_*` usem a mesma referência dentro de uma mesma rodada; `reference_date` pode ser passada explicitamente para reexecução reprodutível (depuração/auditoria). |

## Como executar

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.pipeline
```

Rode sempre a partir da **raiz do projeto** (a pasta que contém `src/`), usando `python -m src.pipeline` — nunca `python src/pipeline.py` nem `cd src && python pipeline.py`. `pipeline.py` usa imports absolutos (`from src.cleaning...`); a flag `-m` executa o arquivo como módulo do pacote `src`, colocando a raiz do projeto no `sys.path`. Rodando de outra forma, o Python não encontra `src` e falha com `ModuleNotFoundError: No module named 'src'`.

O comando acima gera/atualiza, em ordem:
- `data/1_silver/associados.parquet`, `produtos.parquet`, `movimentacao.parquet` (camada Silver)
- `data/2_gold/features.parquet` (tabela fato completa — features/classificação consolidadas, faixas/classes como ID)
- `data/2_gold/features_dashboard.parquet` (tabela fato reduzida, só as colunas usadas pelas 4 páginas do Power BI — ver `docs/dicionario_dados.md` seção 5.6)
- `data/2_gold/dim_faixa_renda.parquet`, `dim_tempo_relacionamento.parquet`, `dim_nivel_diversificacao.parquet`, `dim_nivel_movimentacao.parquet`, `dim_classificacao.parquet` (tabelas de dimensão — de-para ID → descrição, ver `docs/dicionario_dados.md` seção 6)
- `data/2_gold/dim_calendario.parquet` (dimensão de data, projetada a partir de `data/0_bronze/raw_Dim_Calendario.xlsx` — ver `docs/dicionario_dados.md` seção 6.6)
- `data/2_gold/dim_agencia.parquet` (código AGENCIA → nome de agência, levantamento de negócio — ver `docs/dicionario_dados.md` seção 6.7)

Para rodar os testes: `pytest tests/ -q` (também a partir da raiz do projeto).


