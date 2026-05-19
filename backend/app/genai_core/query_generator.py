# LLM-based SQL query generation

import json

from openai import OpenAI

from app.config import settings
from app.genai_core.prompts import (
    chart_sql_user_prompt,
    format_schema,
    get_chart_system_prompt,
    get_system_prompt,
    sql_user_prompt,
)


class QueryGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=settings.api_key, base_url=settings.openai_base_url)
        self.model = "azure.gpt-4.1"

    async def generate_query(self, question: str,
        schema: dict,
        dialect: str,
        chat_history_context: dict) -> str:

        schema_text = format_schema(schema)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": get_system_prompt(dialect)},
                {"role": "user", "content": sql_user_prompt(question, chat_history_context,
                                                            schema_text)},
            ],
            temperature=0.0,
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("LLM response did not include SQL content")

        sql = content.strip()

        if sql.startswith("```"):
            lines = sql.split("\n")
            sql = "\n".join(lines[1:-1]).strip()
        if sql.lower().startswith("sql"):
            sql = sql[3:].strip()

        return sql

    async def generate_chart_query(
        self,
        question: str,
        chart_intent: dict,
        schema: dict,
        dialect: str,
        base_sql: str,
    ) -> str:
        schema_text = format_schema(schema)
        intent_json = json.dumps(chart_intent, ensure_ascii=True)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": get_chart_system_prompt(dialect)},
                {
                    "role": "user",
                    "content": chart_sql_user_prompt(
                        question,
                        schema_text,
                        intent_json,
                        base_sql,
                    ),
                },
            ],
            temperature=0.0,
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("LLM response did not include chart SQL content")

        sql = content.strip()

        if sql.startswith("```"):
            lines = sql.split("\n")
            sql = "\n".join(lines[1:-1]).strip()
        if sql.lower().startswith("sql"):
            sql = sql[3:].strip()

        return sql
