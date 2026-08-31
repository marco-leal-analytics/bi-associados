"""Indicadores derivados da entidade Associados: tempo de relacionamento e
faixa de renda. Ver `docs/regras_negocio.md` (seções 2 e 3).
"""

import pandas as pd

from src.config.settings import DIAS_POR_ANO, FAIXAS_RENDA

FAIXA_RENDA_NAO_INFORMADO = "Não informado"


def add_indicadores_relacionamento(df, reference_date=None):
    """Adiciona o tempo de relacionamento em dias e anos.

    `TEMPO_RELACIONAMENTO_DIAS`/`_ANOS` ficam nulos para os registros
    sinalizados em `DATA_ASSOCIACAO_INVALIDA` (data de associação futura,
    ver `src/cleaning/associados.py`) — o problema de qualidade não é
    fabricado como um valor válido (ex.: zero), apenas preservado como
    nulo, mantendo o registro íntegro para os demais indicadores.

    Args:
        df: `DataFrame` (Silver) com as colunas `DATA_ASSOCIACAO` e
            `DATA_ASSOCIACAO_INVALIDA`.
        reference_date: Data de referência (`DATA_REFERENCIA`) para o
            cálculo de `DATA_REFERENCIA − DATA_ASSOCIACAO`. Se `None`,
            usa `pandas.Timestamp.now()` normalizado. Deve ser a mesma
            data usada na sinalização de `DATA_ASSOCIACAO_INVALIDA` na
            Silver, para consistência dentro de uma mesma rodada do
            pipeline (ver `run_pipeline` em `src/pipeline.py`).

    Returns:
        Cópia de `df` com `TEMPO_RELACIONAMENTO_DIAS` (`Int64`) e
        `TEMPO_RELACIONAMENTO_ANOS` (float, arredondado a 2 casas)
        adicionadas.
    """
    df = df.copy()
    reference_date = reference_date or pd.Timestamp.now().normalize()

    dias = (reference_date - df["DATA_ASSOCIACAO"]).dt.days.astype("Int64")
    dias = dias.mask(df["DATA_ASSOCIACAO_INVALIDA"])

    df["TEMPO_RELACIONAMENTO_DIAS"] = dias
    df["TEMPO_RELACIONAMENTO_ANOS"] = (dias / DIAS_POR_ANO).round(2)

    return df


def add_faixa_renda(df):
    """Classifica `RENDA_MENSAL` em faixas fixas (`FAIXAS_RENDA`).

    Registros com `RENDA_MENSAL` nula recebem a categoria
    `FAIXA_RENDA_NAO_INFORMADO` em vez de serem excluídos ou imputados
    (ver `docs/regras_negocio.md`, seção 3).

    Args:
        df: `DataFrame` com a coluna `RENDA_MENSAL`.

    Returns:
        Cópia de `df` com `FAIXA_RENDA` adicionada (categórica, rótulos
        de `FAIXAS_RENDA` mais `FAIXA_RENDA_NAO_INFORMADO`).
    """
    df = df.copy()

    labels, _, maximos = zip(*FAIXAS_RENDA)
    bins = [0, *maximos[:-1], float("inf")]

    faixa = pd.cut(df["RENDA_MENSAL"], bins=bins, labels=labels, include_lowest=True)
    df["FAIXA_RENDA"] = faixa.cat.add_categories([FAIXA_RENDA_NAO_INFORMADO]).fillna(
        FAIXA_RENDA_NAO_INFORMADO
    )

    return df
