import unicodedata

import pandas as pd


def strip_accents(text):
    if not isinstance(text, str):
        return text
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def standardize_text(series, case="title"):
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
    return series.replace(mapping)


def validate_domain(series, allowed_values):
    invalid = series[~series.isin(allowed_values)]
    return invalid.unique().tolist()


def null_report(df, columns=None):
    columns = list(columns) if columns is not None else list(df.columns)
    counts = df[columns].isna().sum()
    percentages = (counts / len(df) * 100).round(2)
    return pd.DataFrame({"nulos": counts, "percentual": percentages})


def flag_nulls(df, column, flag_column=None):
    flag_column = flag_column or f"{column}_NULO"
    return df.assign(**{flag_column: df[column].isna()})


def flag_future_dates(series, reference_date=None, invalid_value=pd.NaT):
    reference_date = reference_date or pd.Timestamp.now().normalize()
    is_future = series > reference_date
    treated = series.where(~is_future, invalid_value)
    return treated, is_future


def count_duplicates(df, subset=None):
    return int(df.duplicated(subset=subset).sum())


def cast_types(df, dtype_map):
    return df.astype(dtype_map)


def convert_sn_to_bool(series):
    return series.map({"S": True, "N": False})
