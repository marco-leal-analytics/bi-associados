from src.cleaning.common import assert_allowed_nulls, flag_out_of_range, handle_duplicate_keys
from src.config.settings import KEY_COLUMN

NUMERIC_COLUMNS = ("SALDO_MEDIO", "PIX_MENSAL", "COMPRAS_CARTAO")
COLUNAS_COM_NULO_PERMITIDO = NUMERIC_COLUMNS


def clean_movimentacao(df):
    df = df.copy()

    df[KEY_COLUMN] = df[KEY_COLUMN].astype("int64")
    df, _ = handle_duplicate_keys(df, KEY_COLUMN)

    df["SALDO_MEDIO"] = df["SALDO_MEDIO"].astype("float64")
    df["COMPRAS_CARTAO"] = df["COMPRAS_CARTAO"].astype("float64")
    df["PIX_MENSAL"] = df["PIX_MENSAL"].astype("int64")

    for column in NUMERIC_COLUMNS:
        treated, is_invalid = flag_out_of_range(df[column], min_value=0)
        df[column] = treated
        df[f"{column}_INVALIDO"] = is_invalid

    assert_allowed_nulls(df, COLUNAS_COM_NULO_PERMITIDO)

    return df
