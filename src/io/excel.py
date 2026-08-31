"""Leitura genérica das planilhas Excel da fonte Bronze. Camada exclusiva
de I/O — sem limpeza nem regra de negócio.
"""

import pandas as pd

from src.config.settings import (
    RAW_ASSOCIADOS_PATH,
    SHEET_ASSOCIADOS,
    SHEET_PRODUTOS,
    SHEET_MOVIMENTACAO,
)

SOURCE_SHEETS = (SHEET_ASSOCIADOS, SHEET_PRODUTOS, SHEET_MOVIMENTACAO)


def read_sheet(file_path, sheet_name):
    """Lê uma única aba de uma planilha Excel para um `DataFrame`.

    Args:
        file_path: Caminho do arquivo `.xlsx`.
        sheet_name: Nome da aba a ler.

    Returns:
        `DataFrame` com o conteúdo bruto da aba, sem qualquer transformação.
    """
    return pd.read_excel(file_path, sheet_name=sheet_name)


def load_sources(file_path=RAW_ASSOCIADOS_PATH, sheets=SOURCE_SHEETS):
    """Lê múltiplas abas de uma planilha Excel de uma só vez.

    Args:
        file_path: Caminho do arquivo `.xlsx`. Por padrão, a fonte Bronze
            do projeto (`RAW_ASSOCIADOS_PATH`).
        sheets: Nomes das abas a ler. Por padrão, as três entidades do
            desafio (`SOURCE_SHEETS`).

    Returns:
        Dicionário `{nome_da_aba: DataFrame}`, uma entrada por aba lida.
    """
    return {sheet_name: read_sheet(file_path, sheet_name) for sheet_name in sheets}
