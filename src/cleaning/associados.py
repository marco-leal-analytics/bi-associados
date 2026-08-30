import pandas as pd

from src.cleaning.common import (
    assert_allowed_nulls,
    assert_exact_categories,
    flag_future_dates,
    handle_duplicate_keys,
    normalize_categories,
    standardize_text,
)
from src.config.settings import KEY_COLUMN, RAW_ASSOCIADOS_PATH, SHEET_ASSOCIADOS
from src.io.excel import read_sheet

CIDADE_CANONICAL_MAP = {
    "P. Branco": "Pato Branco",
    "Chapeco": "Chapecó",
    "Maringa": "Maringá",
}
CIDADE_CATEGORIAS_CANONICAS = {"Pato Branco", "Chapecó", "Cascavel", "Toledo", "Maringá"}
COLUNAS_COM_NULO_PERMITIDO = ("RENDA_MENSAL",)

SILVER_DTYPES_ASSOCIADOS = {
    "CHAVE": "int64",
    "AGENCIA": "int64",
    "RENDA_MENSAL": "float64",
}


def read_associados(file_path=RAW_ASSOCIADOS_PATH):
    return read_sheet(file_path, SHEET_ASSOCIADOS)


def clean_associados(df, reference_date=None):
    df = df.copy()

    df[KEY_COLUMN] = df[KEY_COLUMN].astype("int64")
    df, _ = handle_duplicate_keys(df, KEY_COLUMN)

    df["NOME"] = standardize_text(df["NOME"])
    df["CIDADE"] = normalize_categories(standardize_text(df["CIDADE"]), CIDADE_CANONICAL_MAP)
    assert_exact_categories(df["CIDADE"], CIDADE_CATEGORIAS_CANONICAS)

    df["DATA_ASSOCIACAO"] = pd.to_datetime(df["DATA_ASSOCIACAO"]).dt.normalize()
    reference_date = reference_date or pd.Timestamp.now().normalize()
    _, df["DATA_ASSOCIACAO_INVALIDA"] = flag_future_dates(df["DATA_ASSOCIACAO"], reference_date)

    df = df.astype(SILVER_DTYPES_ASSOCIADOS)
    assert_allowed_nulls(df, COLUNAS_COM_NULO_PERMITIDO)

    return df
