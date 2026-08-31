"""Limpeza da entidade Movimentacao (Bronze → Silver): tipagem numérica e
sinalização de valores fora do domínio (negativos) por coluna.
"""

from src.cleaning.common import assert_allowed_nulls, flag_out_of_range, handle_duplicate_keys
from src.config.settings import KEY_COLUMN

NUMERIC_COLUMNS = ("SALDO_MEDIO", "PIX_MENSAL", "COMPRAS_CARTAO")
COLUNAS_COM_NULO_PERMITIDO = NUMERIC_COLUMNS


def clean_movimentacao(df):
    """Limpa e valida a base bruta de Movimentacao, produzindo a versão Silver.

    Etapas: tipa `CHAVE`; remove duplicidade de linha e valida unicidade de
    chave; tipa as métricas numéricas (`NUMERIC_COLUMNS`); e, para cada
    uma, sinaliza valores negativos em `{coluna}_INVALIDO` e os substitui
    por `NaN` (sem descartar o registro — ver `flag_out_of_range` em
    `src/cleaning/common.py`).

    Args:
        df: `DataFrame` bruto da planilha `Movimentacao` (Bronze).

    Returns:
        `DataFrame` tratado (Silver), com as métricas numéricas tipadas e
        uma coluna `{coluna}_INVALIDO` por métrica.

    Raises:
        ValueError: Se houver `CHAVE` duplicada com dados divergentes, ou
            nulo em coluna fora de `COLUNAS_COM_NULO_PERMITIDO` (os nulos
            introduzidos pela própria sinalização de valores negativos
            são esperados e permitidos).
    """
    df = df.copy()

    df[KEY_COLUMN] = df[KEY_COLUMN].astype("int64")
    df, _ = handle_duplicate_keys(df, KEY_COLUMN)

    df["SALDO_MEDIO"] = df["SALDO_MEDIO"].astype("float64")
    df["COMPRAS_CARTAO"] = df["COMPRAS_CARTAO"].astype("float64")
    df["PIX_MENSAL"] = df["PIX_MENSAL"].astype("int64")

    for column in NUMERIC_COLUMNS:
        treated, is_invalid = flag_out_of_range(df[column], min_value=0)
        df[column] = treated
        df[f"{column}_INVALIDO"] = is_invalid

    assert_allowed_nulls(df, COLUNAS_COM_NULO_PERMITIDO)

    return df
