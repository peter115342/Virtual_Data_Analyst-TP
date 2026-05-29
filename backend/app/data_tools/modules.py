# TODO: Implement data analysis modules (not LLM-based)

import polars as pl


def analyze_null_values(data: list[dict]) -> dict:
    """
    Nájde null hodnoty v dátach.
    Vráti prehľad nullov pre každý stĺpec.
    """

    if not data:
        return {"error": "No data provided", "results": []}

    df = pl.DataFrame(data)
    total_rows = len(df)

    results = []
    for col in df.columns:
        null_count = df[col].null_count()
        null_percentage = round((null_count / total_rows) * 100, 2) if total_rows > 0 else 0.0

        if null_count > 0:
            results.append({
                "column": col,
                "null_count": null_count,
                "total_rows": total_rows,
                "null_percentage": null_percentage,
            })

        results.sort(key=lambda x: x["null_count"], reverse=True)

    return {
        "total_rows": total_rows,
        "total_columns": len(df.columns),
        "columns_with_nulls": len(results),
        "results": results,
        "summary": (
            f"Found null values in {len(results)} out of {len(df.columns)} columns."
            if results
            else f"No null values found."
        )
    }


def analyze_outliers(data: list[dict]) -> dict:
    """
    Nájde outliers v numerických stĺpcoch.

    method:
        "iqr"    — IQR metóda (Q1 - 1.5*IQR, Q3 + 1.5*IQR) — default, robustná
    """

    if not data:
        return {"error": "No data provided", "results": []}

    df = pl.DataFrame(data)

    numeric_columns = [
        col for col in df.columns
        if df[col].dtype in [
            pl.Int8, pl.Int16, pl.Int32, pl.Int64,
            pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
            pl.Float32, pl.Float64
        ]
    ]

    if not numeric_columns:
        return {
            "error" : "No numeric columns found.",
            "results": [],
            "summary": "No numeric columns to analyze for outliers.",
        }

    total_rows = len(df)
    results = []

    for col in numeric_columns:

        series = df[col].drop_nulls()
        if len(series) < 4:
            continue

        # IQR method
        pass

    return {

    }
