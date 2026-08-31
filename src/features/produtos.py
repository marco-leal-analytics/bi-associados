"""Indicadores derivados da entidade Produtos: índice e nível de
diversificação de produtos. Ver `docs/regras_negocio.md` (seção 1).
"""

import pandas as pd

from src.config.settings import FAIXAS_DIVERSIFICACAO, PRODUCT_COLUMNS

TOTAL_PRODUTOS_POSSIVEIS = len(PRODUCT_COLUMNS)


def add_indicadores_produtos(df):
    """Adiciona o índice e o nível de diversificação de produtos.

    `INDICE_DIVERSIFICACAO` é a proporção de produtos possuídos
    (`QTD_PRODUTOS`) sobre o total possível (`TOTAL_PRODUTOS_POSSIVEIS`).
    `NIVEL_DIVERSIFICACAO` classifica `QTD_PRODUTOS` nas faixas definidas
    em `FAIXAS_DIVERSIFICACAO` (Baixa/Média/Alta).

    Args:
        df: `DataFrame` (Silver) já contendo `QTD_PRODUTOS`.

    Returns:
        Cópia de `df` com `INDICE_DIVERSIFICACAO` (float, 0–1,
        arredondado a 4 casas) e `NIVEL_DIVERSIFICACAO` (categórica
        ordenada) adicionadas.
    """
    df = df.copy()

    df["INDICE_DIVERSIFICACAO"] = (df["QTD_PRODUTOS"] / TOTAL_PRODUTOS_POSSIVEIS).round(4)

    bins = [-1] + [max_qtd for _, _, max_qtd in FAIXAS_DIVERSIFICACAO]
    labels = [nome for nome, _, _ in FAIXAS_DIVERSIFICACAO]
    df["NIVEL_DIVERSIFICACAO"] = pd.Categorical(
        pd.cut(df["QTD_PRODUTOS"], bins=bins, labels=labels), categories=labels, ordered=True
    )

    return df
