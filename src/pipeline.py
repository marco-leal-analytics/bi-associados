from src.cleaning.associados import clean_associados, read_associados
from src.cleaning.movimentacao import clean_movimentacao, read_movimentacao
from src.cleaning.produtos import clean_produtos, read_produtos
from src.config.settings import SILVER_DIR

SILVER_ASSOCIADOS_PATH = SILVER_DIR / "associados.parquet"
SILVER_PRODUTOS_PATH = SILVER_DIR / "produtos.parquet"
SILVER_MOVIMENTACAO_PATH = SILVER_DIR / "movimentacao.parquet"


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


if __name__ == "__main__":
    build_silver_associados()
    build_silver_produtos()
    build_silver_movimentacao()
