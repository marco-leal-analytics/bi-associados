from src.cleaning.common import flag_out_of_range
from src.config.settings import KEY_COLUMN, RAW_ASSOCIADOS_PATH, SHEET_MOVIMENTACAO
from src.io.excel import read_sheet

NUMERIC_COLUMNS = ("SALDO_MEDIO", "PIX_MENSAL", "COMPRAS_CARTAO")


def read_movimentacao(file_path=RAW_ASSOCIADOS_PATH):
    return read_sheet(file_path, SHEET_MOVIMENTACAO)


def clean_movimentacao(df):
    df = df.copy()

    df[KEY_COLUMN] = df[KEY_COLUMN].astype("int64")
    df["SALDO_MEDIO"] = df["SALDO_MEDIO"].astype("float64")
    df["COMPRAS_CARTAO"] = df["COMPRAS_CARTAO"].astype("float64")
    df["PIX_MENSAL"] = df["PIX_MENSAL"].astype("int64")

    for column in NUMERIC_COLUMNS:
        treated, is_invalid = flag_out_of_range(df[column], min_value=0)
        df[column] = treated
        df[f"{column}_INVALIDO"] = is_invalid

    return df
