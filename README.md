# bi-associados
Associados 360 | Business Intelligence &amp; Relationship Analytics — Solução completa de BI desenvolvida com Python, Excel, Parquet e Power BI para tratamento e qualidade de dados, análise de relacionamento, classificação de associados, identificação de oportunidades e geração de insights, com arquitetura Bronze → Silver → Gold e versionamento Git.

## Status do Projeto (atualizado em 2026-08-30)

Legenda: **Concluído** | **Parcial** (existe, mas incompleto/divergente) | **Pendente** (não iniciado)

### Fase 01 — Planejamento e Preparação do Projeto
| Item | Status | Observação |
|---|---|---|
| 01.01 Revisar escopo e requisitos | **Concluído** | Requisitos extraídos de `docs/orientações.docx` e cruzados com profiling real da base; documentados em `docs/dicionario_dados.md`, `docs/qualidade_dados.md`, `docs/regras_negocio.md` e `docs/insights.md`. |
| 01.02 Definir arquitetura | **Pendente** | O fluxo Bronze → IO → Validation → Cleaning → Silver → Features → Classification → Validation → Gold → Power BI → Insights ainda não foi documentado formalmente em um arquivo próprio. |
| 01.03 Criar backlog técnico | **Pendente** | O backlog por fases existe apenas como referência de trabalho; ainda não foi versionado como documento no repositório. |
| 01.04 Definir estratégia de qualidade | **Concluído** | Critérios de chave, duplicidade, nulos, tipos e cardinalidade definidos em `docs/qualidade_dados.md`. |

### Fase 03 — Estruturação da Arquitetura
| Item | Status | Observação |
|---|---|---|
| 03.01 Estruturar camadas de dados | **Parcial** | Camadas existem como `data/0_bronze`, `data/1_silver`, `data/2_gold` — nomenclatura numerada, diferente do padrão `bronze/silver/gold` previsto no backlog. |
| 03.02 Estruturar módulos Python | **Parcial** | `src/config`, `src/cleaning` e `src/features` existem, mas apenas como esqueleto (sem lógica implementada). `src/io` e `src/validation` — previstos no backlog e **importados por `src/pipeline.py`** — ainda não existem, o que quebra a execução do pipeline. Há também um módulo `src/utils` (logging) não previsto originalmente. |
| 03.03 Estruturar testes e documentação | **Parcial** | `docs/` criada e com conteúdo substancial. `tests/` ainda não existe. |
| 03.04 Preparar Power BI | **Pendente** | `powerbi/Associados360.pbip` ainda não criado. |

### Fase 04 — Camada Bronze
| Item | Status | Observação |
|---|---|---|
| 04.01 Preservar fonte original | **Parcial** | Arquivo bruto presente em `data/0_bronze/raw_associados.xlsx` (nome diferente do especificado no backlog, `teste_bi_base_crua.xlsx`); nenhuma transformação foi aplicada a ele até o momento. |
| 04.02 Inventariar fonte | **Concluído** | Abas `Associados`, `Produtos` e `Movimentacao`, seus campos e tipos mapeados em `docs/dicionario_dados.md`; profiling completo em `docs/qualidade_dados.md`. |
| 04.03 Documentar imutabilidade | **Pendente** | A regra de que a camada Bronze não pode ser alterada pelo pipeline ainda não está documentada explicitamente em nenhum arquivo do projeto. |

### Pendências técnicas identificadas
- `src/pipeline.py` importa módulos inexistentes (`src.io.excel`, `src.validation.quality`) — o pipeline não executa no estado atual do código.
- `src/cleaning/*.py` e `src/features/associados.py` estão vazios/esqueleto, sem lógica de limpeza ou de cálculo de indicadores implementada.
- Ambiente virtual `.venv/` criado localmente e ignorado via `.gitignore`; dependências de `requirements.txt` (pandas, openpyxl, pyarrow, pytest) instaladas.
- `tests/` e `powerbi/` ainda não existem no repositório.
