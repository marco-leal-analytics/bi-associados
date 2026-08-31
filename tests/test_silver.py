"""Testes da camada Silver: tipos, domínios, nulos residuais e integridade
referencial de Associados, Produtos e Movimentacao (`src/cleaning/*.py`),
lidos diretamente dos parquets gerados pelo pipeline.
"""

import pandas as pd
import pytest

from src.cleaning.associados import CIDADE_CATEGORIAS_CANONICAS
from src.config.settings import (
    EXPECTED_COLUMNS_MOVIMENTACAO,
    EXPECTED_COLUMNS_PRODUTOS,
    KEY_COLUMN,
    PRODUCT_COLUMNS,
)
from src.pipeline import SILVER_ASSOCIADOS_PATH, SILVER_MOVIMENTACAO_PATH, SILVER_PRODUTOS_PATH

BRONZE_ROW_COUNT = 1000


@pytest.fixture(scope="module")
def associados():
    """Silver de Associados, lida do parquet gerado pelo pipeline."""
    return pd.read_parquet(SILVER_ASSOCIADOS_PATH)


@pytest.fixture(scope="module")
def produtos():
    """Silver de Produtos, lida do parquet gerado pelo pipeline."""
    return pd.read_parquet(SILVER_PRODUTOS_PATH)


@pytest.fixture(scope="module")
def movimentacao():
    """Silver de Movimentacao, lida do parquet gerado pelo pipeline."""
    return pd.read_parquet(SILVER_MOVIMENTACAO_PATH)


def assert_unique_key(df):
    """Verifica que KEY_COLUMN é única e que não há linha duplicada.

    Args:
        df: `DataFrame` a validar.
    """
    assert not df[KEY_COLUMN].duplicated().any()
    assert not df.duplicated().any()


# --- Associados ---


def test_associados_row_count(associados):
    assert len(associados) == BRONZE_ROW_COUNT


def test_associados_chave_unica(associados):
    assert_unique_key(associados)


def test_associados_cidade_categorias_canonicas(associados):
    assert set(associados["CIDADE"].dropna().unique()) == CIDADE_CATEGORIAS_CANONICAS


def test_associados_agencia_dominio(associados):
    assert set(associados["AGENCIA"].unique()) <= {1, 2, 3, 4, 5}


def test_associados_nulos_residuais(associados):
    columns_with_nulls = set(associados.columns[associados.isna().any()])
    assert columns_with_nulls <= {"RENDA_MENSAL"}


def test_associados_renda_nao_negativa(associados):
    assert (associados["RENDA_MENSAL"].dropna() >= 0).all()


def test_associados_data_associacao_invalida_consistente(associados):
    # DATA_ASSOCIACAO_INVALIDA sinaliza sem editar o dado de origem (ver qualidade_dados.md),
    # por isso a data futura permanece no campo e só é tratada como nula no cálculo derivado
    # de TEMPO_RELACIONAMENTO (camada Gold).
    reference_date = pd.Timestamp.now().normalize()
    flagged = associados["DATA_ASSOCIACAO_INVALIDA"]
    assert (associados.loc[flagged, "DATA_ASSOCIACAO"] > reference_date).all()
    assert (associados.loc[~flagged, "DATA_ASSOCIACAO"] <= reference_date).all()


def test_associados_tipos(associados):
    assert associados["CHAVE"].dtype == "int64"
    assert associados["AGENCIA"].dtype == "int64"
    assert associados["RENDA_MENSAL"].dtype == "float64"
    assert pd.api.types.is_datetime64_any_dtype(associados["DATA_ASSOCIACAO"])


# --- Produtos ---


def test_produtos_row_count(produtos):
    assert len(produtos) == BRONZE_ROW_COUNT


def test_produtos_chave_unica(produtos):
    assert_unique_key(produtos)


def test_produtos_colunas_esperadas(produtos):
    assert set(EXPECTED_COLUMNS_PRODUTOS) <= set(produtos.columns)


def test_produtos_flags_booleanas(produtos):
    for column in PRODUCT_COLUMNS:
        assert produtos[column].dtype == bool


def test_produtos_qtd_produtos_dominio(produtos):
    assert produtos["QTD_PRODUTOS"].between(0, len(PRODUCT_COLUMNS)).all()
    assert (produtos["QTD_PRODUTOS"] == produtos[list(PRODUCT_COLUMNS)].sum(axis=1)).all()


def test_produtos_sem_nulos(produtos):
    assert not produtos.isna().any().any()


# --- Movimentacao ---


def test_movimentacao_row_count(movimentacao):
    assert len(movimentacao) == BRONZE_ROW_COUNT


def test_movimentacao_chave_unica(movimentacao):
    assert_unique_key(movimentacao)


def test_movimentacao_colunas_esperadas(movimentacao):
    assert set(EXPECTED_COLUMNS_MOVIMENTACAO) <= set(movimentacao.columns)


def test_movimentacao_valores_nao_negativos_ou_sinalizados(movimentacao):
    for column in ("SALDO_MEDIO", "PIX_MENSAL", "COMPRAS_CARTAO"):
        valores = movimentacao.loc[~movimentacao[f"{column}_INVALIDO"], column]
        assert (valores.dropna() >= 0).all()


# --- Integridade referencial entre as três entidades ---


def test_chaves_identicas_entre_entidades(associados, produtos, movimentacao):
    chaves_associados = set(associados[KEY_COLUMN])
    chaves_produtos = set(produtos[KEY_COLUMN])
    chaves_movimentacao = set(movimentacao[KEY_COLUMN])

    assert chaves_associados == chaves_produtos == chaves_movimentacao
    assert chaves_associados == set(range(1, BRONZE_ROW_COUNT + 1))
