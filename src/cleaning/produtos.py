from src.cleaning.common import standardize_text


def clean_produtos(df):
    df = df.copy()

    product_columns = [
        "CONTA_CORRENTE",
        "CARTAO",
        "CREDITO",
        "INVESTIMENTO",
        "CONSORCIO",
        "SEGURO",
    ]

    for column in product_columns:
        df[column] = standardize_text(df[column]).str.upper()

    df["QTD_PRODUTOS"] = (
        df[product_columns].eq("S").sum(axis=1)
    )

    return df
