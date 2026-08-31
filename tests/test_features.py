"""Testes da camada Features/Gold: indicadores de produtos, tempo de
relacionamento, faixa de renda, consolidação, nível de movimentação,
classificação, flags de oportunidade e tabelas de dimensão (`src/features/*.py`).
"""

import pandas as pd
import pytest

from src.config.settings import (
    DASHBOARD_COLUMNS,
    DIAS_POR_ANO,
    DIM_AGENCIA,
    DIM_CLASSIFICACAO,
    DIM_FAIXA_RENDA,
    DIM_NIVEL_DIVERSIFICACAO,
    DIM_NIVEL_MOVIMENTACAO,
    DIM_TEMPO_RELACIONAMENTO,
    FAIXA_RENDA_NAO_INFORMADO_ID,
    FAIXAS_DIVERSIFICACAO,
    FAIXAS_RENDA,
    FAIXAS_TEMPO_RELACIONAMENTO,
    KEY_COLUMN,
    OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS,
    OPORTUNIDADE_BAIXA_UTILIZACAO,
    OPORTUNIDADE_POTENCIAL_CRESCIMENTO,
    TEMPO_RELACIONAMENTO_NAO_DISPONIVEL_ID,
    TERCIS_MOVIMENTACAO,
)
from src.features.associados import (
    add_faixa_renda,
    add_faixa_tempo_relacionamento,
    add_indicadores_relacionamento,
)
from src.features.consolidado import build_dashboard_features, build_features
from src.features.dimensoes import build_dim_agencia, build_dimensions
from src.features.movimentacao import IDS_NIVEL_MOVIMENTACAO
from src.features.produtos import TOTAL_PRODUTOS_POSSIVEIS, add_indicadores_produtos
from src.pipeline import SILVER_ASSOCIADOS_PATH, SILVER_MOVIMENTACAO_PATH, SILVER_PRODUTOS_PATH


@pytest.fixture(scope="module")
def produtos_features():
    """Silver de Produtos com INDICE_DIVERSIFICACAO/NIVEL_DIVERSIFICACAO_ID adicionados."""
    df = pd.read_parquet(SILVER_PRODUTOS_PATH)
    return add_indicadores_produtos(df)


@pytest.fixture(scope="module")
def associados_features():
    """Silver de Associados com TEMPO_RELACIONAMENTO_DIAS/_ANOS adicionados."""
    df = pd.read_parquet(SILVER_ASSOCIADOS_PATH)
    return add_indicadores_relacionamento(df)


@pytest.fixture(scope="module")
def associados_faixa_renda():
    """Silver de Associados com FAIXA_RENDA_ID adicionada."""
    df = pd.read_parquet(SILVER_ASSOCIADOS_PATH)
    return add_faixa_renda(df)


@pytest.fixture(scope="module")
def associados_faixa_tempo_relacionamento():
    """Silver de Associados com TEMPO_RELACIONAMENTO_ANOS e _FAIXA_ID adicionadas."""
    df = pd.read_parquet(SILVER_ASSOCIADOS_PATH)
    return add_faixa_tempo_relacionamento(add_indicadores_relacionamento(df))


@pytest.fixture(scope="module")
def features_consolidadas():
    """Base Gold completa: Associados + Produtos + Movimentacao consolidados
    pela CHAVE, com todos os indicadores, classificação e flags de oportunidade.
    """
    associados = pd.read_parquet(SILVER_ASSOCIADOS_PATH)
    produtos = pd.read_parquet(SILVER_PRODUTOS_PATH)
    movimentacao = pd.read_parquet(SILVER_MOVIMENTACAO_PATH)
    return build_features(associados, produtos, movimentacao)


@pytest.fixture(scope="module")
def dimensoes():
    """As quatro tabelas de dimensão (ID -> descrição) da Gold."""
    return build_dimensions()


@pytest.fixture(scope="module")
def dim_agencia():
    """Dimensão AGENCIA (código -> nome de agência)."""
    return build_dim_agencia()


def test_indice_diversificacao_dominio(produtos_features):
    assert produtos_features["INDICE_DIVERSIFICACAO"].between(0, 1).all()
    esperado = produtos_features["QTD_PRODUTOS"] / TOTAL_PRODUTOS_POSSIVEIS
    assert (produtos_features["INDICE_DIVERSIFICACAO"].round(4) == esperado.round(4)).all()


def test_nivel_diversificacao_id_dominio(produtos_features):
    esperado = {id_ for id_, _, _ in FAIXAS_DIVERSIFICACAO}
    assert set(produtos_features["NIVEL_DIVERSIFICACAO_ID"].dropna().unique()) == esperado


def test_nivel_diversificacao_id_consistente_com_qtd_produtos(produtos_features):
    for id_, minimo, maximo in FAIXAS_DIVERSIFICACAO:
        qtd = produtos_features.loc[produtos_features["NIVEL_DIVERSIFICACAO_ID"] == id_, "QTD_PRODUTOS"]
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


def test_faixa_renda_id_dominio(associados_faixa_renda):
    esperado = {id_ for id_, _, _ in FAIXAS_RENDA} | {FAIXA_RENDA_NAO_INFORMADO_ID}
    assert set(associados_faixa_renda["FAIXA_RENDA_ID"].dropna().unique()) == esperado


def test_faixa_renda_id_nao_informado_em_renda_nula(associados_faixa_renda):
    nula = associados_faixa_renda["RENDA_MENSAL"].isna()
    assert (associados_faixa_renda.loc[nula, "FAIXA_RENDA_ID"] == FAIXA_RENDA_NAO_INFORMADO_ID).all()
    assert (associados_faixa_renda.loc[~nula, "FAIXA_RENDA_ID"] != FAIXA_RENDA_NAO_INFORMADO_ID).all()


def test_faixa_renda_id_limites_consistentes(associados_faixa_renda):
    limite_anterior = 0
    for id_, _, maximo in FAIXAS_RENDA:
        renda = associados_faixa_renda.loc[associados_faixa_renda["FAIXA_RENDA_ID"] == id_, "RENDA_MENSAL"]
        assert (renda > limite_anterior).all()
        if maximo is not None:
            assert (renda <= maximo).all()
        limite_anterior = maximo if maximo is not None else limite_anterior


# --- Faixa de tempo de relacionamento ---


def test_faixa_tempo_relacionamento_id_dominio(associados_faixa_tempo_relacionamento):
    esperado = {id_ for id_, _, _ in FAIXAS_TEMPO_RELACIONAMENTO} | {TEMPO_RELACIONAMENTO_NAO_DISPONIVEL_ID}
    assert set(associados_faixa_tempo_relacionamento["TEMPO_RELACIONAMENTO_FAIXA_ID"].dropna().unique()) == esperado


def test_faixa_tempo_relacionamento_id_nao_disponivel_em_data_invalida(associados_faixa_tempo_relacionamento):
    invalida = associados_faixa_tempo_relacionamento["DATA_ASSOCIACAO_INVALIDA"]
    faixa = associados_faixa_tempo_relacionamento["TEMPO_RELACIONAMENTO_FAIXA_ID"]
    assert (faixa[invalida] == TEMPO_RELACIONAMENTO_NAO_DISPONIVEL_ID).all()
    assert (faixa[~invalida] != TEMPO_RELACIONAMENTO_NAO_DISPONIVEL_ID).all()


def test_faixa_tempo_relacionamento_id_limites_consistentes(associados_faixa_tempo_relacionamento):
    limite_anterior_meses = 0
    for id_, _, maximo_meses in FAIXAS_TEMPO_RELACIONAMENTO:
        meses = (
            associados_faixa_tempo_relacionamento.loc[
                associados_faixa_tempo_relacionamento["TEMPO_RELACIONAMENTO_FAIXA_ID"] == id_,
                "TEMPO_RELACIONAMENTO_ANOS",
            ]
            * 12
        )
        assert (meses > limite_anterior_meses).all()
        if maximo_meses is not None:
            assert (meses <= maximo_meses).all()
        limite_anterior_meses = maximo_meses if maximo_meses is not None else limite_anterior_meses


# --- Consolidação de features ---


def test_features_consolidadas_chave_unica_e_completa(features_consolidadas):
    assert not features_consolidadas[KEY_COLUMN].duplicated().any()
    assert len(features_consolidadas) == 1000


def test_features_consolidadas_contem_indicadores_das_tres_entidades(features_consolidadas):
    colunas_esperadas = {
        "QTD_PRODUTOS",
        "INDICE_DIVERSIFICACAO",
        "NIVEL_DIVERSIFICACAO_ID",
        "TEMPO_RELACIONAMENTO_DIAS",
        "TEMPO_RELACIONAMENTO_ANOS",
        "TEMPO_RELACIONAMENTO_FAIXA_ID",
        "FAIXA_RENDA_ID",
        "SALDO_MEDIO",
        "PIX_MENSAL",
        "COMPRAS_CARTAO",
        "NIVEL_MOVIMENTACAO_ID",
    }
    assert colunas_esperadas <= set(features_consolidadas.columns)


# --- Nível de movimentação ---


def test_nivel_movimentacao_id_dominio(features_consolidadas):
    assert set(features_consolidadas["NIVEL_MOVIMENTACAO_ID"].dropna().unique()) <= set(IDS_NIVEL_MOVIMENTACAO)
    assert features_consolidadas["NIVEL_MOVIMENTACAO_ID"].notna().all()


def test_nivel_movimentacao_id_consistente_com_tercis_saldo_medio(features_consolidadas):
    baixo, alto = TERCIS_MOVIMENTACAO["SALDO_MEDIO"]
    coincide_com_saldo = features_consolidadas["NIVEL_MOVIMENTACAO_ID"] == pd.cut(
        features_consolidadas["SALDO_MEDIO"],
        bins=[-float("inf"), baixo, alto, float("inf")],
        labels=IDS_NIVEL_MOVIMENTACAO,
    ).astype("int64")
    # SALDO_MEDIO é o critério de desempate; deve coincidir na maioria dos casos
    # (todas as linhas onde não houve empate entre os três indicadores).
    assert coincide_com_saldo.mean() > 0.5


# --- Classificação dos associados ---


def test_classificacao_id_dominio(features_consolidadas):
    ids_esperados = {id_ for id_, _ in DIM_CLASSIFICACAO}
    assert set(features_consolidadas["CLASSIFICACAO_ID"].dropna().unique()) == ids_esperados
    assert features_consolidadas["CLASSIFICACAO_ID"].notna().all()


def test_classificacao_id_grupos_balanceados(features_consolidadas):
    contagem = features_consolidadas["CLASSIFICACAO_ID"].value_counts()
    esperado = len(features_consolidadas) / len(DIM_CLASSIFICACAO)
    assert (contagem.between(esperado * 0.9, esperado * 1.1)).all()


def test_classificacao_indice_no_dominio_0_1(features_consolidadas):
    assert features_consolidadas["INDICE_CLASSIFICACAO"].between(0, 1).all()


def test_classificacao_tempo_indisponivel_consistente_com_tempo_nulo(features_consolidadas):
    tempo_nulo = features_consolidadas["TEMPO_RELACIONAMENTO_ANOS"].isna()
    assert (features_consolidadas.loc[tempo_nulo, "CLASSIFICACAO_TEMPO_INDISPONIVEL"]).all()
    assert (~features_consolidadas.loc[~tempo_nulo, "CLASSIFICACAO_TEMPO_INDISPONIVEL"]).all()
    assert features_consolidadas.loc[tempo_nulo, "CLASSIFICACAO_ID"].notna().all()


def test_classificacao_ordem_coerente_com_saldo_medio(features_consolidadas):
    ids_em_ordem = [id_ for id_, _ in DIM_CLASSIFICACAO]
    medias = features_consolidadas.groupby("CLASSIFICACAO_ID")["SALDO_MEDIO"].mean()
    medias = medias.reindex(ids_em_ordem)
    assert medias.is_monotonic_increasing


# --- Flags de oportunidade ---


def test_flag_alta_renda_poucos_produtos_consistente(features_consolidadas):
    cfg = OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS
    flag = features_consolidadas["FLAG_OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS"]
    esperado = (features_consolidadas["FAIXA_RENDA_ID"] == cfg["faixa_renda_id"]) & (
        features_consolidadas["QTD_PRODUTOS"] <= cfg["qtd_produtos_max"]
    )
    assert (flag == esperado).all()


def test_flag_baixa_utilizacao_consistente(features_consolidadas):
    cfg = OPORTUNIDADE_BAIXA_UTILIZACAO
    flag = features_consolidadas["FLAG_OPORTUNIDADE_BAIXA_UTILIZACAO"]
    esperado = (features_consolidadas["NIVEL_MOVIMENTACAO_ID"] == cfg["nivel_movimentacao_id"]) & (
        features_consolidadas["QTD_PRODUTOS"] >= cfg["qtd_produtos_min"]
    )
    assert (flag == esperado).all()


def test_flag_potencial_crescimento_consistente(features_consolidadas):
    cfg = OPORTUNIDADE_POTENCIAL_CRESCIMENTO
    flag = features_consolidadas["FLAG_OPORTUNIDADE_POTENCIAL_CRESCIMENTO"]
    esperado = (features_consolidadas["CLASSIFICACAO_ID"] == cfg["classificacao_id"]) & (
        features_consolidadas["NIVEL_MOVIMENTACAO_ID"].isin(cfg["nivel_movimentacao_ids"])
    )
    assert (flag == esperado).all()


def test_flags_oportunidade_sao_booleanas(features_consolidadas):
    colunas = [
        "FLAG_OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS",
        "FLAG_OPORTUNIDADE_BAIXA_UTILIZACAO",
        "FLAG_OPORTUNIDADE_POTENCIAL_CRESCIMENTO",
    ]
    for coluna in colunas:
        assert features_consolidadas[coluna].dtype == bool


# --- Dimensões ---


def test_dimensoes_nomes_esperados(dimensoes):
    assert set(dimensoes.keys()) == {
        "faixa_renda",
        "tempo_relacionamento",
        "nivel_diversificacao",
        "nivel_movimentacao",
        "classificacao",
    }


def test_dimensoes_schema_e_chave_unica(dimensoes):
    for nome, dim in dimensoes.items():
        assert list(dim.columns) == ["ID", "DESCRICAO"], nome
        assert not dim["ID"].duplicated().any(), nome
        assert dim["DESCRICAO"].notna().all(), nome


def test_dimensao_faixa_renda_bate_com_settings(dimensoes):
    esperado = {id_: descricao for id_, descricao in DIM_FAIXA_RENDA}
    obtido = dict(zip(dimensoes["faixa_renda"]["ID"], dimensoes["faixa_renda"]["DESCRICAO"]))
    assert obtido == esperado


def test_dimensao_tempo_relacionamento_bate_com_settings(dimensoes):
    esperado = {id_: descricao for id_, descricao in DIM_TEMPO_RELACIONAMENTO}
    obtido = dict(zip(dimensoes["tempo_relacionamento"]["ID"], dimensoes["tempo_relacionamento"]["DESCRICAO"]))
    assert obtido == esperado


def test_dimensao_nivel_diversificacao_bate_com_settings(dimensoes):
    esperado = {id_: descricao for id_, descricao in DIM_NIVEL_DIVERSIFICACAO}
    obtido = dict(zip(dimensoes["nivel_diversificacao"]["ID"], dimensoes["nivel_diversificacao"]["DESCRICAO"]))
    assert obtido == esperado


def test_dimensao_nivel_movimentacao_bate_com_settings(dimensoes):
    esperado = {id_: descricao for id_, descricao in DIM_NIVEL_MOVIMENTACAO}
    obtido = dict(zip(dimensoes["nivel_movimentacao"]["ID"], dimensoes["nivel_movimentacao"]["DESCRICAO"]))
    assert obtido == esperado


def test_dimensao_classificacao_bate_com_settings(dimensoes):
    esperado = {id_: descricao for id_, descricao in DIM_CLASSIFICACAO}
    obtido = dict(zip(dimensoes["classificacao"]["ID"], dimensoes["classificacao"]["DESCRICAO"]))
    assert obtido == esperado


# --- Dimensão AGENCIA ---


def test_dim_agencia_schema_e_chave_unica(dim_agencia):
    assert list(dim_agencia.columns) == ["AGENCIA", "NOME_AGENCIA"]
    assert not dim_agencia["AGENCIA"].duplicated().any()
    assert dim_agencia["NOME_AGENCIA"].notna().all()


def test_dim_agencia_bate_com_settings(dim_agencia):
    esperado = {codigo: nome for codigo, nome in DIM_AGENCIA}
    obtido = dict(zip(dim_agencia["AGENCIA"], dim_agencia["NOME_AGENCIA"]))
    assert obtido == esperado


def test_agencia_da_fato_existe_na_dim_agencia(features_consolidadas, dim_agencia):
    """Integridade referencial: todo código AGENCIA da fato deve existir na dimensão."""
    assert set(features_consolidadas["AGENCIA"].unique()) <= set(dim_agencia["AGENCIA"])


# --- Tabela reduzida para o Power BI ---


def test_dashboard_features_contem_apenas_colunas_esperadas(features_consolidadas):
    dashboard = build_dashboard_features(features_consolidadas)
    assert list(dashboard.columns) == list(DASHBOARD_COLUMNS)


def test_dashboard_features_chave_unica_e_completa(features_consolidadas):
    dashboard = build_dashboard_features(features_consolidadas)
    assert not dashboard[KEY_COLUMN].duplicated().any()
    assert len(dashboard) == len(features_consolidadas)


def test_dashboard_features_valores_batem_com_a_fato_completa(features_consolidadas):
    dashboard = build_dashboard_features(features_consolidadas)
    for coluna in DASHBOARD_COLUMNS:
        pd.testing.assert_series_equal(dashboard[coluna], features_consolidadas[coluna])


def test_ids_da_fato_existem_nas_dimensoes(features_consolidadas, dimensoes):
    """Integridade referencial: todo ID gravado na fato deve existir na dimensão correspondente."""
    assert set(features_consolidadas["FAIXA_RENDA_ID"].unique()) <= set(dimensoes["faixa_renda"]["ID"])
    assert set(features_consolidadas["TEMPO_RELACIONAMENTO_FAIXA_ID"].unique()) <= set(
        dimensoes["tempo_relacionamento"]["ID"]
    )
    assert set(features_consolidadas["NIVEL_DIVERSIFICACAO_ID"].unique()) <= set(
        dimensoes["nivel_diversificacao"]["ID"]
    )
    assert set(features_consolidadas["NIVEL_MOVIMENTACAO_ID"].unique()) <= set(
        dimensoes["nivel_movimentacao"]["ID"]
    )
    assert set(features_consolidadas["CLASSIFICACAO_ID"].unique()) <= set(dimensoes["classificacao"]["ID"])
