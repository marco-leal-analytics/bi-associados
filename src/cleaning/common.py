def standardize_text(series):
    return (
        series.astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )


def normalize_categories(series, mapping):
    return standardize_text(series).replace(mapping)


def validate_unique_key(df, key_column):
    return not df[key_column].duplicated().any()
