"""Ponto de entrada do pipeline (`python -m src.pipeline`). Orquestra as
três etapas — ingestão, Silver e Gold — sem conter regra de negócio própria;
toda a lógica de limpeza e features vive em `src/cleaning` e `src/features`.
"""

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
from src.features.consolidado import build_dashboard_features, build_features
from src.features.dimensoes import build_dimensions
from src.io.excel import load_sources
from src.utils.logging import get_logger

logger = get_logger(__name__)

SILVER_ASSOCIADOS_PATH = SILVER_DIR / "associados.parquet"
SILVER_PRODUTOS_PATH = SILVER_DIR / "produtos.parquet"
SILVER_MOVIMENTACAO_PATH = SILVER_DIR / "movimentacao.parquet"

GOLD_FEATURES_PATH = GOLD_DIR / "features.parquet"
GOLD_FEATURES_DASHBOARD_PATH = GOLD_DIR / "features_dashboard.parquet"
GOLD_DIM_PATHS = {
    "faixa_renda": GOLD_DIR / "dim_faixa_renda.parquet",
    "nivel_diversificacao": GOLD_DIR / "dim_nivel_diversificacao.parquet",
    "nivel_movimentacao": GOLD_DIR / "dim_nivel_movimentacao.parquet",
    "classificacao": GOLD_DIR / "dim_classificacao.parquet",
}


def run_ingestion(file_path=RAW_ASSOCIADOS_PATH):
    """Lê as três planilhas da fonte Bronze, sem qualquer transformação.

    Args:
        file_path: Caminho do arquivo Excel Bronze. Por padrão,
            `RAW_ASSOCIADOS_PATH` (`src/config/settings.py`).

    Returns:
        Tupla `(associados, produtos, movimentacao)`, cada um um
        `DataFrame` bruto (uma aba da planilha).
    """
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
    """Valida, limpa e revalida cada entidade (regras em `src/cleaning`) e persiste a Silver.

    Args:
        raw_associados: `DataFrame` bruto de Associados (saída de `run_ingestion`).
        raw_produtos: `DataFrame` bruto de Produtos.
        raw_movimentacao: `DataFrame` bruto de Movimentacao.
        reference_date: `DATA_REFERENCIA` da rodada, repassada a
            `clean_associados` para sinalizar `DATA_ASSOCIACAO_INVALIDA`
            (datas futuras). Deve ser a mesma data usada depois em
            `run_gold`, para consistência dentro da rodada.

    Returns:
        Tupla `(associados, produtos, movimentacao)` já tratados
        (Silver), na mesma ordem persistida em `data/1_silver/`.
    """
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
    """Consolida features, classificação e indicadores analíticos (`src/features`) e persiste a Gold.

    Args:
        associados: `DataFrame` Silver de Associados (saída de `run_silver`).
        produtos: `DataFrame` Silver de Produtos.
        movimentacao: `DataFrame` Silver de Movimentacao.
        reference_date: `DATA_REFERENCIA` da rodada, repassada a
            `build_features` para o cálculo de `TEMPO_RELACIONAMENTO_*`.
            Deve ser a mesma data usada em `run_silver`.

    Returns:
        `DataFrame` Gold consolidado (uma linha por `CHAVE`), o mesmo
        conteúdo persistido em `GOLD_FEATURES_PATH`. As tabelas de
        dimensão (`dim_*.parquet`, ver `GOLD_DIM_PATHS`) e a tabela
        reduzida para o Power BI (`GOLD_FEATURES_DASHBOARD_PATH`) são
        persistidas como efeito colateral, mas não fazem parte do retorno.
    """
    logger.info("Gold iniciada (DATA_REFERENCIA=%s)", reference_date.date())

    features = build_features(associados, produtos, movimentacao, reference_date=reference_date)
    dashboard_features = build_dashboard_features(features)
    dimensions = build_dimensions()

    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    features.to_parquet(GOLD_FEATURES_PATH, index=False)
    dashboard_features.to_parquet(GOLD_FEATURES_DASHBOARD_PATH, index=False)
    for name, dim in dimensions.items():
        dim.to_parquet(GOLD_DIM_PATHS[name], index=False)

    logger.info(
        "Gold concluída: %s (%d linhas, %d colunas), %s (%d colunas), %d dimensões",
        GOLD_FEATURES_PATH,
        len(features),
        len(features.columns),
        GOLD_FEATURES_DASHBOARD_PATH,
        len(dashboard_features.columns),
        len(dimensions),
    )
    return features


def run_pipeline(file_path=RAW_ASSOCIADOS_PATH, reference_date=None):
    """Executa ingestão, Silver e Gold em sequência com uma única DATA_REFERENCIA.

    Capturar `reference_date` uma única vez no início da execução — em vez de
    cada etapa consultar `pd.Timestamp.now()` de forma independente — garante
    que a sinalização de datas futuras (Silver) e o cálculo de tempo de
    relacionamento (Gold) usem exatamente o mesmo "hoje", tornando uma mesma
    rodada do pipeline reproduzível e passível de reexecução com data fixa
    (parâmetro `reference_date`) para depuração ou auditoria.

    Args:
        file_path: Caminho do arquivo Excel Bronze, repassado a
            `run_ingestion`. Por padrão, `RAW_ASSOCIADOS_PATH`.
        reference_date: Data de referência a fixar para toda a rodada. Se
            `None`, usa `pandas.Timestamp.now()` normalizado (o caso de
            uso normal — recalcula os indicadores baseados em data a
            cada execução). Passar um valor explícito reproduz uma
            rodada passada de forma determinística.

    Returns:
        `DataFrame` Gold consolidado (mesmo retorno de `run_gold`).
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
