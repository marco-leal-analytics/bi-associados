"""Testes da Dim_Calendario reduzida (`src/features/calendario.py`), gerada
a partir da fonte externa bruta (`data/0_bronze/raw_Dim_Calendario.xlsx`).
"""

import pandas as pd
import pytest

from src.config.settings import DIM_CALENDARIO_COLUNAS
from src.features.calendario import build_dim_calendario
from src.pipeline import SILVER_ASSOCIADOS_PATH

REFERENCE_DATE = pd.Timestamp("2026-08-30")


@pytest.fixture(scope="module")
def associados():
    return pd.read_parquet(SILVER_ASSOCIADOS_PATH)


@pytest.fixture(scope="module")
def dim_calendario(associados):
    return build_dim_calendario(associados, REFERENCE_DATE)


def test_dim_calendario_contem_apenas_colunas_esperadas(dim_calendario):
    assert list(dim_calendario.columns) == list(DIM_CALENDARIO_COLUNAS)


def test_dim_calendario_data_unica_e_sem_nulos(dim_calendario):
    assert not dim_calendario["DATA"].duplicated().any()
    assert dim_calendario.notna().all().all()


def test_dim_calendario_cobre_intervalo_de_data_associacao(associados, dim_calendario):
    datas_associacao = associados["DATA_ASSOCIACAO"].dt.normalize()
    assert datas_associacao.isin(dim_calendario["DATA"]).all()


def test_dim_calendario_cobre_data_referencia(dim_calendario):
    assert REFERENCE_DATE.normalize() in set(dim_calendario["DATA"])


def test_dim_calendario_ordenada_por_data(dim_calendario):
    assert dim_calendario["DATA"].is_monotonic_increasing


def test_dim_calendario_mes_consistente_com_nome_mes(dim_calendario):
    mapa = dim_calendario.drop_duplicates("MES").set_index("MES")["NOME_MES"]
    assert mapa[1] == "Janeiro"
    assert mapa[12] == "Dezembro"


def test_dim_calendario_trimestre_e_semestre_no_dominio(dim_calendario):
    assert set(dim_calendario["TRIMESTRE"].unique()) <= {1, 2, 3, 4}
    assert set(dim_calendario["SEMESTRE"].unique()) <= {1, 2}
