from src.cleaning.common import standardize_text
from src.config.settings import RAW_ASSOCIADOS_PATH, SHEET_PRODUTOS
from src.io.excel import read_sheet


def read_produtos(file_path=RAW_ASSOCIADOS_PATH):
    return read_sheet(file_path, SHEET_PRODUTOS)

