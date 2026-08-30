import pandas as pd

from src.config.settings import DIAS_POR_ANO


def add_indicadores_relacionamento(df, reference_date=None):
    df = df.copy()
    reference_date = reference_date or pd.Timestamp.now().normalize()

    dias = (reference_date - df["DATA_ASSOCIACAO"]).dt.days.astype("Int64")
    dias = dias.mask(df["DATA_ASSOCIACAO_INVALIDA"])

    df["TEMPO_RELACIONAMENTO_DIAS"] = dias
    df["TEMPO_RELACIONAMENTO_ANOS"] = (dias / DIAS_POR_ANO).round(2)

    return df
