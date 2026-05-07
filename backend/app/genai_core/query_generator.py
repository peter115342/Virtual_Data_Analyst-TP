# LLM-based SQL query generation

from openai import OpenAI

from app.config import settings
from app.genai_core.prompts import get_system_prompt, format_schema, sql_user_prompt


class QueryGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=settings.api_key, base_url=settings.openai_base_url)
        self.model = "azure.gpt-4.1"

    async def generate_query(self, question: str, schema: dict, dialect: str,
        history_text: str = "",
        previous_sql: str = "",
        previous_question: str = "",
        last_successful_sql: str = "") -> str:
        schema_text = format_schema(schema)
        sections = []
        sections.append("""
### ROLE
You are a deterministic PostgreSQL query generator.
You only translate schema into SQL.
You must not interpret meaning.
""")

        sections.append("""
### STRICT SEMANTIC BOUNDARY (CRITICAL)
Do not interpret natural language into business logic.
If a term is not in schema, treat it as UNKNOWN.
Do not infer filters, metrics, time logic, or categories.
""")

        sections.append("""
### HARD RULES
- Use only schema tables and columns
- Never invent columns or logic
- Never assume meaning of words (active, sales, users, top, etc.)
- Current question is the only source of logic
- If missing info, return minimal valid SQL
""")

        sections.append("""
### OUTPUT FORMAT
Return only raw SQL.
No markdown.
No explanation.
No comments.
""")

        sections.append(f"""
### SCHEMA
{schema_text}
""")

        sections.append("""
### SAFE RULES
Do not map natural language to business logic.
Do not infer meaning of words.
Do not assume aggregations or filters.
""")

        if history_text:
            sections.append(f"""
### HISTORY (CONTEXT ONLY)
{history_text}
""")

        if previous_sql:
            sections.append(f"""
### PREVIOUS SQL (REFERENCE ONLY)
{previous_sql}
""")

        if last_successful_sql:
            sections.append(f"""
### LAST SUCCESSFUL SQL (REFERENCE ONLY)
{last_successful_sql}
""")

        sections.append(f"""
### CURRENT QUESTION
{question}
""")

        sections.append("""
### FINAL RULE
Verify all columns exist in schema.
Remove any inferred logic.
If uncertain, return simplest SELECT.
""")
        user_prompt = "\n\n".join(sections)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
#                 {"role": "system", "content": SQL_SYSTEM_PROMPT},
#                 {"role": "user", "content": user_prompt},
                {"role": "system", "content": get_system_prompt(dialect)},
                {"role": "user", "content": sql_user_prompt(question, schema_text)},
            ],
            temperature=0.0,
        )

        sql = response.choices[0].message.content.strip()

        if sql.startswith("```"):
            lines = sql.split("\n")
            sql = "\n".join(lines[1:-1]).strip()
        if sql.lower().startswith("sql"):
            sql = sql[3:].strip()

        return sql
