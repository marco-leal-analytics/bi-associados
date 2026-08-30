import pandas as pd

from src.config.settings import RAW_ASSOCIADOS_PATH, SHEET_MOVIMENTACAO
from src.io.excel import read_sheet


def read_movimentacao(file_path=RAW_ASSOCIADOS_PATH):
    return read_sheet(file_path, SHEET_MOVIMENTACAO)
