from src.cleaning.associados import clean_associados, read_associados
from src.config.settings import SILVER_DIR

SILVER_ASSOCIADOS_PATH = SILVER_DIR / "associados.parquet"


def build_silver_associados(output_path=SILVER_ASSOCIADOS_PATH):
    df = clean_associados(read_associados())
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    return df


if __name__ == "__main__":
    build_silver_associados()
