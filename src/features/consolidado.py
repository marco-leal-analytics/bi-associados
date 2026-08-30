from src.config.settings import KEY_COLUMN
from src.features.associados import add_faixa_renda, add_indicadores_relacionamento
from src.features.classificacao import add_classificacao
from src.features.movimentacao import add_nivel_movimentacao
from src.features.oportunidades import add_flags_oportunidade
from src.features.produtos import add_indicadores_produtos


def build_features(associados, produtos, movimentacao, reference_date=None):
    associados = add_faixa_renda(add_indicadores_relacionamento(associados, reference_date))
    produtos = add_indicadores_produtos(produtos)

    df = associados.merge(produtos, on=KEY_COLUMN, how="inner", validate="one_to_one")
    df = df.merge(movimentacao, on=KEY_COLUMN, how="inner", validate="one_to_one")
    df = add_nivel_movimentacao(df)
    df = add_classificacao(df)
    df = add_flags_oportunidade(df)

    return df
