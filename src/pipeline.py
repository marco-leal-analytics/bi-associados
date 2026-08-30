from src.io.excel import load_sources
from src.cleaning.associados import clean_associados
from src.cleaning.produtos import clean_produtos
from src.cleaning.movimentacao import clean_movimentacao
from src.features.associados import build_associate_features
from src.validation.quality import validate_sources


def run_pipeline(input_file: str):
    sources = load_sources(input_file)
    validate_sources(sources)

    associados = clean_associados(sources["Associados"])
    produtos = clean_produtos(sources["Produtos"])
    movimentacao = clean_movimentacao(sources["Movimentacao"])

    analytics = build_associate_features(
        associados, produtos, movimentacao
    )

    return analytics


if __name__ == "__main__":
    run_pipeline("data/raw/teste_bi_base_crua.xlsx")
