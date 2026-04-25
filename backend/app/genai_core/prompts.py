import json

SQL_SYSTEM_PROMPT = """\
You are a SQL expert. Convert the user's question into a single valid SELECT query.

Rules:
- Output ONLY the raw SQL — no markdown, no code fences, no explanation.
- Only SELECT statements. Never INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, TRUNCATE, GRANT, REVOKE.
- Use exact table and column names from the schema.
- Add LIMIT 1000 unless the question asks for totals/aggregates or a specific count.
- Prefer explicit JOINs over implicit cross-joins.\
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
Do not describe the SQL query. Do not repeat the question. Use plain language.\
"""  # noqa: E501


def summarizer_user_prompt(question: str, sql_query: str, data: list[dict], row_count: int) -> str:
    preview = data[:10] if len(data) > 10 else data
    data_json = json.dumps(preview, default=str, indent=2)
    truncation_note = f" (showing first 10 of {row_count})" if row_count > 10 else ""
    return f"Question: {question}\n\nSQL: {sql_query}\n\nResults{truncation_note}:\n{data_json}"
