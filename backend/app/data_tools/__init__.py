from app.data_tools import modules


async def run_data_tools(tool: str, data: list[dict]) -> dict:
    """
    Dispatcher — vyberie správny data tool podľa názvu.

    tool:
        "null_values" — analýza chýbajúcich hodnôt
        "outliers"    — detekcia outlierov (kwargs: method="iqr"|"zscore")
        "select_star" — kompletný profiling tabuľky
    """

    if tool == "null_values":
        return modules.analyze_null_values(data)

    if tool == "outliers":
        return modules.analyze_outliers(data)

    if tool == "select_star":
        return modules.analyze_table(data)

    return {"error": f"Unknown data tool: {tool}"}

