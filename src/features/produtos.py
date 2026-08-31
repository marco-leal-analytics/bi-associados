"""Indicadores derivados da entidade Produtos: índice e nível (ID) de
diversificação de produtos. Ver `docs/regras_negocio.md` (seção 1) e a
dimensão `DIM_NIVEL_DIVERSIFICACAO` (`src/config/settings.py`).
"""

import pandas as pd

from src.config.settings import FAIXAS_DIVERSIFICACAO, PRODUCT_COLUMNS

TOTAL_PRODUTOS_POSSIVEIS = len(PRODUCT_COLUMNS)


def add_indicadores_produtos(df):
    """Adiciona o índice e o nível (ID) de diversificação de produtos.

    `INDICE_DIVERSIFICACAO` é a proporção de produtos possuídos
    (`QTD_PRODUTOS`) sobre o total possível (`TOTAL_PRODUTOS_POSSIVEIS`).
    `NIVEL_DIVERSIFICACAO_ID` classifica `QTD_PRODUTOS` nas faixas
    definidas em `FAIXAS_DIVERSIFICACAO`, gravando o ID da faixa (o
    rótulo correspondente vive em `DIM_NIVEL_DIVERSIFICACAO`).

    Args:
        df: `DataFrame` (Silver) já contendo `QTD_PRODUTOS`.

    Returns:
        Cópia de `df` com `INDICE_DIVERSIFICACAO` (float, 0–1,
        arredondado a 4 casas) e `NIVEL_DIVERSIFICACAO_ID` (int)
        adicionadas.
    """
    df = df.copy()

    df["INDICE_DIVERSIFICACAO"] = (df["QTD_PRODUTOS"] / TOTAL_PRODUTOS_POSSIVEIS).round(4)

    bins = [-1] + [max_qtd for _, _, max_qtd in FAIXAS_DIVERSIFICACAO]
    ids = [id_ for id_, _, _ in FAIXAS_DIVERSIFICACAO]
    faixa = pd.cut(df["QTD_PRODUTOS"], bins=bins, labels=ids)
    df["NIVEL_DIVERSIFICACAO_ID"] = faixa.astype("int64")

    return df
