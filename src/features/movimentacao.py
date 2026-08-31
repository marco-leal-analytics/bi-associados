"""Nível de movimentação: classifica SALDO_MEDIO, PIX_MENSAL e
COMPRAS_CARTAO por tercis próprios e combina os três pela moda.
Ver `docs/regras_negocio.md` (seção 4).
"""

import pandas as pd

from src.config.settings import TERCIS_MOVIMENTACAO

NIVEIS_MOVIMENTACAO = ("Baixa", "Média", "Alta")
DESEMPATE_COLUNA = "SALDO_MEDIO"


def _classificar_por_tercil(serie, limites):
    """Classifica uma série numérica em Baixa/Média/Alta por dois cortes.

    Args:
        serie: Coluna numérica a classificar (ex.: `SALDO_MEDIO`).
        limites: Tupla `(p33, p66)` com os cortes do 33º e 66º percentil
            (ver `TERCIS_MOVIMENTACAO`). Valores `<= p33` viram "Baixa",
            entre `p33` e `p66` viram "Média", `> p66` viram "Alta".

    Returns:
        `pandas.Categorical` ordenado com as categorias de
        `NIVEIS_MOVIMENTACAO`.
    """
    baixo, alto = limites
    bins = [-float("inf"), baixo, alto, float("inf")]
    return pd.Categorical(
        pd.cut(serie, bins=bins, labels=NIVEIS_MOVIMENTACAO),
        categories=NIVEIS_MOVIMENTACAO,
        ordered=True,
    )


def _moda_com_desempate(row, colunas_nivel, coluna_desempate):
    """Retorna a classificação mais frequente entre as colunas de nível de uma linha.

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
        O rótulo de nível (Baixa/Média/Alta) vencedor para a linha.
    """
    contagem = row[colunas_nivel].value_counts()
    if len(contagem) == len(colunas_nivel):
        return row[coluna_desempate]
    return contagem.idxmax()


def add_nivel_movimentacao(df):
    """Adiciona `NIVEL_MOVIMENTACAO`, combinando os três indicadores por moda.

    Cada indicador em `TERCIS_MOVIMENTACAO` é primeiro classificado
    individualmente (colunas auxiliares `NIVEL_{indicador}`); o nível
    final do associado é a moda entre os três, com o desempate descrito
    em `_moda_com_desempate`.

    Args:
        df: `DataFrame` (Gold, já consolidado) contendo as colunas
            listadas em `TERCIS_MOVIMENTACAO` (`SALDO_MEDIO`,
            `PIX_MENSAL`, `COMPRAS_CARTAO`).

    Returns:
        Cópia de `df` com uma coluna `NIVEL_{indicador}` por indicador e
        `NIVEL_MOVIMENTACAO` (categórica ordenada) adicionadas.
    """
    df = df.copy()

    colunas_nivel = [f"NIVEL_{coluna}" for coluna in TERCIS_MOVIMENTACAO]
    for coluna, limites in TERCIS_MOVIMENTACAO.items():
        df[f"NIVEL_{coluna}"] = _classificar_por_tercil(df[coluna], limites)

    nivel = df.apply(
        _moda_com_desempate,
        axis=1,
        colunas_nivel=colunas_nivel,
        coluna_desempate=f"NIVEL_{DESEMPATE_COLUNA}",
    )
    df["NIVEL_MOVIMENTACAO"] = pd.Categorical(
        nivel, categories=NIVEIS_MOVIMENTACAO, ordered=True
    )

    return df
