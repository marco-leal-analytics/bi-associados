"""Classificação (ID) dos associados por índice composto de percentil.
IDs seguem a dimensão `DIM_CLASSIFICACAO` (`src/config/settings.py`).
Ver `docs/regras_negocio.md` (seção 5) para a metodologia e a justificativa
da escolha em relação às regras sequenciais avaliadas originalmente.
"""

import pandas as pd

from src.config.settings import CLASSIFICACAO_IDS, CLASSIFICACAO_PESOS

SCORE_NEUTRO_TEMPO_INDISPONIVEL = 0.5


def add_classificacao(df):
    """Calcula o índice composto de classificação e o corta em quartis (ID).

    Cada associado recebe um percentil (`rank(pct=True)`, 0 a 1) em cada
    um dos cinco pilares — Produtos, Relacionamento, Saldo, Pix Mensal e
    Compras no Cartão —, combinados em `INDICE_CLASSIFICACAO` pela soma
    ponderada de `CLASSIFICACAO_PESOS`. Pix Mensal e Compras no Cartão são
    pilares separados (e não mais um único "Utilização" médio entre os
    dois) porque medem bases diferentes: quantidade de transações PIX
    contra volume financeiro movimentado no cartão. `CLASSIFICACAO_ID` é
    o corte desse índice em quartis, com os IDs de `CLASSIFICACAO_IDS` em
    ordem crescente (o rótulo de cada ID vive em `DIM_CLASSIFICACAO`, não
    nesta coluna).

    Associados com `TEMPO_RELACIONAMENTO_ANOS` nulo (data de associação
    futura, ver `src/features/associados.py`) recebem
    `SCORE_RELACIONAMENTO = SCORE_NEUTRO_TEMPO_INDISPONIVEL` (mediana
    neutra) em vez de serem excluídos do índice, com a ocorrência
    sinalizada em `CLASSIFICACAO_TEMPO_INDISPONIVEL` para transparência.

    Args:
        df: `DataFrame` (Gold, pré-classificação) contendo
            `INDICE_DIVERSIFICACAO`, `TEMPO_RELACIONAMENTO_ANOS`,
            `SALDO_MEDIO`, `PIX_MENSAL` e `COMPRAS_CARTAO`.

    Returns:
        Cópia de `df` com `SCORE_PRODUTOS`, `SCORE_RELACIONAMENTO`,
        `SCORE_SALDO`, `SCORE_PIX_MENSAL`, `SCORE_COMPRAS_CARTAO`,
        `INDICE_CLASSIFICACAO`, `CLASSIFICACAO_TEMPO_INDISPONIVEL` e
        `CLASSIFICACAO_ID` adicionadas.
    """
    df = df.copy()

    score_produtos = df["INDICE_DIVERSIFICACAO"].rank(pct=True)
    score_relacionamento = df["TEMPO_RELACIONAMENTO_ANOS"].rank(pct=True)
    score_saldo = df["SALDO_MEDIO"].rank(pct=True)
    score_pix_mensal = df["PIX_MENSAL"].rank(pct=True)
    score_compras_cartao = df["COMPRAS_CARTAO"].rank(pct=True)

    df["CLASSIFICACAO_TEMPO_INDISPONIVEL"] = score_relacionamento.isna()
    score_relacionamento = score_relacionamento.fillna(SCORE_NEUTRO_TEMPO_INDISPONIVEL)

    df["SCORE_PRODUTOS"] = score_produtos.round(4)
    df["SCORE_RELACIONAMENTO"] = score_relacionamento.round(4)
    df["SCORE_SALDO"] = score_saldo.round(4)
    df["SCORE_PIX_MENSAL"] = score_pix_mensal.round(4)
    df["SCORE_COMPRAS_CARTAO"] = score_compras_cartao.round(4)

    df["INDICE_CLASSIFICACAO"] = (
        score_produtos * CLASSIFICACAO_PESOS["produtos"]
        + score_relacionamento * CLASSIFICACAO_PESOS["relacionamento"]
        + score_saldo * CLASSIFICACAO_PESOS["saldo"]
        + score_pix_mensal * CLASSIFICACAO_PESOS["pix_mensal"]
        + score_compras_cartao * CLASSIFICACAO_PESOS["compras_cartao"]
    ).round(4)

    df["CLASSIFICACAO_ID"] = pd.qcut(
        df["INDICE_CLASSIFICACAO"], len(CLASSIFICACAO_IDS), labels=CLASSIFICACAO_IDS
    ).astype("int64")

    return df
