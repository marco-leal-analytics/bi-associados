"""Consolidação da camada Gold: junção de Associados, Produtos e
Movimentacao pela CHAVE e aplicação de todos os indicadores/classificação.
Orquestrado por `run_gold` em `src/pipeline.py`.
"""

from src.config.settings import DASHBOARD_COLUMNS, KEY_COLUMN
from src.features.associados import add_faixa_renda, add_indicadores_relacionamento
from src.features.classificacao import add_classificacao
from src.features.movimentacao import add_nivel_movimentacao
from src.features.oportunidades import add_flags_oportunidade
from src.features.produtos import add_indicadores_produtos


def build_features(associados, produtos, movimentacao, reference_date=None):
    """Monta o dataset analítico consolidado (Gold) a partir das três entidades Silver.

    Ordem das etapas: (1) indicadores por entidade — tempo de
    relacionamento e faixa de renda em Associados, índice/nível de
    diversificação em Produtos; (2) junção das três bases pela `CHAVE`,
    com `validate="one_to_one"` para impor a cardinalidade 1:1:1
    documentada em `docs/dicionario_dados.md` (qualquer duplicidade
    interrompe o pipeline em vez de inflar a base silenciosamente); (3)
    nível de movimentação (depende das três métricas já consolidadas);
    (4) classificação por índice composto (depende dos indicadores de
    produtos/tempo/saldo/utilização já presentes); (5) flags de
    oportunidade (dependem de `NIVEL_MOVIMENTACAO` e `CLASSIFICACAO` já
    calculados).

    Args:
        associados: `DataFrame` Silver de Associados.
        produtos: `DataFrame` Silver de Produtos.
        movimentacao: `DataFrame` Silver de Movimentacao.
        reference_date: `DATA_REFERENCIA` a propagar para
            `add_indicadores_relacionamento`. Se `None`, cada chamada usa
            `pandas.Timestamp.now()` independentemente — prefira sempre
            passar a mesma data usada na Silver (ver `run_pipeline` em
            `src/pipeline.py`) para uma rodada consistente/reprodutível.

    Returns:
        `DataFrame` Gold com uma linha por `CHAVE`, contendo os campos
        originais das três entidades mais todos os indicadores derivados
        e `CLASSIFICACAO_ID`/`FLAG_OPORTUNIDADE_*`. As faixas/classes
        derivadas ficam como ID inteiro (`FAIXA_RENDA_ID`,
        `NIVEL_DIVERSIFICACAO_ID`, `NIVEL_MOVIMENTACAO_ID`,
        `CLASSIFICACAO_ID`) — o rótulo de cada uma vive nas tabelas de
        dimensão (`src/features/dimensoes.py`, `build_dimensions`),
        persistidas separadamente por `run_gold` (`src/pipeline.py`).

    Raises:
        pandas.errors.MergeError: Se a cardinalidade 1:1:1 pela `CHAVE`
            for violada em algum dos dois merges.
    """
    associados = add_faixa_renda(add_indicadores_relacionamento(associados, reference_date))
    produtos = add_indicadores_produtos(produtos)

    df = associados.merge(produtos, on=KEY_COLUMN, how="inner", validate="one_to_one")
    df = df.merge(movimentacao, on=KEY_COLUMN, how="inner", validate="one_to_one")
    df = add_nivel_movimentacao(df)
    df = add_classificacao(df)
    df = add_flags_oportunidade(df)

    return df


def build_dashboard_features(features):
    """Projeta a Gold completa nas colunas efetivamente usadas pelo dashboard Power BI.

    A fato completa (`features`, retorno de `build_features`) carrega campos
    intermediários do cálculo — pilares de score, níveis individuais de
    movimentação, colunas de produto por tipo — que nenhuma das 4 páginas do
    dashboard usa diretamente (ver `docs/regras_negocio.md`, seção 7).
    Importar essas colunas no Power BI não erra o resultado, mas infla o
    modelo sem necessidade. `DASHBOARD_COLUMNS` (`src/config/settings.py`)
    é a lista de colunas de fato necessárias; some-se a ela as quatro
    tabelas de dimensão (`build_dimensions`) para o modelo em estrela.

    Args:
        features: `DataFrame` Gold completo (saída de `build_features`).

    Returns:
        Cópia de `features` restrita às colunas de `DASHBOARD_COLUMNS`,
        na mesma ordem.
    """
    return features[list(DASHBOARD_COLUMNS)].copy()
