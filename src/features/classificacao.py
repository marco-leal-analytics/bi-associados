import pandas as pd

from src.config.settings import CLASSIFICACAO_LABELS, CLASSIFICACAO_PESOS

SCORE_NEUTRO_TEMPO_INDISPONIVEL = 0.5


def add_classificacao(df):
    df = df.copy()

    score_produtos = df["INDICE_DIVERSIFICACAO"].rank(pct=True)
    score_relacionamento = df["TEMPO_RELACIONAMENTO_ANOS"].rank(pct=True)
    score_saldo = df["SALDO_MEDIO"].rank(pct=True)
    score_utilizacao = (df["PIX_MENSAL"].rank(pct=True) + df["COMPRAS_CARTAO"].rank(pct=True)) / 2

    df["CLASSIFICACAO_TEMPO_INDISPONIVEL"] = score_relacionamento.isna()
    score_relacionamento = score_relacionamento.fillna(SCORE_NEUTRO_TEMPO_INDISPONIVEL)

    df["SCORE_PRODUTOS"] = score_produtos.round(4)
    df["SCORE_RELACIONAMENTO"] = score_relacionamento.round(4)
    df["SCORE_SALDO"] = score_saldo.round(4)
    df["SCORE_UTILIZACAO"] = score_utilizacao.round(4)

    df["INDICE_CLASSIFICACAO"] = (
        score_produtos * CLASSIFICACAO_PESOS["produtos"]
        + score_relacionamento * CLASSIFICACAO_PESOS["relacionamento"]
        + score_saldo * CLASSIFICACAO_PESOS["saldo"]
        + score_utilizacao * CLASSIFICACAO_PESOS["utilizacao"]
    ).round(4)

    df["CLASSIFICACAO"] = pd.Categorical(
        pd.qcut(df["INDICE_CLASSIFICACAO"], 4, labels=CLASSIFICACAO_LABELS),
        categories=CLASSIFICACAO_LABELS,
        ordered=True,
    )

    return df
