import pandas as pd

from src.config.settings import (
    RAW_ASSOCIADOS_PATH,
    SHEET_ASSOCIADOS,
    SHEET_PRODUTOS,
    SHEET_MOVIMENTACAO,
)

SOURCE_SHEETS = (SHEET_ASSOCIADOS, SHEET_PRODUTOS, SHEET_MOVIMENTACAO)


def read_sheet(file_path, sheet_name):
    return pd.read_excel(file_path, sheet_name=sheet_name)


def load_sources(file_path=RAW_ASSOCIADOS_PATH, sheets=SOURCE_SHEETS):
    return {sheet_name: read_sheet(file_path, sheet_name) for sheet_name in sheets}
