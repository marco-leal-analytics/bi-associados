"""Dimensão de calendário (Dim_Calendario): projeta a fonte externa bruta
(`data/0_bronze/raw_Dim_Calendario.xlsx`) nas colunas e no intervalo de anos
efetivamente necessários ao projeto. Diferente das dimensões de
`src/features/dimensoes.py` (construídas a partir de pares fixos em
`src/config/settings.py`), esta vem de uma fonte externa pré-calculada — só
há leitura, filtro de linhas/colunas e validação de cobertura, sem cálculo
de negócio.
"""

from src.config.settings import (
    CALENDARIO_ANOS_BUFFER,
    DIM_CALENDARIO_COLUNAS,
    RAW_DIM_CALENDARIO_PATH,
    SHEET_DIM_CALENDARIO,
)
from src.io.excel import read_sheet


def build_dim_calendario(
    associados,
    reference_date,
    file_path=RAW_DIM_CALENDARIO_PATH,
    buffer_anos=CALENDARIO_ANOS_BUFFER,
):
    """Monta a Dim_Calendario reduzida a partir da fonte externa bruta.

    Args:
        associados: `DataFrame` (Silver) contendo `DATA_ASSOCIACAO`, usado
            para delimitar o intervalo de anos necessário — a coluna que se
            relaciona com esta dimensão na fato (`DASHBOARD_COLUMNS`,
            `src/config/settings.py`).
        reference_date: `DATA_REFERENCIA` da rodada (mesma usada em
            `run_silver`/`run_gold`) — garante que o calendário cubra pelo
            menos o "hoje" do pipeline, mesmo que nenhum `DATA_ASSOCIACAO`
            alcance essa data.
        file_path: Caminho do Excel bruto do calendário. Por padrão,
            `RAW_DIM_CALENDARIO_PATH`.
        buffer_anos: Anos de folga somados antes/depois do intervalo
            observado, para tolerar pequenas variações da fonte sem precisar
            regenerar o arquivo. Por padrão, `CALENDARIO_ANOS_BUFFER`.

    Returns:
        `DataFrame` com as colunas de `DIM_CALENDARIO_COLUNAS`, uma linha
        por dia, ordenado por `DATA`, cobrindo de 1º de janeiro do (ano
        mínimo − `buffer_anos`) a 31 de dezembro do (ano máximo +
        `buffer_anos`).

    Raises:
        ValueError: se a Dim_Calendario bruta não cobrir integralmente o
            intervalo de anos necessário (nenhuma linha para algum ano
            requerido) — a fonte bruta precisaria ser atualizada.
    """
    calendario = read_sheet(file_path, SHEET_DIM_CALENDARIO)

    ano_min = min(associados["DATA_ASSOCIACAO"].dt.year.min(), reference_date.year) - buffer_anos
    ano_max = max(associados["DATA_ASSOCIACAO"].dt.year.max(), reference_date.year) + buffer_anos

    anos_disponiveis = set(calendario["ANO"].unique())
    anos_faltantes = set(range(ano_min, ano_max + 1)) - anos_disponiveis
    if anos_faltantes:
        raise ValueError(
            f"Dim_Calendario bruta não cobre os anos {sorted(anos_faltantes)}, "
            f"necessários para o intervalo de DATA_ASSOCIACAO/DATA_REFERENCIA da rodada."
        )

    calendario = calendario.loc[calendario["ANO"].between(ano_min, ano_max), list(DIM_CALENDARIO_COLUNAS)]
    return calendario.sort_values("DATA").reset_index(drop=True)
