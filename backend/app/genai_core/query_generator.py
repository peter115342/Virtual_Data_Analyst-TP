# LLM-based SQL query generation

from openai import OpenAI

from app.config import settings
from app.genai_core.prompts import SQL_SYSTEM_PROMPT, format_schema, sql_user_prompt


class QueryGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=settings.api_key, base_url=settings.openai_base_url)
        self.model = "azure.gpt-4.1"

    async def generate_query(self, question: str, schema: dict) -> str:
        schema_text = format_schema(schema)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SQL_SYSTEM_PROMPT},
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
