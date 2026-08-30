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

PRODUCT_COLUMNS = EXPECTED_COLUMNS_PRODUTOS[1:]

# --- Parâmetros estáveis (regras analíticas e de classificação) ---
DIAS_POR_ANO = 365.25

FAIXAS_RENDA = (
    ("A - Até R$ 3.000", 0, 3_000),
    ("B - R$ 3.001 a R$ 8.000", 3_000, 8_000),
    ("C - R$ 8.001 a R$ 15.000", 8_000, 15_000),
    ("D - Acima de R$ 15.000", 15_000, None),
)

FAIXAS_DIVERSIFICACAO = (
    ("0 - Baixa", 0, 1),
    ("1 - Média", 2, 4),
    ("2 - Alta", 5, len(PRODUCT_COLUMNS)),
)

TERCIS_MOVIMENTACAO = {
    "SALDO_MEDIO": (78_900, 163_530),
    "PIX_MENSAL": (32, 66),
    "COMPRAS_CARTAO": (6_745, 13_131),
}

CLASSIFICACAO_LABELS = ("A - Inicial", "B - Em Desenvolvimento", "C - Maduro", "D - Engajado")

CLASSIFICACAO_PESOS = {
    "produtos": 0.25,
    "relacionamento": 0.25,
    "saldo": 0.25,
    "utilizacao": 0.25,
}

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
