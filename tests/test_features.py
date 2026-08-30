import pandas as pd
import pytest

from src.config.settings import DIAS_POR_ANO, FAIXAS_RENDA, PRODUCT_COLUMNS
from src.features.associados import (
    FAIXA_RENDA_NAO_INFORMADO,
    add_faixa_renda,
    add_indicadores_relacionamento,
)
from src.features.produtos import TOTAL_PRODUTOS_POSSIVEIS, add_indicadores_produtos
from src.pipeline import SILVER_ASSOCIADOS_PATH, SILVER_PRODUTOS_PATH


@pytest.fixture(scope="module")
def produtos_features():
    df = pd.read_parquet(SILVER_PRODUTOS_PATH)
    return add_indicadores_produtos(df)


@pytest.fixture(scope="module")
def associados_features():
    df = pd.read_parquet(SILVER_ASSOCIADOS_PATH)
    return add_indicadores_relacionamento(df)


@pytest.fixture(scope="module")
def associados_faixa_renda():
    df = pd.read_parquet(SILVER_ASSOCIADOS_PATH)
    return add_faixa_renda(df)


def test_indice_diversificacao_dominio(produtos_features):
    assert produtos_features["INDICE_DIVERSIFICACAO"].between(0, 1).all()
    esperado = produtos_features["QTD_PRODUTOS"] / TOTAL_PRODUTOS_POSSIVEIS
    assert (produtos_features["INDICE_DIVERSIFICACAO"].round(4) == esperado.round(4)).all()


def test_nivel_diversificacao_categorias(produtos_features):
    assert set(produtos_features["NIVEL_DIVERSIFICACAO"].dropna().unique()) == {
        "Baixa",
        "Média",
        "Alta",
    }


def test_nivel_diversificacao_consistente_com_qtd_produtos(produtos_features):
    baixa = produtos_features.loc[produtos_features["NIVEL_DIVERSIFICACAO"] == "Baixa", "QTD_PRODUTOS"]
    media = produtos_features.loc[produtos_features["NIVEL_DIVERSIFICACAO"] == "Média", "QTD_PRODUTOS"]
    alta = produtos_features.loc[produtos_features["NIVEL_DIVERSIFICACAO"] == "Alta", "QTD_PRODUTOS"]

    assert baixa.between(0, 1).all()
    assert media.between(2, 4).all()
    assert alta.between(5, len(PRODUCT_COLUMNS)).all()


# --- Indicadores de relacionamento ---


def test_tempo_relacionamento_nulo_em_data_invalida(associados_features):
    invalidos = associados_features["DATA_ASSOCIACAO_INVALIDA"]
    assert associados_features.loc[invalidos, "TEMPO_RELACIONAMENTO_DIAS"].isna().all()
    assert associados_features.loc[invalidos, "TEMPO_RELACIONAMENTO_ANOS"].isna().all()
    assert associados_features.loc[~invalidos, "TEMPO_RELACIONAMENTO_DIAS"].notna().all()


def test_tempo_relacionamento_nao_negativo(associados_features):
    dias = associados_features["TEMPO_RELACIONAMENTO_DIAS"].dropna()
    assert (dias >= 0).all()


def test_tempo_relacionamento_anos_consistente_com_dias(associados_features):
    validos = associados_features["TEMPO_RELACIONAMENTO_DIAS"].notna()
    dias = associados_features.loc[validos, "TEMPO_RELACIONAMENTO_DIAS"].astype("float64")
    anos_esperado = (dias / DIAS_POR_ANO).round(2)
    assert (associados_features.loc[validos, "TEMPO_RELACIONAMENTO_ANOS"] == anos_esperado).all()


# --- Faixa de renda ---


def test_faixa_renda_categorias(associados_faixa_renda):
    esperado = {nome for nome, _, _ in FAIXAS_RENDA} | {FAIXA_RENDA_NAO_INFORMADO}
    assert set(associados_faixa_renda["FAIXA_RENDA"].dropna().unique()) == esperado


def test_faixa_renda_nao_informado_em_renda_nula(associados_faixa_renda):
    nula = associados_faixa_renda["RENDA_MENSAL"].isna()
    assert (associados_faixa_renda.loc[nula, "FAIXA_RENDA"] == FAIXA_RENDA_NAO_INFORMADO).all()
    assert (associados_faixa_renda.loc[~nula, "FAIXA_RENDA"] != FAIXA_RENDA_NAO_INFORMADO).all()


def test_faixa_renda_limites_consistentes(associados_faixa_renda):
    limite_anterior = 0
    for nome, _, maximo in FAIXAS_RENDA:
        renda = associados_faixa_renda.loc[associados_faixa_renda["FAIXA_RENDA"] == nome, "RENDA_MENSAL"]
        assert (renda > limite_anterior).all()
        if maximo is not None:
            assert (renda <= maximo).all()
            limite_anterior = maximo
