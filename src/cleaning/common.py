"""Funções genéricas de limpeza e validação, reutilizadas pelos módulos de
`src/cleaning` (associados, produtos, movimentacao). Não conhecem o schema de
nenhuma entidade específica — recebem `Series`/`DataFrame` e parâmetros.
"""

import unicodedata

import pandas as pd


def strip_accents(text):
    """Remove acentuação de uma string, preservando os demais caracteres.

    Args:
        text: Valor a normalizar. Valores que não são `str` (ex.: `NaN`)
            são retornados sem alteração.

    Returns:
        A string sem acentos, ou o valor original se não for `str`.
    """
    if not isinstance(text, str):
        return text
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def standardize_text(series, case="title"):
    """Padroniza uma coluna de texto: remove espaços nas pontas, colapsa
    espaços internos repetidos e aplica a capitalização informada.

    Args:
        series: Coluna de texto (`pandas.Series`) a padronizar.
        case: Capitalização a aplicar — `"title"` (padrão), `"upper"` ou
            `"lower"`. Qualquer outro valor mantém a capitalização original.

    Returns:
        Nova `Series` (dtype `string`) com o texto padronizado.
    """
    cleaned = series.astype("string").str.strip()
    cleaned = cleaned.str.replace(r"\s+", " ", regex=True)
    if case == "title":
        cleaned = cleaned.str.title()
    elif case == "upper":
        cleaned = cleaned.str.upper()
    elif case == "lower":
        cleaned = cleaned.str.lower()
    return cleaned


def normalize_categories(series, mapping):
    """Substitui valores de categoria por seus equivalentes canônicos.

    Args:
        series: Coluna categórica a normalizar.
        mapping: Dicionário `{valor_observado: valor_canônico}` com as
            variantes a corrigir (valores fora do mapa são mantidos).

    Returns:
        Nova `Series` com os valores mapeados substituídos.
    """
    return series.replace(mapping)


def validate_domain(series, allowed_values):
    """Verifica se todos os valores de uma coluna pertencem a um domínio.

    Args:
        series: Coluna a validar.
        allowed_values: Conjunto de valores permitidos.

    Returns:
        Lista dos valores distintos encontrados fora do domínio (vazia se
        todos os valores forem válidos).
    """
    invalid = series[~series.isin(allowed_values)]
    return invalid.unique().tolist()


def null_report(df, columns=None):
    """Monta um relatório de nulos (contagem e percentual) por coluna.

    Args:
        df: `DataFrame` a inspecionar.
        columns: Colunas a considerar. Se `None`, usa todas as colunas
            do `df`.

    Returns:
        `DataFrame` indexado pelas colunas analisadas, com as colunas
        `nulos` (contagem absoluta) e `percentual` (0–100, 2 casas).
    """
    columns = list(columns) if columns is not None else list(df.columns)
    counts = df[columns].isna().sum()
    percentages = (counts / len(df) * 100).round(2)
    return pd.DataFrame({"nulos": counts, "percentual": percentages})


def flag_nulls(df, column, flag_column=None):
    """Adiciona uma coluna booleana sinalizando os registros nulos de `column`.

    Args:
        df: `DataFrame` de origem.
        column: Coluna cujos nulos serão sinalizados.
        flag_column: Nome da coluna de sinalização a criar. Se `None`,
            usa `"{column}_NULO"`.

    Returns:
        Novo `DataFrame` (via `DataFrame.assign`) com a coluna de flag
        adicionada; `column` permanece inalterada.
    """
    flag_column = flag_column or f"{column}_NULO"
    return df.assign(**{flag_column: df[column].isna()})


def flag_future_dates(series, reference_date=None, invalid_value=pd.NaT):
    """Sinaliza e trata datas posteriores a uma data de referência.

    Não remove nem "corrige" o dado: substitui apenas o valor retornado
    em `treated` pelos registros futuros (por padrão, `NaT`), preservando
    a coluna original intacta em `df` — quem chama decide se/onde grava
    o resultado tratado.

    Args:
        series: Coluna de datas (`datetime64`) a avaliar.
        reference_date: Data de referência para o corte. Se `None`, usa
            `pandas.Timestamp.now()` normalizado (meia-noite do dia atual).
        invalid_value: Valor a atribuir às datas futuras em `treated`.

    Returns:
        Tupla `(treated, is_future)`: `treated` é a série com as datas
        futuras substituídas por `invalid_value`; `is_future` é a máscara
        booleana correspondente.
    """
    reference_date = reference_date or pd.Timestamp.now().normalize()
    is_future = series > reference_date
    treated = series.where(~is_future, invalid_value)
    return treated, is_future


def flag_out_of_range(series, min_value=None, max_value=None, invalid_value=None):
    """Sinaliza e trata valores numéricos fora de um intervalo permitido.

    Args:
        series: Coluna numérica a avaliar.
        min_value: Limite inferior (inclusive). Se `None`, não é checado.
        max_value: Limite superior (inclusive). Se `None`, não é checado.
        invalid_value: Valor a atribuir aos registros fora do intervalo em
            `treated`. Se `None`, usa `NaN`.

    Returns:
        Tupla `(treated, is_invalid)`: `treated` é a série com os valores
        fora do intervalo substituídos por `invalid_value`; `is_invalid`
        é a máscara booleana correspondente.
    """
    invalid_value = float("nan") if invalid_value is None else invalid_value
    is_invalid = pd.Series(False, index=series.index)
    if min_value is not None:
        is_invalid |= series < min_value
    if max_value is not None:
        is_invalid |= series > max_value
    treated = series.where(~is_invalid, invalid_value)
    return treated, is_invalid


def count_duplicates(df, subset=None):
    """Conta linhas duplicadas em um `DataFrame`.

    Args:
        df: `DataFrame` a inspecionar.
        subset: Colunas a considerar na comparação. Se `None`, compara
            todas as colunas (duplicidade de linha completa).

    Returns:
        Número de linhas duplicadas (mantendo a primeira ocorrência).
    """
    return int(df.duplicated(subset=subset).sum())


def handle_duplicate_keys(df, key_column):
    """Remove duplicidade de linha completa e valida a unicidade da chave.

    Linhas 100% idênticas são removidas silenciosamente (duplicidade de
    carga). Se, após essa remoção, ainda houver mais de uma linha com o
    mesmo `key_column` mas dados divergentes, a granularidade é
    inesperada e não pode ser resolvida automaticamente — o erro é
    levantado para decisão manual.

    Args:
        df: `DataFrame` a validar.
        key_column: Nome da coluna que deve ser chave única.

    Returns:
        Tupla `(df, full_row_duplicates)`: `df` sem as linhas duplicadas;
        `full_row_duplicates` é o número de linhas removidas.

    Raises:
        ValueError: Se restar mais de uma linha com o mesmo `key_column`
            e conteúdo divergente entre elas.
    """
    full_row_duplicates = int(df.duplicated().sum())
    df = df.drop_duplicates()

    key_duplicates = df[df.duplicated(subset=[key_column], keep=False)]
    if not key_duplicates.empty:
        raise ValueError(
            f"Duplicidade de {key_column} com dados divergentes (granularidade "
            f"inesperada, não pode ser resolvida automaticamente): "
            f"{sorted(key_duplicates[key_column].unique().tolist())}"
        )

    return df, full_row_duplicates


def assert_allowed_nulls(df, allowed_columns):
    """Garante que só as colunas esperadas contenham valores nulos.

    Args:
        df: `DataFrame` a validar.
        allowed_columns: Colunas em que nulos são aceitáveis (decisão de
            negócio já tomada, ex.: `RENDA_MENSAL`).

    Raises:
        ValueError: Se houver nulos em qualquer coluna fora de
            `allowed_columns`.
    """
    allowed_columns = set(allowed_columns)
    columns_with_nulls = set(df.columns[df.isna().any()])
    unexpected = columns_with_nulls - allowed_columns
    if unexpected:
        raise ValueError(f"Nulos não previstos nas colunas: {sorted(unexpected)}")


def assert_exact_categories(series, expected_categories):
    """Garante que uma coluna categórica contenha exatamente o domínio esperado.

    Args:
        series: Coluna categórica a validar (nulos são ignorados).
        expected_categories: Conjunto de categorias esperado, nem mais
            nem menos.

    Raises:
        ValueError: Se as categorias observadas divergirem das esperadas
            (categoria a mais, a menos, ou variante não padronizada).
    """
    observed = set(series.dropna().unique())
    expected = set(expected_categories)
    if observed != expected:
        raise ValueError(
            f"Categorias divergentes do esperado. Observadas: {sorted(observed)}; "
            f"esperadas: {sorted(expected)}"
        )


def cast_types(df, dtype_map):
    """Converte os tipos das colunas de um `DataFrame`.

    Args:
        df: `DataFrame` de origem.
        dtype_map: Dicionário `{coluna: dtype}` com as conversões a aplicar.

    Returns:
        Novo `DataFrame` com os tipos convertidos.
    """
    return df.astype(dtype_map)


def convert_sn_to_bool(series):
    """Converte uma coluna de domínio "S"/"N" para booleano.

    Args:
        series: Coluna com valores `"S"`/`"N"`. Valores fora do domínio
            viram `NaN` — validar com `validate_domain` antes de chamar.

    Returns:
        Nova `Series` booleana (`"S"` → `True`, `"N"` → `False`).
    """
    return series.map({"S": True, "N": False})
