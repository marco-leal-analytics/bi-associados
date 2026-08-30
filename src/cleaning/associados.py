from src.config.settings import RAW_ASSOCIADOS_PATH, SHEET_ASSOCIADOS
from src.io.excel import read_sheet

# from src.cleaning.utils import standardize_text, normalize_categories


def read_associados(file_path=RAW_ASSOCIADOS_PATH):
    return read_sheet(file_path, SHEET_ASSOCIADOS)
