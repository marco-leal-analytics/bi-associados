import pandas as pd


def calculate_income_band(income):
    if pd.isna(income):
        return "Não informado"
    if income <= 3000:
        return "Até R$ 3.000"
    if income <= 8000:
        return "R$ 3.001 a R$ 8.000"
    if income <= 15000:
        return "R$ 8.001 a R$ 15.000"
    return "Acima de R$ 15.000"


def calculate_relationship_years(date_association, reference_date=None):
    reference_date = reference_date or pd.Timestamp.today().normalize()
    if pd.isna(date_association):
        return pd.NA
    return round((reference_date - date_association).days / 365.25, 2)


def build_associate_features(associados, produtos, movimentacao):
    df = associados.merge(
        produtos[["CHAVE", "QTD_PRODUTOS"]],
        on="CHAVE",
        how="left",
        validate="one_to_one",
    ).merge(
        movimentacao,
        on="CHAVE",
        how="left",
        validate="one_to_one",
    )

    df["FAIXA_RENDA"] = df["RENDA_MENSAL"].apply(calculate_income_band)
    df["ANOS_RELACIONAMENTO"] = df["DATA_ASSOCIACAO"].apply(
        calculate_relationship_years
    )

    return df
