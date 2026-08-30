import pandas as pd
import pytest

from src.config.settings import (
    CLASSIFICACAO_LABELS,
    DIAS_POR_ANO,
    FAIXAS_DIVERSIFICACAO,
    FAIXAS_RENDA,
    KEY_COLUMN,
)
from src.features.associados import (
    FAIXA_RENDA_NAO_INFORMADO,
    add_faixa_renda,
    add_indicadores_relacionamento,
)
from src.features.consolidado import build_features
from src.features.produtos import TOTAL_PRODUTOS_POSSIVEIS, add_indicadores_produtos
from src.pipeline import SILVER_ASSOCIADOS_PATH, SILVER_MOVIMENTACAO_PATH, SILVER_PRODUTOS_PATH


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


@pytest.fixture(scope="module")
def features_consolidadas():
    associados = pd.read_parquet(SILVER_ASSOCIADOS_PATH)
    produtos = pd.read_parquet(SILVER_PRODUTOS_PATH)
    movimentacao = pd.read_parquet(SILVER_MOVIMENTACAO_PATH)
    return build_features(associados, produtos, movimentacao)


def test_indice_diversificacao_dominio(produtos_features):
    assert produtos_features["INDICE_DIVERSIFICACAO"].between(0, 1).all()
    esperado = produtos_features["QTD_PRODUTOS"] / TOTAL_PRODUTOS_POSSIVEIS
    assert (produtos_features["INDICE_DIVERSIFICACAO"].round(4) == esperado.round(4)).all()


def test_nivel_diversificacao_categorias(produtos_features):
    esperado = {nome for nome, _, _ in FAIXAS_DIVERSIFICACAO}
    assert set(produtos_features["NIVEL_DIVERSIFICACAO"].dropna().unique()) == esperado


def test_nivel_diversificacao_consistente_com_qtd_produtos(produtos_features):
    for nome, minimo, maximo in FAIXAS_DIVERSIFICACAO:
        qtd = produtos_features.loc[produtos_features["NIVEL_DIVERSIFICACAO"] == nome, "QTD_PRODUTOS"]
        assert qtd.between(minimo, maximo).all()


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


# --- Consolidação de features ---


def test_features_consolidadas_chave_unica_e_completa(features_consolidadas):
    assert not features_consolidadas[KEY_COLUMN].duplicated().any()
    assert len(features_consolidadas) == 1000


def test_features_consolidadas_contem_indicadores_das_tres_entidades(features_consolidadas):
    colunas_esperadas = {
        "QTD_PRODUTOS",
        "INDICE_DIVERSIFICACAO",
        "NIVEL_DIVERSIFICACAO",
        "TEMPO_RELACIONAMENTO_DIAS",
        "TEMPO_RELACIONAMENTO_ANOS",
        "FAIXA_RENDA",
        "SALDO_MEDIO",
        "PIX_MENSAL",
        "COMPRAS_CARTAO",
    }
    assert colunas_esperadas <= set(features_consolidadas.columns)


# --- Classificação dos associados ---


def test_classificacao_dominio(features_consolidadas):
    assert set(features_consolidadas["CLASSIFICACAO"].dropna().unique()) == set(CLASSIFICACAO_LABELS)
    assert features_consolidadas["CLASSIFICACAO"].notna().all()


def test_classificacao_grupos_balanceados(features_consolidadas):
    contagem = features_consolidadas["CLASSIFICACAO"].value_counts()
    esperado = len(features_consolidadas) / len(CLASSIFICACAO_LABELS)
    assert (contagem.between(esperado * 0.9, esperado * 1.1)).all()


def test_classificacao_indice_no_dominio_0_1(features_consolidadas):
    assert features_consolidadas["INDICE_CLASSIFICACAO"].between(0, 1).all()


def test_classificacao_tempo_indisponivel_consistente_com_tempo_nulo(features_consolidadas):
    tempo_nulo = features_consolidadas["TEMPO_RELACIONAMENTO_ANOS"].isna()
    assert (features_consolidadas.loc[tempo_nulo, "CLASSIFICACAO_TEMPO_INDISPONIVEL"]).all()
    assert (~features_consolidadas.loc[~tempo_nulo, "CLASSIFICACAO_TEMPO_INDISPONIVEL"]).all()
    assert features_consolidadas.loc[tempo_nulo, "CLASSIFICACAO"].notna().all()


def test_classificacao_ordem_coerente_com_saldo_medio(features_consolidadas):
    medias = features_consolidadas.groupby("CLASSIFICACAO", observed=True)["SALDO_MEDIO"].mean()
    medias = medias.reindex(CLASSIFICACAO_LABELS)
    assert medias.is_monotonic_increasing
