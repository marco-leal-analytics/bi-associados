import pandas as pd

from src.config.settings import TERCIS_MOVIMENTACAO

NIVEIS_MOVIMENTACAO = ("Baixa", "Média", "Alta")
DESEMPATE_COLUNA = "SALDO_MEDIO"


def _classificar_por_tercil(serie, limites):
    baixo, alto = limites
    bins = [-float("inf"), baixo, alto, float("inf")]
    return pd.Categorical(
        pd.cut(serie, bins=bins, labels=NIVEIS_MOVIMENTACAO),
        categories=NIVEIS_MOVIMENTACAO,
        ordered=True,
    )


def _moda_com_desempate(row, colunas_nivel, coluna_desempate):
    contagem = row[colunas_nivel].value_counts()
    if len(contagem) == len(colunas_nivel):
        return row[coluna_desempate]
    return contagem.idxmax()


def add_nivel_movimentacao(df):
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
