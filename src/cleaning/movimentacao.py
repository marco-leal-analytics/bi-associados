import pandas as pd


def clean_movimentacao(df):
    df = df.copy()

    numeric_columns = [
        "SALDO_MEDIO",
        "PIX_MENSAL",
        "COMPRAS_CARTAO",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df
