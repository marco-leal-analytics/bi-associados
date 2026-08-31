"""Limpeza da entidade Associados (Bronze → Silver): padronização de
`CIDADE`, sinalização de `DATA_ASSOCIACAO` futura e tipagem canônica.
Ver `docs/qualidade_dados.md` e `docs/regras_negocio.md` para as regras.
"""

import pandas as pd

from src.cleaning.common import (
    assert_allowed_nulls,
    assert_exact_categories,
    flag_future_dates,
    handle_duplicate_keys,
    normalize_categories,
    standardize_text,
)
from src.config.settings import KEY_COLUMN

CIDADE_CANONICAL_MAP = {
    "P. Branco": "Pato Branco",
    "Chapeco": "Chapecó",
    "Maringa": "Maringá",
}
CIDADE_CATEGORIAS_CANONICAS = {"Pato Branco", "Chapecó", "Cascavel", "Toledo", "Maringá"}
COLUNAS_COM_NULO_PERMITIDO = ("RENDA_MENSAL",)

SILVER_DTYPES_ASSOCIADOS = {
    "CHAVE": "int64",
    "AGENCIA": "int64",
    "RENDA_MENSAL": "float64",
}


def clean_associados(df, reference_date=None):
    """Limpa e valida a base bruta de Associados, produzindo a versão Silver.

    Etapas: tipa `CHAVE`; remove duplicidade de linha e valida unicidade de
    chave; padroniza `NOME`/`CIDADE` e normaliza as variantes de grafia de
    `CIDADE` para o domínio canônico (validando que nenhuma variante
    remanesceu); normaliza `DATA_ASSOCIACAO` e sinaliza datas futuras em
    `DATA_ASSOCIACAO_INVALIDA` (sem alterar o valor original — ver
    `docs/qualidade_dados.md`); tipa as colunas finais; e garante que só
    `RENDA_MENSAL` contenha nulos residuais.

    Args:
        df: `DataFrame` bruto da planilha `Associados` (Bronze).
        reference_date: Data de referência para julgar `DATA_ASSOCIACAO`
            como futura. Se `None`, usa `pandas.Timestamp.now()`
            normalizado. Deve ser a mesma `DATA_REFERENCIA` usada na
            camada Gold (ver `run_pipeline` em `src/pipeline.py`), para
            que a rodada seja consistente.

    Returns:
        `DataFrame` tratado (Silver), com `DATA_ASSOCIACAO_INVALIDA`
        adicionada e os tipos definidos em `SILVER_DTYPES_ASSOCIADOS`.

    Raises:
        ValueError: Se houver `CHAVE` duplicada com dados divergentes
            (`handle_duplicate_keys`), categoria de `CIDADE` fora do
            domínio canônico (`assert_exact_categories`), ou nulo em
            coluna não prevista (`assert_allowed_nulls`).
    """
    df = df.copy()

    df[KEY_COLUMN] = df[KEY_COLUMN].astype("int64")
    df, _ = handle_duplicate_keys(df, KEY_COLUMN)

    df["NOME"] = standardize_text(df["NOME"])
    df["CIDADE"] = normalize_categories(standardize_text(df["CIDADE"]), CIDADE_CANONICAL_MAP)
    assert_exact_categories(df["CIDADE"], CIDADE_CATEGORIAS_CANONICAS)

    df["DATA_ASSOCIACAO"] = pd.to_datetime(df["DATA_ASSOCIACAO"]).dt.normalize()
    reference_date = reference_date or pd.Timestamp.now().normalize()
    _, df["DATA_ASSOCIACAO_INVALIDA"] = flag_future_dates(df["DATA_ASSOCIACAO"], reference_date)

    df = df.astype(SILVER_DTYPES_ASSOCIADOS)
    assert_allowed_nulls(df, COLUNAS_COM_NULO_PERMITIDO)

    return df
