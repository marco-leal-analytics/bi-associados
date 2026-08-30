from src.cleaning.associados import clean_associados
from src.cleaning.movimentacao import clean_movimentacao
from src.cleaning.produtos import clean_produtos
from src.config.settings import (
    GOLD_DIR,
    RAW_ASSOCIADOS_PATH,
    SHEET_ASSOCIADOS,
    SHEET_MOVIMENTACAO,
    SHEET_PRODUTOS,
    SILVER_DIR,
)
from src.features.consolidado import build_features
from src.io.excel import load_sources

SILVER_ASSOCIADOS_PATH = SILVER_DIR / "associados.parquet"
SILVER_PRODUTOS_PATH = SILVER_DIR / "produtos.parquet"
SILVER_MOVIMENTACAO_PATH = SILVER_DIR / "movimentacao.parquet"

GOLD_FEATURES_PATH = GOLD_DIR / "features.parquet"


def run_ingestion(file_path=RAW_ASSOCIADOS_PATH):
    """Lê as três planilhas da fonte Bronze, sem qualquer transformação."""
    sources = load_sources(file_path)
    return sources[SHEET_ASSOCIADOS], sources[SHEET_PRODUTOS], sources[SHEET_MOVIMENTACAO]


def run_silver(raw_associados, raw_produtos, raw_movimentacao):
    """Valida, limpa e revalida cada entidade (regras em `src/cleaning`) e persiste a Silver."""
    associados = clean_associados(raw_associados)
    produtos = clean_produtos(raw_produtos)
    movimentacao = clean_movimentacao(raw_movimentacao)

    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    associados.to_parquet(SILVER_ASSOCIADOS_PATH, index=False)
    produtos.to_parquet(SILVER_PRODUTOS_PATH, index=False)
    movimentacao.to_parquet(SILVER_MOVIMENTACAO_PATH, index=False)

    return associados, produtos, movimentacao


def run_gold(associados, produtos, movimentacao):
    """Consolida features, classificação e indicadores analíticos (`src/features`) e persiste a Gold."""
    features = build_features(associados, produtos, movimentacao)

    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    features.to_parquet(GOLD_FEATURES_PATH, index=False)

    return features


def run_pipeline(file_path=RAW_ASSOCIADOS_PATH):
    raw_associados, raw_produtos, raw_movimentacao = run_ingestion(file_path)
    associados, produtos, movimentacao = run_silver(raw_associados, raw_produtos, raw_movimentacao)
    return run_gold(associados, produtos, movimentacao)


if __name__ == "__main__":
    run_pipeline()
