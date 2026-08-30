import pandas as pd

from src.cleaning.common import flag_future_dates, normalize_categories, standardize_text
from src.config.settings import KEY_COLUMN, RAW_ASSOCIADOS_PATH, SHEET_ASSOCIADOS
from src.io.excel import read_sheet

CIDADE_CANONICAL_MAP = {
    "P. Branco": "Pato Branco",
    "Chapeco": "Chapecó",
    "Maringa": "Maringá",
}


def read_associados(file_path=RAW_ASSOCIADOS_PATH):
    return read_sheet(file_path, SHEET_ASSOCIADOS)


def clean_associados(df, reference_date=None):
    df = df.copy()

    df[KEY_COLUMN] = df[KEY_COLUMN].astype("int64")
    df["AGENCIA"] = df["AGENCIA"].astype("int64")
    df["NOME"] = standardize_text(df["NOME"])
    df["CIDADE"] = normalize_categories(standardize_text(df["CIDADE"]), CIDADE_CANONICAL_MAP)
    df["RENDA_MENSAL"] = df["RENDA_MENSAL"].astype("float64")

    df["DATA_ASSOCIACAO"] = pd.to_datetime(df["DATA_ASSOCIACAO"])
    reference_date = reference_date or pd.Timestamp.now().normalize()
    _, df["DATA_ASSOCIACAO_INVALIDA"] = flag_future_dates(df["DATA_ASSOCIACAO"], reference_date)

    return df
