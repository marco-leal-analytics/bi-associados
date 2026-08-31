"""Configurações centrais do pipeline: paths, schema das fontes e parâmetros
analíticos/de classificação. Fonte única de verdade — demais módulos importam
daqui em vez de repetir literais, para que um limiar ou rótulo só precise
mudar em um lugar (ver `docs/regras_negocio.md` para a justificativa de cada
parâmetro).
"""

from pathlib import Path

# --- Paths ---
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"

BRONZE_DIR = DATA_DIR / "0_bronze"
SILVER_DIR = DATA_DIR / "1_silver"
GOLD_DIR = DATA_DIR / "2_gold"

RAW_ASSOCIADOS_PATH = BRONZE_DIR / "raw_associados.xlsx"

# --- Schema das fontes ---
SHEET_ASSOCIADOS = "Associados"
SHEET_PRODUTOS = "Produtos"
SHEET_MOVIMENTACAO = "Movimentacao"

KEY_COLUMN = "CHAVE"

EXPECTED_COLUMNS_ASSOCIADOS = (
    "CHAVE",
    "NOME",
    "AGENCIA",
    "CIDADE",
    "DATA_ASSOCIACAO",
    "RENDA_MENSAL",
)
EXPECTED_COLUMNS_PRODUTOS = (
    "CHAVE",
    "CONTA_CORRENTE",
    "CARTAO",
    "CREDITO",
    "INVESTIMENTO",
    "CONSORCIO",
    "SEGURO",
)
EXPECTED_COLUMNS_MOVIMENTACAO = (
    "CHAVE",
    "SALDO_MEDIO",
    "PIX_MENSAL",
    "COMPRAS_CARTAO",
)

# Colunas binárias (S/N na origem) usadas para calcular QTD_PRODUTOS.
PRODUCT_COLUMNS = EXPECTED_COLUMNS_PRODUTOS[1:]

# --- Parâmetros estáveis (regras analíticas e de classificação) ---
DIAS_POR_ANO = 365.25  # usado para converter TEMPO_RELACIONAMENTO_DIAS em anos

# --- Dimensões (ID -> descrição) ---
# Toda faixa/classe/classificação criada na Gold é gravada como um ID inteiro
# (chave estrangeira) na tabela fato, e seu significado (o rótulo textual)
# vive só na dimensão correspondente — reduz o tamanho da Gold (int em vez de
# string repetida por linha) e segue o padrão de modelagem em estrela do
# Power BI (fato + dimensões relacionadas pelo ID). As dimensões são
# construídas em `src/features/dimensoes.py` (`build_dimensions`) e
# persistidas em `data/2_gold/dim_*.parquet`.

FAIXA_RENDA_NAO_INFORMADO_ID = -1

DIM_FAIXA_RENDA = (
    (0, "Até R$ 3.000"),
    (1, "R$ 3.001 a R$ 8.000"),
    (2, "R$ 8.001 a R$ 15.000"),
    (3, "Acima de R$ 15.000"),
    (FAIXA_RENDA_NAO_INFORMADO_ID, "Não informado"),
)

# Faixas de RENDA_MENSAL: (ID, limite inferior exclusivo, limite superior
# inclusivo). Ver src/features/associados.py (add_faixa_renda) e
# regras_negocio.md (seção 3).
FAIXAS_RENDA = (
    (0, 0, 3_000),
    (1, 3_000, 8_000),
    (2, 8_000, 15_000),
    (3, 15_000, None),
)

DIM_NIVEL_DIVERSIFICACAO = (
    (0, "Baixa"),
    (1, "Média"),
    (2, "Alta"),
)

# Faixas de QTD_PRODUTOS: (ID, mínimo inclusive, máximo inclusive).
# Ver src/features/produtos.py (add_indicadores_produtos).
FAIXAS_DIVERSIFICACAO = (
    (0, 0, 1),
    (1, 2, 4),
    (2, 5, len(PRODUCT_COLUMNS)),
)

# Dimensão compartilhada pelos quatro indicadores de nível de movimentação
# (NIVEL_SALDO_MEDIO_ID, NIVEL_PIX_MENSAL_ID, NIVEL_COMPRAS_CARTAO_ID e o
# NIVEL_MOVIMENTACAO_ID final) — mesmo domínio Baixa/Média/Alta para os quatro.
DIM_NIVEL_MOVIMENTACAO = (
    (0, "Baixa"),
    (1, "Média"),
    (2, "Alta"),
)

# Tercis (P33, P66) de cada indicador de movimentação, calculados sobre a
# base Bronze e validados sobre a Silver (ver docs/qualidade_dados.md) —
# usados para classificar cada indicador em Baixa/Média/Alta (IDs de
# DIM_NIVEL_MOVIMENTACAO) antes de combinar pela moda em
# src/features/movimentacao.py (add_nivel_movimentacao).
TERCIS_MOVIMENTACAO = {
    "SALDO_MEDIO": (78_900, 163_530),
    "PIX_MENSAL": (32, 66),
    "COMPRAS_CARTAO": (6_745, 13_131),
}

# IDs de CLASSIFICACAO, em ordem crescente de INDICE_CLASSIFICACAO (quartis).
# Ver src/features/classificacao.py (add_classificacao).
DIM_CLASSIFICACAO = (
    (0, "Inicial"),
    (1, "Em Desenvolvimento"),
    (2, "Maduro"),
    (3, "Engajado"),
)
CLASSIFICACAO_IDS = tuple(id_ for id_, _ in DIM_CLASSIFICACAO)

# Pesos de cada pilar na soma ponderada que forma INDICE_CLASSIFICACAO.
# Devem somar 1.0; 20% cada por padrão (nenhuma dimensão priorizada no
# desafio) — ver docs/regras_negocio.md (seção 5.2). PIX_MENSAL (quantidade
# de transações) e COMPRAS_CARTAO (volume financeiro no cartão) são bases
# distintas e por isso viraram pilares próprios em vez de um único
# "utilização" médio entre as duas.
CLASSIFICACAO_PESOS = {
    "produtos": 0.20,
    "relacionamento": 0.20,
    "saldo": 0.20,
    "pix_mensal": 0.20,
    "compras_cartao": 0.20,
}

# Critérios das três flags de oportunidade (src/features/oportunidades.py,
# add_flags_oportunidade), expressos em IDs das dimensões acima. Ver
# docs/regras_negocio.md (seção 6).
OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS = {
    "faixa_renda_id": FAIXAS_RENDA[-1][0],
    "qtd_produtos_max": 2,
}
OPORTUNIDADE_BAIXA_UTILIZACAO = {
    "nivel_movimentacao_id": DIM_NIVEL_MOVIMENTACAO[0][0],  # Baixa
    "qtd_produtos_min": 2,
}
OPORTUNIDADE_POTENCIAL_CRESCIMENTO = {
    "classificacao_id": DIM_CLASSIFICACAO[1][0],  # Em Desenvolvimento
    "nivel_movimentacao_ids": {DIM_NIVEL_MOVIMENTACAO[1][0], DIM_NIVEL_MOVIMENTACAO[2][0]},  # Média, Alta
}

# Colunas da Gold efetivamente usadas pelas 4 páginas do dashboard Power BI
# (ver docs/regras_negocio.md, seção 7, e docs/insights.md). A fato completa
# (`features.parquet`, ~40 colunas) carrega campos intermediários do cálculo
# (ex.: SCORE_*, NIVEL_SALDO_MEDIO_ID, colunas de produto individuais) que não
# alimentam nenhum visual — importar tudo no Power BI infla o modelo sem
# ganho. `build_dashboard_features` (src/features/consolidado.py) projeta só
# estas colunas para `features_dashboard.parquet`, a fonte recomendada para o
# import no Power BI.
DASHBOARD_COLUMNS = (
    "CHAVE",  # Página 1 (contagem de associados) e chave de linha
    "AGENCIA",  # Página 2 — Associados por Agência
    "CIDADE",  # Página 2 — Associados por Cidade
    "RENDA_MENSAL",  # Página 1 — Renda Média
    "FAIXA_RENDA_ID",  # Página 2 — Faixa de Renda (FK para dim_faixa_renda)
    "SALDO_MEDIO",  # Página 1 — Saldo Médio
    "QTD_PRODUTOS",  # Página 1 — Produtos por Associado
    "DATA_ASSOCIACAO",  # Página 2 — FK para dim_calendario (associados por ano/mês de entrada)
    "TEMPO_RELACIONAMENTO_ANOS",  # Página 2 — Tempo de Relacionamento
    "DATA_ASSOCIACAO_INVALIDA",  # Nota de rodapé: exclusões de tempo de relacionamento (docs/insights.md)
    "CLASSIFICACAO_ID",  # Página 3 — FK para dim_classificacao
    "CLASSIFICACAO_TEMPO_INDISPONIVEL",  # Transparência: score de relacionamento neutralizado
    "FLAG_OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS",  # Página 4
    "FLAG_OPORTUNIDADE_BAIXA_UTILIZACAO",  # Página 4
    "FLAG_OPORTUNIDADE_POTENCIAL_CRESCIMENTO",  # Página 4
)

# --- Dimensão Calendário (fonte externa, data/0_bronze/raw_Dim_Calendario.xlsx) ---
RAW_DIM_CALENDARIO_PATH = BRONZE_DIR / "raw_Dim_Calendario.xlsx"
SHEET_DIM_CALENDARIO = "Dim_Calendario"

# Colunas mantidas da Dim_Calendario bruta (45 colunas, ~28.850 linhas, anos
# 2000-2078) para a dimensão de data usada no projeto. A fonte traz
# granularidade de dia da semana, feriado, bimestre e quadrimestre — nenhuma
# das 4 páginas do dashboard (docs/regras_negocio.md, seção 7) analisa nesse
# nível; a única necessidade é relacionar DATA_ASSOCIACAO por ano/mês/
# trimestre/semestre (ex.: associados por ano de entrada, Página 2), então a
# dimensão fica reduzida ao necessário.
DIM_CALENDARIO_COLUNAS = (
    "DATA",
    "ANO",
    "MES",
    "NOME_MES",
    "NOME_MES_ABREVIADO",
    "ANO_MES",
    "TRIMESTRE",
    "NOME_TRIMESTRE",
    "SEMESTRE",
    "NOME_SEMESTRE",
)

# Anos de folga antes/depois do intervalo observado em DATA_ASSOCIACAO (e da
# DATA_REFERENCIA da rodada) ao filtrar a Dim_Calendario — evita relacionamento
# órfão na fato se a fonte for regenerada com datas fora do intervalo atual
# (2018-2026, ver docs/qualidade_dados.md), sem carregar as 79 safras
# completas do arquivo bruto.
CALENDARIO_ANOS_BUFFER = 1
