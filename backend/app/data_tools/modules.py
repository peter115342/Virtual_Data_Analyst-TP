from datetime import date, datetime
from decimal import Decimal
from math import isnan
from typing import Any

import polars as pl

NUMERIC_DTYPES = {
    pl.Int8,
    pl.Int16,
    pl.Int32,
    pl.Int64,
    pl.UInt8,
    pl.UInt16,
    pl.UInt32,
    pl.UInt64,
    pl.Float32,
    pl.Float64,
}


def analyze_null_values(data: list[dict]) -> dict:
    if not data:
        return {
            "error": "No data provided",
            "total_rows": 0,
            "total_columns": 0,
            "columns_with_nulls": 0,
            "results": [],
            "summary": "No data provided.",
        }

    df = pl.DataFrame(data)
    total_rows = len(df)

    results = []
    for col in df.columns:
        null_count = int(df[col].null_count())
        null_percentage = round((null_count / total_rows) * 100, 2) if total_rows else 0.0

        if null_count > 0:
            results.append(
                {
                    "column": col,
                    "null_count": null_count,
                    "total_rows": total_rows,
                    "null_percentage": null_percentage,
                }
            )

    results.sort(key=lambda x: x["null_count"], reverse=True)

    return {
        "total_rows": total_rows,
        "total_columns": len(df.columns),
        "columns_with_nulls": len(results),
        "results": results,
        "summary": (
            f"Found null values in {len(results)} out of {len(df.columns)} columns."
            if results
            else "No null values found."
        ),
    }


def analyze_outliers(data: list[dict]) -> dict:
    if not data:
        return {
            "error": "No data provided",
            "total_rows": 0,
            "numeric_columns": 0,
            "columns_with_outliers": 0,
            "results": [],
            "summary": "No data provided.",
        }

    df = pl.DataFrame(data)
    numeric_columns = [col for col in df.columns if _is_numeric(df[col])]

    if not numeric_columns:
        return {
            "error": "No numeric columns found.",
            "total_rows": len(df),
            "numeric_columns": 0,
            "columns_with_outliers": 0,
            "results": [],
            "summary": "No numeric columns to analyze for outliers.",
        }

    total_rows = len(df)
    results = []

    for col in numeric_columns:
        series = df[col].drop_nulls()
        if len(series) < 4:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        if q1 is None or q3 is None:
            continue

        iqr = q3 - q1
        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)
        outlier_series = series.filter((series < lower_bound) | (series > upper_bound))
        outlier_count = len(outlier_series)

        if outlier_count == 0:
            continue

        results.append(
            {
                "column": col,
                "method": "iqr",
                "non_null_count": len(series),
                "outlier_count": outlier_count,
                "outlier_percentage": round((outlier_count / total_rows) * 100, 2),
                "lower_bound": _json_value(lower_bound),
                "upper_bound": _json_value(upper_bound),
                "q1": _json_value(q1),
                "q3": _json_value(q3),
                "examples": [_json_value(value) for value in outlier_series.head(5).to_list()],
            }
        )

    results.sort(key=lambda x: x["outlier_count"], reverse=True)

    return {
        "total_rows": total_rows,
        "numeric_columns": len(numeric_columns),
        "columns_with_outliers": len(results),
        "results": results,
        "summary": (
            f"Found outliers in {len(results)} out of {len(numeric_columns)} numeric columns."
            if results
            else "No outliers found in numeric columns."
        ),
    }


def analyze_table(data: list[dict]) -> dict:
    if not data:
        return {
            "error": "No data provided",
            "total_rows": 0,
            "total_columns": 0,
            "columns": [],
            "summary": "No data provided.",
        }

    df = pl.DataFrame(data)
    total_rows = len(df)
    columns: list[dict[str, Any]] = []

    for col in df.columns:
        series = df[col]
        null_count = int(series.null_count())
        profile: dict[str, Any] = {
            "column": col,
            "dtype": str(series.dtype),
            "null_count": null_count,
            "null_percentage": round((null_count / total_rows) * 100, 2) if total_rows else 0.0,
            "non_null_count": total_rows - null_count,
        }

        non_null_series = series.drop_nulls()
        if _is_numeric(series) and len(non_null_series) > 0:
            profile["numeric_summary"] = {
                "min": _json_value(non_null_series.min()),
                "max": _json_value(non_null_series.max()),
                "mean": _json_value(non_null_series.mean()),
                "median": _json_value(non_null_series.median()),
                "std": _json_value(non_null_series.std()),
            }
        elif len(non_null_series) > 0:
            profile["top_values"] = _top_values(non_null_series)

        columns.append(profile)

    null_columns = sum(1 for column in columns if column["null_count"] > 0)
    numeric_columns = sum(1 for column in columns if "numeric_summary" in column)

    return {
        "total_rows": total_rows,
        "total_columns": len(df.columns),
        "columns_with_nulls": null_columns,
        "numeric_columns": numeric_columns,
        "columns": columns,
        "summary": (
            f"Profiled {total_rows} rows and {len(df.columns)} columns. "
            f"{null_columns} columns contain null values."
        ),
    }


def _is_numeric(series: pl.Series) -> bool:
    return series.dtype in NUMERIC_DTYPES


def _top_values(series: pl.Series) -> list[dict[str, Any]]:
    value_counts = series.value_counts(sort=True).head(5).to_dicts()
    value_column = series.name

    return [
        {
            "value": _json_value(row.get(value_column)),
            "count": int(row.get("count", 0)),
        }
        for row in value_counts
    ]


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, float) and isnan(value):
        return None
    return value
