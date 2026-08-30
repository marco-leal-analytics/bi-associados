from src.cleaning.common import convert_sn_to_bool, validate_domain
from src.config.settings import KEY_COLUMN, PRODUCT_COLUMNS, RAW_ASSOCIADOS_PATH, SHEET_PRODUTOS
from src.io.excel import read_sheet


def read_produtos(file_path=RAW_ASSOCIADOS_PATH):
    return read_sheet(file_path, SHEET_PRODUTOS)


def clean_produtos(df):
    df = df.copy()

    df[KEY_COLUMN] = df[KEY_COLUMN].astype("int64")

    for column in PRODUCT_COLUMNS:
        invalid_values = validate_domain(df[column], {"S", "N"})
        if invalid_values:
            raise ValueError(f"Valores fora do domínio S/N em {column}: {invalid_values}")
        df[column] = convert_sn_to_bool(df[column])

    df["QTD_PRODUTOS"] = df[list(PRODUCT_COLUMNS)].sum(axis=1)

    return df
