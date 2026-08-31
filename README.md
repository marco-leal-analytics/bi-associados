# bi-associados
Associados 360 | Business Intelligence &amp; Relationship Analytics — Solução completa de BI desenvolvida com Python, Excel, Parquet e Power BI para tratamento e qualidade de dados, análise de relacionamento, classificação de associados, identificação de oportunidades e geração de insights, com arquitetura Bronze → Silver → Gold e versionamento Git.

## Status do Projeto (atualizado em 2026-08-30)

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
| 10.03 Faixas de renda | **Concluído** | `src/features/associados.py` (`add_faixa_renda`): categoriza `RENDA_MENSAL` em `FAIXA_RENDA_ID` (int 0–3, ou -1 para "Não informado"; FK para `dim_faixa_renda`, ver 12.03), faixas definidas em `FAIXAS_RENDA` (`src/config/settings.py`). Os 12 registros com `RENDA_MENSAL` nula recebem o ID -1, conforme `docs/regras_negocio.md` (seção 3), em vez de serem excluídos ou imputados. Testado em `tests/test_features.py`. |
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
| 12.03 Modelagem em estrela (dimensões) | **Concluído** | Toda faixa/classe/classificação criada na Gold (`FAIXA_RENDA_ID`, `NIVEL_DIVERSIFICACAO_ID`, `NIVEL_*_MOVIMENTACAO_ID`, `CLASSIFICACAO_ID`) é gravada como ID inteiro, não como texto — o rótulo vive em tabelas de dimensão separadas (`data/2_gold/dim_faixa_renda.parquet`, `dim_nivel_diversificacao.parquet`, `dim_nivel_movimentacao.parquet`, `dim_classificacao.parquet`), construídas por `build_dimensions()` (`src/features/dimensoes.py`) e persistidas em `run_gold()` (`src/pipeline.py`). Pares ID/descrição centralizados em `DIM_*` (`src/config/settings.py`). Reduz o tamanho da fato (int em vez de string repetida por linha) e permite relacionar fato + dimensões pelo ID no Power BI. Testado em `tests/test_features.py` (schema, unicidade de ID e integridade referencial fato → dimensão). |

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
- `data/2_gold/dim_faixa_renda.parquet`, `dim_nivel_diversificacao.parquet`, `dim_nivel_movimentacao.parquet`, `dim_classificacao.parquet` (tabelas de dimensão — de-para ID → descrição, ver `docs/dicionario_dados.md` seção 6)

Para rodar os testes: `pytest tests/ -q` (também a partir da raiz do projeto).


