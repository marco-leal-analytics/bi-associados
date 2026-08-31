"""Nível (ID) de movimentação: classifica SALDO_MEDIO, PIX_MENSAL e
COMPRAS_CARTAO por tercis próprios e combina os três pela moda. Os IDs
seguem a dimensão compartilhada `DIM_NIVEL_MOVIMENTACAO`
(`src/config/settings.py`). Ver `docs/regras_negocio.md` (seção 4).
"""

import pandas as pd

from src.config.settings import DIM_NIVEL_MOVIMENTACAO, TERCIS_MOVIMENTACAO

IDS_NIVEL_MOVIMENTACAO = tuple(id_ for id_, _ in DIM_NIVEL_MOVIMENTACAO)
DESEMPATE_COLUNA = "SALDO_MEDIO"


def _classificar_por_tercil(serie, limites):
    """Classifica uma série numérica em Baixa/Média/Alta (ID) por dois cortes.

    Args:
        serie: Coluna numérica a classificar (ex.: `SALDO_MEDIO`).
        limites: Tupla `(p33, p66)` com os cortes do 33º e 66º percentil
            (ver `TERCIS_MOVIMENTACAO`). Valores `<= p33` viram o ID de
            "Baixa", entre `p33` e `p66` viram o de "Média", `> p66` o de
            "Alta" (IDs de `DIM_NIVEL_MOVIMENTACAO`).

    Returns:
        `Series` de inteiros com os IDs de `IDS_NIVEL_MOVIMENTACAO`.
    """
    baixo, alto = limites
    bins = [-float("inf"), baixo, alto, float("inf")]
    return pd.cut(serie, bins=bins, labels=IDS_NIVEL_MOVIMENTACAO).astype("int64")


def _moda_com_desempate(row, colunas_nivel, coluna_desempate):
    """Retorna o ID de nível mais frequente entre as colunas de uma linha.

    Com três colunas, só há empate quando as três divergem entre si (cada
    uma aparece uma única vez); nesse caso, prevalece `coluna_desempate`
    (indicador mais estável de relacionamento financeiro — ver
    `docs/regras_negocio.md`, seção 4). Qualquer outra distribuição (duas
    iguais e uma diferente, ou as três iguais) tem moda única e sem ambiguidade.

    Args:
        row: Linha do `DataFrame` (`Series`), acessada via `DataFrame.apply(axis=1)`.
        colunas_nivel: Nomes das colunas de nível (uma por indicador de
            movimentação) a comparar.
        coluna_desempate: Nome da coluna de nível a usar como critério de
            desempate em caso de empate triplo.

    Returns:
        O ID de nível (Baixa/Média/Alta) vencedor para a linha.
    """
    contagem = row[colunas_nivel].value_counts()
    if len(contagem) == len(colunas_nivel):
        return row[coluna_desempate]
    return contagem.idxmax()


def add_nivel_movimentacao(df):
    """Adiciona `NIVEL_MOVIMENTACAO_ID`, combinando os três indicadores por moda.

    Cada indicador em `TERCIS_MOVIMENTACAO` é primeiro classificado
    individualmente (colunas auxiliares `NIVEL_{indicador}_ID`); o nível
    final do associado é a moda entre os três, com o desempate descrito
    em `_moda_com_desempate`.

    Args:
        df: `DataFrame` (Gold, já consolidado) contendo as colunas
            listadas em `TERCIS_MOVIMENTACAO` (`SALDO_MEDIO`,
            `PIX_MENSAL`, `COMPRAS_CARTAO`).

    Returns:
        Cópia de `df` com uma coluna `NIVEL_{indicador}_ID` por indicador
        e `NIVEL_MOVIMENTACAO_ID` (int) adicionadas.
    """
    df = df.copy()

    colunas_nivel = [f"NIVEL_{coluna}_ID" for coluna in TERCIS_MOVIMENTACAO]
    for coluna, limites in TERCIS_MOVIMENTACAO.items():
        df[f"NIVEL_{coluna}_ID"] = _classificar_por_tercil(df[coluna], limites)

    df["NIVEL_MOVIMENTACAO_ID"] = df.apply(
        _moda_com_desempate,
        axis=1,
        colunas_nivel=colunas_nivel,
        coluna_desempate=f"NIVEL_{DESEMPATE_COLUNA}_ID",
    ).astype("int64")

    return df
