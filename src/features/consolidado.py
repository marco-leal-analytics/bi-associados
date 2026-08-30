from src.config.settings import KEY_COLUMN
from src.features.associados import add_faixa_renda, add_indicadores_relacionamento
from src.features.produtos import add_indicadores_produtos


def build_features(associados, produtos, movimentacao, reference_date=None):
    associados = add_faixa_renda(add_indicadores_relacionamento(associados, reference_date))
    produtos = add_indicadores_produtos(produtos)

    df = associados.merge(produtos, on=KEY_COLUMN, how="inner")
    df = df.merge(movimentacao, on=KEY_COLUMN, how="inner")

    return df
