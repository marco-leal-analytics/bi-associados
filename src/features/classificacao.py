"""Classificação dos associados por índice composto de percentil.
Ver `docs/regras_negocio.md` (seção 5) para a metodologia e a justificativa
da escolha em relação às regras sequenciais avaliadas originalmente.
"""

import pandas as pd

from src.config.settings import CLASSIFICACAO_LABELS, CLASSIFICACAO_PESOS

SCORE_NEUTRO_TEMPO_INDISPONIVEL = 0.5


def add_classificacao(df):
    """Calcula o índice composto de classificação e o corta em quartis.

    Cada associado recebe um percentil (`rank(pct=True)`, 0 a 1) em cada
    um dos quatro pilares — Produtos, Relacionamento, Saldo e Utilização
    (média dos percentis de PIX e compras no cartão) —, combinados em
    `INDICE_CLASSIFICACAO` pela soma ponderada de `CLASSIFICACAO_PESOS`.
    `CLASSIFICACAO` é o corte desse índice em quartis, rotulado por
    `CLASSIFICACAO_LABELS` em ordem crescente.

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
        `SCORE_SALDO`, `SCORE_UTILIZACAO`, `INDICE_CLASSIFICACAO`,
        `CLASSIFICACAO_TEMPO_INDISPONIVEL` e `CLASSIFICACAO` adicionadas.
    """
    df = df.copy()

    score_produtos = df["INDICE_DIVERSIFICACAO"].rank(pct=True)
    score_relacionamento = df["TEMPO_RELACIONAMENTO_ANOS"].rank(pct=True)
    score_saldo = df["SALDO_MEDIO"].rank(pct=True)
    score_utilizacao = (df["PIX_MENSAL"].rank(pct=True) + df["COMPRAS_CARTAO"].rank(pct=True)) / 2

    df["CLASSIFICACAO_TEMPO_INDISPONIVEL"] = score_relacionamento.isna()
    score_relacionamento = score_relacionamento.fillna(SCORE_NEUTRO_TEMPO_INDISPONIVEL)

    df["SCORE_PRODUTOS"] = score_produtos.round(4)
    df["SCORE_RELACIONAMENTO"] = score_relacionamento.round(4)
    df["SCORE_SALDO"] = score_saldo.round(4)
    df["SCORE_UTILIZACAO"] = score_utilizacao.round(4)

    df["INDICE_CLASSIFICACAO"] = (
        score_produtos * CLASSIFICACAO_PESOS["produtos"]
        + score_relacionamento * CLASSIFICACAO_PESOS["relacionamento"]
        + score_saldo * CLASSIFICACAO_PESOS["saldo"]
        + score_utilizacao * CLASSIFICACAO_PESOS["utilizacao"]
    ).round(4)

    df["CLASSIFICACAO"] = pd.Categorical(
        pd.qcut(df["INDICE_CLASSIFICACAO"], 4, labels=CLASSIFICACAO_LABELS),
        categories=CLASSIFICACAO_LABELS,
        ordered=True,
    )

    return df
