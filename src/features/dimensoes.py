"""Tabelas de dimensão (ID -> descrição) para as faixas/classes/classificações
criadas na Gold. Persistidas separadamente da tabela fato (`run_gold`,
`src/pipeline.py`) em `data/2_gold/dim_*.parquet`, para relacionamento em
estrela no Power BI e para não repetir o rótulo textual em cada linha da fato.
"""

import pandas as pd

from src.config.settings import (
    DIM_AGENCIA,
    DIM_CLASSIFICACAO,
    DIM_FAIXA_RENDA,
    DIM_NIVEL_DIVERSIFICACAO,
    DIM_NIVEL_MOVIMENTACAO,
)

ID_COLUMN = "ID"
DESCRICAO_COLUMN = "DESCRICAO"
AGENCIA_COLUMN = "AGENCIA"
NOME_AGENCIA_COLUMN = "NOME_AGENCIA"


def _build_dim(pairs):
    """Monta um `DataFrame` de dimensão a partir de pares (ID, descrição).

    Args:
        pairs: Sequência de tuplas `(id, descricao)`, ex.: `DIM_FAIXA_RENDA`.

    Returns:
        `DataFrame` com as colunas `ID` (int64) e `DESCRICAO` (string),
        uma linha por par.
    """
    return pd.DataFrame(pairs, columns=[ID_COLUMN, DESCRICAO_COLUMN]).astype(
        {ID_COLUMN: "int64", DESCRICAO_COLUMN: "string"}
    )


def build_dimensions():
    """Monta as quatro tabelas de dimensão usadas pela Gold.

    Returns:
        Dicionário `{nome_da_dimensao: DataFrame}`, com as chaves
        `faixa_renda`, `nivel_diversificacao`, `nivel_movimentacao` e
        `classificacao` — mesmos nomes usados nos arquivos
        `data/2_gold/dim_{nome}.parquet` (ver `run_gold`,
        `src/pipeline.py`).
    """
    return {
        "faixa_renda": _build_dim(DIM_FAIXA_RENDA),
        "nivel_diversificacao": _build_dim(DIM_NIVEL_DIVERSIFICACAO),
        "nivel_movimentacao": _build_dim(DIM_NIVEL_MOVIMENTACAO),
        "classificacao": _build_dim(DIM_CLASSIFICACAO),
    }


def build_dim_agencia():
    """Monta a dimensão AGENCIA (código -> nome de agência).

    Diferente das quatro dimensões de `build_dimensions` (faixa/classe
    calculada sobre os dados, relacionada à fato por um `*_ID`), esta
    relaciona-se com a fato diretamente pela coluna `AGENCIA` — mesmo
    padrão usado por `dim_calendario` (`src/features/calendario.py`),
    por isso fica fora do dicionário genérico. Conteúdo de `DIM_AGENCIA`
    (`src/config/settings.py`) é levantamento de negócio (nomes reais de
    agências da cooperativa), não cálculo sobre a base.

    Returns:
        `DataFrame` com as colunas `AGENCIA` (int64) e `NOME_AGENCIA`
        (string), uma linha por código de agência.
    """
    return pd.DataFrame(DIM_AGENCIA, columns=[AGENCIA_COLUMN, NOME_AGENCIA_COLUMN]).astype(
        {AGENCIA_COLUMN: "int64", NOME_AGENCIA_COLUMN: "string"}
    )
