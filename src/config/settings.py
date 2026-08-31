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

# Faixas de RENDA_MENSAL: (rótulo, limite inferior exclusivo, limite superior
# inclusivo). O prefixo alfabético (A/B/C/D) ordena as faixas no Power BI.
# Ver src/features/associados.py (add_faixa_renda) e regras_negocio.md (seção 3).
FAIXAS_RENDA = (
    ("A - Até R$ 3.000", 0, 3_000),
    ("B - R$ 3.001 a R$ 8.000", 3_000, 8_000),
    ("C - R$ 8.001 a R$ 15.000", 8_000, 15_000),
    ("D - Acima de R$ 15.000", 15_000, None),
)

# Faixas de QTD_PRODUTOS: (rótulo, mínimo inclusive, máximo inclusive).
# Ver src/features/produtos.py (add_indicadores_produtos).
FAIXAS_DIVERSIFICACAO = (
    ("0 - Baixa", 0, 1),
    ("1 - Média", 2, 4),
    ("2 - Alta", 5, len(PRODUCT_COLUMNS)),
)

# Tercis (P33, P66) de cada indicador de movimentação, calculados sobre a
# base Bronze (ver docs/qualidade_dados.md) — usados para classificar cada
# indicador em Baixa/Média/Alta antes de combinar pela moda em
# src/features/movimentacao.py (add_nivel_movimentacao).
TERCIS_MOVIMENTACAO = {
    "SALDO_MEDIO": (78_900, 163_530),
    "PIX_MENSAL": (32, 66),
    "COMPRAS_CARTAO": (6_745, 13_131),
}

# Rótulos de CLASSIFICACAO, em ordem crescente de INDICE_CLASSIFICACAO
# (quartis). Prefixo alfabético para ordenação no Power BI.
# Ver src/features/classificacao.py (add_classificacao).
CLASSIFICACAO_LABELS = ("A - Inicial", "B - Em Desenvolvimento", "C - Maduro", "D - Engajado")

# Pesos de cada pilar na soma ponderada que forma INDICE_CLASSIFICACAO.
# Devem somar 1.0; 25% cada por padrão (nenhuma dimensão priorizada no
# desafio) — ver docs/regras_negocio.md (seção 5.2).
CLASSIFICACAO_PESOS = {
    "produtos": 0.25,
    "relacionamento": 0.25,
    "saldo": 0.25,
    "utilizacao": 0.25,
}

# Critérios das três flags de oportunidade (src/features/oportunidades.py,
# add_flags_oportunidade). Ver docs/regras_negocio.md (seção 6).
OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS = {
    "faixa_renda": FAIXAS_RENDA[-1][0],
    "qtd_produtos_max": 2,
}
OPORTUNIDADE_BAIXA_UTILIZACAO = {
    "nivel_movimentacao": "Baixa",
    "qtd_produtos_min": 2,
}
OPORTUNIDADE_POTENCIAL_CRESCIMENTO = {
    "classificacao": CLASSIFICACAO_LABELS[1],
    "nivel_movimentacao": {"Média", "Alta"},
}
