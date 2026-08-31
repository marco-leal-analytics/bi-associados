"""Flags de oportunidade: cruzamentos de indicadores já calculados na Gold,
parametrizados em `src/config/settings.py`. Ver `docs/regras_negocio.md`
(seção 6). As três flags não são mutuamente exclusivas.
"""

from src.config.settings import (
    OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS,
    OPORTUNIDADE_BAIXA_UTILIZACAO,
    OPORTUNIDADE_POTENCIAL_CRESCIMENTO,
)


def add_flags_oportunidade(df):
    """Adiciona as três flags booleanas de oportunidade à base Gold.

    - `FLAG_OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS`: associado na maior
      faixa de renda (`OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS`) mas com
      poucos produtos contratados.
    - `FLAG_OPORTUNIDADE_BAIXA_UTILIZACAO`: já é cliente de mais de um
      produto, mas com nível de movimentação baixo — diferente de um
      associado "Inicial", que ainda não se engajou.
    - `FLAG_OPORTUNIDADE_POTENCIAL_CRESCIMENTO`: classificação "Em
      Desenvolvimento" com nível de movimentação Média/Alta — poucos
      produtos, mas já engajado financeiramente.

    Args:
        df: `DataFrame` (Gold) já contendo `FAIXA_RENDA`, `QTD_PRODUTOS`,
            `NIVEL_MOVIMENTACAO` e `CLASSIFICACAO` (produzidos por
            `add_faixa_renda`, `clean_produtos`, `add_nivel_movimentacao`
            e `add_classificacao`, respectivamente).

    Returns:
        Cópia de `df` com as três colunas `FLAG_OPORTUNIDADE_*`
        (booleanas) adicionadas.
    """
    df = df.copy()

    cfg = OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS
    df["FLAG_OPORTUNIDADE_ALTA_RENDA_POUCOS_PRODUTOS"] = (
        (df["FAIXA_RENDA"] == cfg["faixa_renda"]) & (df["QTD_PRODUTOS"] <= cfg["qtd_produtos_max"])
    )

    cfg = OPORTUNIDADE_BAIXA_UTILIZACAO
    df["FLAG_OPORTUNIDADE_BAIXA_UTILIZACAO"] = (
        (df["NIVEL_MOVIMENTACAO"] == cfg["nivel_movimentacao"]) & (df["QTD_PRODUTOS"] >= cfg["qtd_produtos_min"])
    )

    cfg = OPORTUNIDADE_POTENCIAL_CRESCIMENTO
    df["FLAG_OPORTUNIDADE_POTENCIAL_CRESCIMENTO"] = (
        (df["CLASSIFICACAO"] == cfg["classificacao"])
        & (df["NIVEL_MOVIMENTACAO"].isin(cfg["nivel_movimentacao"]))
    )

    return df
