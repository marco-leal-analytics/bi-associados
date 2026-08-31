"""Limpeza da entidade Produtos (Bronze → Silver): validação do domínio
S/N, conversão para booleano e cálculo de `QTD_PRODUTOS`.
"""

from src.cleaning.common import assert_allowed_nulls, convert_sn_to_bool, handle_duplicate_keys, validate_domain
from src.config.settings import KEY_COLUMN, PRODUCT_COLUMNS

COLUNAS_COM_NULO_PERMITIDO = ()


def clean_produtos(df):
    """Limpa e valida a base bruta de Produtos, produzindo a versão Silver.

    Etapas: tipa `CHAVE`; remove duplicidade de linha e valida unicidade de
    chave; valida que as colunas de produto (`PRODUCT_COLUMNS`) estão
    restritas ao domínio {"S", "N"} e as converte para booleano; calcula
    `QTD_PRODUTOS` como a soma de produtos possuídos; e garante ausência
    de nulos (nenhuma coluna desta entidade tem nulo permitido).

    Args:
        df: `DataFrame` bruto da planilha `Produtos` (Bronze).

    Returns:
        `DataFrame` tratado (Silver), com as colunas de produto booleanas
        e `QTD_PRODUTOS` adicionada.

    Raises:
        ValueError: Se houver `CHAVE` duplicada com dados divergentes,
            algum valor fora do domínio {"S", "N"} em uma coluna de
            produto, ou qualquer nulo residual.
    """
    df = df.copy()

    df[KEY_COLUMN] = df[KEY_COLUMN].astype("int64")
    df, _ = handle_duplicate_keys(df, KEY_COLUMN)

    for column in PRODUCT_COLUMNS:
        invalid_values = validate_domain(df[column], {"S", "N"})
        if invalid_values:
            raise ValueError(f"Valores fora do domínio S/N em {column}: {invalid_values}")
        df[column] = convert_sn_to_bool(df[column])

    df["QTD_PRODUTOS"] = df[list(PRODUCT_COLUMNS)].sum(axis=1).astype("int64")

    

    return df
