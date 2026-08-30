import time

import pandas as pd

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
from src.utils.logging import get_logger

logger = get_logger(__name__)

SILVER_ASSOCIADOS_PATH = SILVER_DIR / "associados.parquet"
SILVER_PRODUTOS_PATH = SILVER_DIR / "produtos.parquet"
SILVER_MOVIMENTACAO_PATH = SILVER_DIR / "movimentacao.parquet"

GOLD_FEATURES_PATH = GOLD_DIR / "features.parquet"


def run_ingestion(file_path=RAW_ASSOCIADOS_PATH):
    """Lê as três planilhas da fonte Bronze, sem qualquer transformação."""
    logger.info("Ingestão iniciada: %s", file_path)

    sources = load_sources(file_path)
    associados = sources[SHEET_ASSOCIADOS]
    produtos = sources[SHEET_PRODUTOS]
    movimentacao = sources[SHEET_MOVIMENTACAO]

    logger.info(
        "Ingestão concluída: Associados=%d, Produtos=%d, Movimentacao=%d linhas",
        len(associados),
        len(produtos),
        len(movimentacao),
    )
    return associados, produtos, movimentacao


def run_silver(raw_associados, raw_produtos, raw_movimentacao, reference_date):
    """Valida, limpa e revalida cada entidade (regras em `src/cleaning`) e persiste a Silver."""
    logger.info("Silver iniciada (DATA_REFERENCIA=%s)", reference_date.date())

    associados = clean_associados(raw_associados, reference_date=reference_date)
    produtos = clean_produtos(raw_produtos)
    movimentacao = clean_movimentacao(raw_movimentacao)

    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    associados.to_parquet(SILVER_ASSOCIADOS_PATH, index=False)
    produtos.to_parquet(SILVER_PRODUTOS_PATH, index=False)
    movimentacao.to_parquet(SILVER_MOVIMENTACAO_PATH, index=False)

    logger.info(
        "Silver concluída: %s, %s, %s",
        SILVER_ASSOCIADOS_PATH,
        SILVER_PRODUTOS_PATH,
        SILVER_MOVIMENTACAO_PATH,
    )
    return associados, produtos, movimentacao


def run_gold(associados, produtos, movimentacao, reference_date):
    """Consolida features, classificação e indicadores analíticos (`src/features`) e persiste a Gold."""
    logger.info("Gold iniciada (DATA_REFERENCIA=%s)", reference_date.date())

    features = build_features(associados, produtos, movimentacao, reference_date=reference_date)

    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    features.to_parquet(GOLD_FEATURES_PATH, index=False)

    logger.info("Gold concluída: %s (%d linhas)", GOLD_FEATURES_PATH, len(features))
    return features


def run_pipeline(file_path=RAW_ASSOCIADOS_PATH, reference_date=None):
    """Executa ingestão, Silver e Gold em sequência com uma única DATA_REFERENCIA.

    Capturar `reference_date` uma única vez no início da execução — em vez de
    cada etapa consultar `pd.Timestamp.now()` de forma independente — garante
    que a sinalização de datas futuras (Silver) e o cálculo de tempo de
    relacionamento (Gold) usem exatamente o mesmo "hoje", tornando uma mesma
    rodada do pipeline reproduzível e passível de reexecução com data fixa
    (parâmetro `reference_date`) para depuração ou auditoria.
    """
    reference_date = reference_date or pd.Timestamp.now().normalize()
    started_at = time.perf_counter()
    logger.info("Pipeline iniciado (DATA_REFERENCIA=%s)", reference_date.date())

    raw_associados, raw_produtos, raw_movimentacao = run_ingestion(file_path)
    associados, produtos, movimentacao = run_silver(
        raw_associados, raw_produtos, raw_movimentacao, reference_date
    )
    features = run_gold(associados, produtos, movimentacao, reference_date)

    logger.info("Pipeline concluído em %.2fs", time.perf_counter() - started_at)
    return features


if __name__ == "__main__":
    run_pipeline()
