import pandas as pd

from src.config.settings import FAIXAS_DIVERSIFICACAO, PRODUCT_COLUMNS

TOTAL_PRODUTOS_POSSIVEIS = len(PRODUCT_COLUMNS)


def add_indicadores_produtos(df):
    df = df.copy()

    df["INDICE_DIVERSIFICACAO"] = (df["QTD_PRODUTOS"] / TOTAL_PRODUTOS_POSSIVEIS).round(4)

    bins = [-1] + [max_qtd for _, _, max_qtd in FAIXAS_DIVERSIFICACAO]
    labels = [nome for nome, _, _ in FAIXAS_DIVERSIFICACAO]
    df["NIVEL_DIVERSIFICACAO"] = pd.Categorical(
        pd.cut(df["QTD_PRODUTOS"], bins=bins, labels=labels), categories=labels, ordered=True
    )

    return df
