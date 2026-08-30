from src.cleaning.common import assert_allowed_nulls, convert_sn_to_bool, handle_duplicate_keys, validate_domain
from src.config.settings import KEY_COLUMN, PRODUCT_COLUMNS

COLUNAS_COM_NULO_PERMITIDO = ()


def clean_produtos(df):
    df = df.copy()

    df[KEY_COLUMN] = df[KEY_COLUMN].astype("int64")
    df, _ = handle_duplicate_keys(df, KEY_COLUMN)

    for column in PRODUCT_COLUMNS:
        invalid_values = validate_domain(df[column], {"S", "N"})
        if invalid_values:
            raise ValueError(f"Valores fora do domínio S/N em {column}: {invalid_values}")
        df[column] = convert_sn_to_bool(df[column])

    df["QTD_PRODUTOS"] = df[list(PRODUCT_COLUMNS)].sum(axis=1).astype("int64")

    assert_allowed_nulls(df, COLUNAS_COM_NULO_PERMITIDO)

    return df
