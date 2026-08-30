import pandas as pd

from src.cleaning.associados import clean_associados, read_associados
from src.cleaning.movimentacao import clean_movimentacao, read_movimentacao
from src.cleaning.produtos import clean_produtos, read_produtos
from src.config.settings import GOLD_DIR, SILVER_DIR
from src.features.consolidado import build_features

SILVER_ASSOCIADOS_PATH = SILVER_DIR / "associados.parquet"
SILVER_PRODUTOS_PATH = SILVER_DIR / "produtos.parquet"
SILVER_MOVIMENTACAO_PATH = SILVER_DIR / "movimentacao.parquet"

GOLD_FEATURES_PATH = GOLD_DIR / "features.parquet"


def build_silver_associados(output_path=SILVER_ASSOCIADOS_PATH):
    df = clean_associados(read_associados())
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    return df


def build_silver_produtos(output_path=SILVER_PRODUTOS_PATH):
    df = clean_produtos(read_produtos())
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    return df


def build_silver_movimentacao(output_path=SILVER_MOVIMENTACAO_PATH):
    df = clean_movimentacao(read_movimentacao())
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    return df


def build_gold_features(output_path=GOLD_FEATURES_PATH):
    associados = pd.read_parquet(SILVER_ASSOCIADOS_PATH)
    produtos = pd.read_parquet(SILVER_PRODUTOS_PATH)
    movimentacao = pd.read_parquet(SILVER_MOVIMENTACAO_PATH)

    df = build_features(associados, produtos, movimentacao)
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    return df


if __name__ == "__main__":
    build_silver_associados()
    build_silver_produtos()
    build_silver_movimentacao()
    build_gold_features()
