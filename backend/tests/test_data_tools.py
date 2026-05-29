import pytest

from app.data_tools import run_data_tools
from app.data_tools.modules import analyze_null_values, analyze_outliers, analyze_table


def test_analyze_null_values_reports_columns_with_nulls():
    result = analyze_null_values(
        [
            {"id": 1, "name": "A", "price": 10},
            {"id": 2, "name": None, "price": None},
            {"id": 3, "name": "C", "price": None},
        ]
    )

    assert result["total_rows"] == 3
    assert result["columns_with_nulls"] == 2
    assert result["results"][0]["column"] == "price"
    assert result["results"][0]["null_count"] == 2


def test_analyze_outliers_detects_iqr_outlier():
    result = analyze_outliers(
        [
            {"id": 1, "amount": 10},
            {"id": 2, "amount": 11},
            {"id": 3, "amount": 12},
            {"id": 4, "amount": 13},
            {"id": 5, "amount": 100},
        ]
    )

    assert result["numeric_columns"] == 2
    amount_result = next(item for item in result["results"] if item["column"] == "amount")
    assert amount_result["outlier_count"] == 1
    assert amount_result["examples"] == [100]


def test_analyze_outliers_handles_no_numeric_columns():
    result = analyze_outliers([{"name": "A"}, {"name": "B"}])

    assert result["error"] == "No numeric columns found."
    assert result["results"] == []


def test_analyze_table_profiles_rows():
    result = analyze_table(
        [
            {"name": "A", "category": "x", "amount": 10},
            {"name": "B", "category": "x", "amount": None},
            {"name": "C", "category": "y", "amount": 20},
        ]
    )

    assert result["total_rows"] == 3
    assert result["total_columns"] == 3
    assert result["columns_with_nulls"] == 1
    amount_profile = next(item for item in result["columns"] if item["column"] == "amount")
    assert amount_profile["numeric_summary"]["min"] == 10
    category_profile = next(item for item in result["columns"] if item["column"] == "category")
    assert category_profile["top_values"][0] == {"value": "x", "count": 2}


@pytest.mark.asyncio
async def test_run_data_tools_dispatches_known_and_unknown_tools():
    data = [{"id": 1, "value": None}]

    null_result = await run_data_tools("null_values", data)
    unknown_result = await run_data_tools("unknown", data)

    assert null_result["columns_with_nulls"] == 1
    assert unknown_result["error"] == "Unknown data tool: unknown"
