import json


limit_syntax = {
    "postgresql": "LIMIT",
    "mysql": "LIMIT",
    "oracle": "FETCH FIRST N ROWS ONLY",
    "mssql": "TOP N or FETCH FIRST N ROWS ONLY",
}

def get_system_prompt(dialect: str) -> str:
    limit_hint = limit_syntax.get(dialect,
                                  "appropriate row-limiting syntax for your dialect")
# SQL_SYSTEM_PROMPT = """\
    return f"""\

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


# def sql_user_prompt(question: str, schema_text: str) -> str:
#     return f"{schema_text}\nQuestion: {question}"

def sql_user_prompt(question: str, chat_history_context: dict, schema_text: str) -> str:

    sections = []

    sections.append(f"""
    ### SCHEMA
    {schema_text}
""")

    sections.append("""
    ### COLUMN MATCHING
    If the user asks for something not literally in the schema:
    - Scan ALL tables and columns for the closest semantic match
    - If multiple columns together describe what was asked
      (e.g. brand + category), SELECT all of them
    - If a JOIN is needed to get descriptive data instead of raw IDs,
      do the JOIN
    - Never return only ID columns when user asked for names or descriptions
    - If truly no match exists anywhere in schema, return simplest valid
      SELECT with a SQL comment explaining the limitation
""")

    sections.append("""
    ### HARD RULES
    - Only SELECT statements — never INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, TRUNCATE, GRANT, REVOKE
    - Use exact table and column names from schema (no inventing columns)
    - Return only raw SQL — no markdown, no explanation, no comments (except the limitation case above)
""")

    if chat_history_context["history_text"]:
        sections.append(f"""
    ### CONVERSATION HISTORY (CONTEXT ONLY)
    {chat_history_context["history_text"]}
""")

    if chat_history_context["previous_sql"]:
        sections.append(f"""
    ### PREVIOUS SQL (REFERENCE ONLY)
    {chat_history_context["previous_sql"]}
""")

    if chat_history_context["previous_question"]:
        sections.append(f"""
    ### PREVIOUS QUESTION (REFERENCE ONLY)
    {chat_history_context["previous_question"]}
""")

    sections.append(f"""
    ### QUESTION
    {question}
""")

    user_prompt = "\n\n".join(sections)

    return user_prompt


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


def summarizer_user_prompt(question: str, sql_query: str, data: list[dict], row_count: int) -> str:
    preview = data[:500] if len(data) > 500 else data
    data_json = json.dumps(preview, default=str, indent=2)
    truncation_note = f" (showing first 500 of {row_count})" if row_count > 500 else ""
    return f"Question: {question}\n\nSQL: {sql_query}\n\nResults{truncation_note}:\n{data_json}"
