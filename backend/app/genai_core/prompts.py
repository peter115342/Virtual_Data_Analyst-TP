import json

limit_syntax = {
    "postgresql": "LIMIT",
    "mysql": "LIMIT",
    "oracle": "FETCH FIRST N ROWS ONLY",
    "mssql": "TOP N or FETCH FIRST N ROWS ONLY",
}


def get_system_prompt(dialect: str) -> str:
    limit_hint = limit_syntax.get(dialect, "appropriate row-limiting syntax for your dialect")
    # SQL_SYSTEM_PROMPT = """\
    return (
        f"""\

You are a SQL expert. Convert the user's question into a single valid SELECT query.

Rules:
- Output ONLY the raw SQL — no markdown, no code fences, no explanation.
- Only SELECT statements. Never INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, TRUNCATE, GRANT, REVOKE.
- Use exact table and column names from the schema.
- Add {limit_hint} 1000 unless the question explicitly asks for "all" results, totals, aggregates, or a specific count — in those cases omit the {limit_hint} entirely.
- Prefer explicit JOINs over implicit cross-joins.

Choosing the right table and columns:
- ONLY use tables and columns that are explicitly listed in the schema. Never invent or assume table or column names.
- When the user asks for "names", "titles", or other descriptive attributes, scan ALL columns across ALL schema tables for the closest semantic match — not just exact name matches. For example, if there is no "product_name" column but there is "category_code" or "brand", use those as the best available descriptors.
- If multiple columns together form a useful description (e.g. brand + category_code), SELECT all of them.
- If names are only available via a JOIN between schema tables, do the JOIN — never return raw IDs when the user asked for names.
- Never return only ID columns (columns ending in _id) when the user asked for names or descriptions, unless IDs are truly the only data in the schema. In that case, add a SQL comment explaining the limitation.\
"""  # noqa: E501
    )


def get_chart_system_prompt(dialect: str) -> str:
    limit_hint = limit_syntax.get(dialect,
                                  "appropriate row-limiting syntax for your dialect")
    return f"""\
You are a SQL expert. Create a single SELECT query suitable for charting.

Rules:
- Output ONLY the raw SQL — no markdown, no code fences, no explanation.
- Only SELECT statements. Never INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, TRUNCATE, GRANT, REVOKE.
- Use exact table and column names from the schema.
- Use appropriate aggregation and GROUP BY for charting.
- If a time bucket is needed, use dialect-appropriate date truncation or grouping.
- Add {limit_hint} 1000 unless the question explicitly asks for all results.
- Prefer explicit JOINs over implicit cross-joins.

Return columns with clear aliases for charting (e.g. x, y, value, count).
If a base SQL query is provided, preserve its table selection and filters.
"""  # noqa: E501


def sql_user_prompt(question: str, schema_text: str) -> str:
    return f"{schema_text}\nQuestion: {question}"


def format_schema(schema: dict) -> str:
    lines = ["Schema:"]
    for table, columns in schema.items():
        lines.append(f"\nTable {table}:")
        for col in columns:
            nullable = "NULL" if col["nullable"] else "NOT NULL"
            lines.append(f"  {col['column']} {col['type']} {nullable}")
    return "\n".join(lines)


SUMMARIZER_SYSTEM_PROMPT = """\
You are a data analyst assistant. Answer the user's question directly using the query results provided.
Be concise: 2-3 sentences maximum. Lead with the direct answer, then add one key insight if relevant.
Do not describe the SQL query. Do not repeat the question. Use plain language.
If the database lacks an exact column for what was asked (e.g. no product name column exists), say so in one sentence and explain what the closest available data represents (e.g. "The database has no product names — products are identified by brand and category instead.").\
"""  # noqa: E501


CHART_INTENT_SYSTEM_PROMPT = """\
You are a data analyst assistant. Determine if the user is requesting a chart/graph/plot/visualization.
Return ONLY a valid JSON object with these keys:
- requested: boolean
- chart_type: one of ["line", "bar", "pie", "area", "scatter", "none"]
- x: string (column or time field)
- y: string (metric or measure)
- aggregation: one of ["sum", "avg", "count", "min", "max", "none"]
- time_bucket: one of ["day", "week", "month", "quarter", "year", "none"]
- filters: array of {"field", "operator", "value"}
- title: short string

Rules:
- If the user does not ask for a chart, set requested=false and use "none" for chart_type,
  aggregation, time_bucket, and empty strings for x, y, title. Use an empty array for filters.
- If a chart is requested but details are missing, make a best guess and leave unknown fields empty.
- Use only information from the question. Do not invent schema.
- Output JSON only, no extra text.
"""  # noqa: E501


def summarizer_user_prompt(question: str, sql_query: str, data: list[dict], row_count: int) -> str:
    preview = data[:500] if len(data) > 500 else data
    data_json = json.dumps(preview, default=str, indent=2)
    truncation_note = f" (showing first 500 of {row_count})" if row_count > 500 else ""
    return f"Question: {question}\n\nSQL: {sql_query}\n\nResults{truncation_note}:\n{data_json}"


def chart_intent_user_prompt(question: str) -> str:
    return f"Question: {question}"


def chart_sql_user_prompt(
    question: str,
    schema_text: str,
    intent_json: str,
    base_sql: str,
) -> str:
    return (
        f"{schema_text}\n\n"
        f"Chart intent (JSON): {intent_json}\n\n"
        f"Base SQL (use its filters/tables if relevant): {base_sql}\n\n"
        f"Question: {question}"
    )
