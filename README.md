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
| 03.01 Estruturar camadas de dados | **Parcial** | Camadas existem como `data/0_bronze`, `data/1_silver`, `data/2_gold` — nomenclatura numerada, diferente do padrão `bronze/silver/gold` do cronograma. `data/2_gold` ainda não tem arquivos gerados. |
| 03.02 Estruturar módulos Python | **Parcial** | `src/config`, `src/io`, `src/cleaning` implementados e em uso; `src/features` iniciado (`produtos.py`, `associados.py` ainda vazio). `src/validation` **não existe como módulo dedicado** — validações hoje estão embutidas em `src/cleaning/common.py` e nos testes. Há também `src/utils` (logging), não previsto no cronograma. |
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
| 05.02 Implementar leitura de Associados | **Parcial** | `read_associados()` existe e usa `read_sheet`, mas está definida em `src/cleaning/associados.py` e não em `src/io` — diverge da separação "io = leitura exclusiva" prevista no cronograma. |
| 05.03 Implementar leitura de Produtos | **Parcial** | Mesma situação: `read_produtos()` está em `src/cleaning/produtos.py`. |
| 05.04 Implementar leitura de Movimentacao | **Parcial** | Mesma situação: `read_movimentacao()` está em `src/cleaning/movimentacao.py`. |

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
| 08.04 Validar camadas | **Parcial** | Integridade referencial entre Associados/Produtos/Movimentacao validada em `tests/test_silver.py` (`test_chaves_identicas_entre_entidades`); validação Silver ↔ Gold ainda não se aplica, pois a Gold não foi gerada. |

### 09 — Construção da Silver
| Item | Status | Observação |
|---|---|---|
| 09.01 Gerar Associados | **Concluído** | `data/1_silver/associados.parquet`, gerado por `build_silver_associados` (`src/pipeline.py`). |
| 09.02 Gerar Produtos | **Concluído** | `data/1_silver/produtos.parquet`, gerado por `build_silver_produtos`. |
| 09.03 Gerar Movimentacao | **Concluído** | `data/1_silver/movimentacao.parquet`, gerado por `build_silver_movimentacao`. |
| 09.04 Validar Silver | **Concluído** | `tests/test_silver.py`: unicidade de chave, domínios, tipos, nulos residuais e integridade referencial entre as três entidades (1 a 1000 registros cada). |

### 10 — Features Analíticas
| Item | Status | Observação |
|---|---|---|
| 10.01 Indicadores de produtos | **Concluído** | `src/features/produtos.py` (`add_indicadores_produtos`): `INDICE_DIVERSIFICACAO` (proporção de produtos possuídos sobre o total possível) e `NIVEL_DIVERSIFICACAO` (categórico ordenado Baixa/Média/Alta, faixas em `FAIXAS_DIVERSIFICACAO`, `src/config/settings.py`), calculados sobre `QTD_PRODUTOS` já existente na Silver. Testado em `tests/test_features.py`. |
| 10.02 Tempo de relacionamento | **Concluído** | `src/features/associados.py` (`add_indicadores_relacionamento`): `TEMPO_RELACIONAMENTO_DIAS` e `TEMPO_RELACIONAMENTO_ANOS` (`dias / DIAS_POR_ANO`) a partir de `DATA_REFERENCIA − DATA_ASSOCIACAO`. Ver decisão sobre datas futuras abaixo. Testado em `tests/test_features.py`. Demais indicadores da fase (movimentação, classificação, oportunidades) ainda pendentes. |

#### Tratamento de datas futuras em TEMPO_RELACIONAMENTO

37 registros da base têm `DATA_ASSOCIACAO` futura em relação à data de execução do pipeline (ver `docs/qualidade_dados.md`) — um problema de qualidade da fonte, não um valor de negócio válido. Alternativas avaliadas para o cálculo de `TEMPO_RELACIONAMENTO_DIAS`/`TEMPO_RELACIONAMENTO_ANOS`:

| Abordagem | Por que foi descartada |
|---|---|
| Zerar/clipar em 0 | Insere um valor factualmente falso (associado não entrou "hoje"); distorce médias e classificações por tempo para baixo. |
| Excluir o associado da base de features | Quebra a integridade 1:1:1 entre Associados/Produtos/Movimentacao (`test_chaves_identicas_entre_entidades`) e o remove de indicadores que não dependem de tempo. |
| Imputar com média/mediana | Cria dado sintético para mascarar um problema de qualidade, em vez de sinalizá-lo — contraria a estratégia definida no item 01.04. |
| **Nulo (NaN), preservando o registro** *(adotada)* | Não fabrica valor, mantém o associado íntegro na base e o problema visível/auditável. |

Solução adotada: a camada Silver (`src/cleaning/associados.py`) sinaliza a inconsistência em `DATA_ASSOCIACAO_INVALIDA`, sem alterar `DATA_ASSOCIACAO` na origem. A camada Features usa essa flag para mascarar `TEMPO_RELACIONAMENTO_DIAS`/`TEMPO_RELACIONAMENTO_ANOS` como nulos apenas nesses 37 registros, mantendo a decisão já formalizada em `docs/regras_negocio.md` (seção 2) — o registro segue disponível para as demais análises, mas nulo para tempo de relacionamento, e cabe à Classificação (fase futura) tratá-lo com a flag `CLASSIFICACAO_TEMPO_INDISPONIVEL`.


