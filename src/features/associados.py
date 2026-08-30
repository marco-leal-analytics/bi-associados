import pandas as pd

from src.config.settings import DIAS_POR_ANO, FAIXAS_RENDA

FAIXA_RENDA_NAO_INFORMADO = "Não informado"


def add_indicadores_relacionamento(df, reference_date=None):
    df = df.copy()
    reference_date = reference_date or pd.Timestamp.now().normalize()

    dias = (reference_date - df["DATA_ASSOCIACAO"]).dt.days.astype("Int64")
    dias = dias.mask(df["DATA_ASSOCIACAO_INVALIDA"])

    df["TEMPO_RELACIONAMENTO_DIAS"] = dias
    df["TEMPO_RELACIONAMENTO_ANOS"] = (dias / DIAS_POR_ANO).round(2)

    return df


def add_faixa_renda(df):
    df = df.copy()

    labels, _, maximos = zip(*FAIXAS_RENDA)
    bins = [0, *maximos[:-1], float("inf")]

    faixa = pd.cut(df["RENDA_MENSAL"], bins=bins, labels=labels, include_lowest=True)
    df["FAIXA_RENDA"] = faixa.cat.add_categories([FAIXA_RENDA_NAO_INFORMADO]).fillna(
        FAIXA_RENDA_NAO_INFORMADO
    )

    return df
