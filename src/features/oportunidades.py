from src.config.settings import (
    OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS,
    OPORTUNIDADE_BAIXA_UTILIZACAO,
    OPORTUNIDADE_POTENCIAL_CRESCIMENTO,
)


def add_flags_oportunidade(df):
    df = df.copy()

    cfg = OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS
    df["FLAG_OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS"] = (
        (df["FAIXA_RENDA"] == cfg["faixa_renda"]) & (df["QTD_PRODUTOS"] <= cfg["qtd_produtos_max"])
    )

    cfg = OPORTUNIDADE_BAIXA_UTILIZACAO
    df["FLAG_OPORTUNIDADE_BAIXA_UTILIZACAO"] = (
        (df["NIVEL_MOVIMENTACAO"] == cfg["nivel_movimentacao"]) & (df["QTD_PRODUTOS"] >= cfg["qtd_produtos_min"])
    )

    cfg = OPORTUNIDADE_POTENCIAL_CRESCIMENTO
    df["FLAG_OPORTUNIDADE_POTENCIAL_CRESCIMENTO"] = (
        (df["CLASSIFICACAO"] == cfg["classificacao"])
        & (df["NIVEL_MOVIMENTACAO"].isin(cfg["nivel_movimentacao"]))
    )

    return df
