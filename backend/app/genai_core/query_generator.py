# LLM-based SQL query generation

from openai import OpenAI

from app.config import settings


class QueryGenerator:
    def __init__(self):
        """Initialize LLM client for SQL generation"""
        self.client = OpenAI(api_key=settings.api_key, base_url=settings.openai_base_url)
        self.model = "azure.gpt-4.1"

    def _format_schema_for_prompt(self, schema: dict) -> str:
        # TODO
        #  change syntax to ORM
        """
        Convert schema dict to a readable text format for the LLM

        Args:
            schema: Dictionary with table names as keys and column info as values

        Returns:
            Formatted schema string
        """
        schema_text = "Database Schema:\n\n"
        for table_name, columns in schema.items():
            schema_text += f"Table: {table_name}\n"
            for col in columns:
                nullable = "NULL" if col["nullable"] else "NOT NULL"
                schema_text += f"  - {col['column']} ({col['type']}) {nullable}\n"
            schema_text += "\n"
        return schema_text

    async def generate_query(self, question: str, schema: dict, dialect: str) -> str:
        # TODO
        #  change syntax to ORM
        """
        Generate SQL query from natural language question using LLM

        Args:
            question: Natural language question from the user
            schema: Database schema dictionary
            dialect: Database dialect

        Returns:
            Generated SQL query string
        """
        schema_text = self._format_schema_for_prompt(schema)

        limit_syntax = {
            "postgresql": "LIMIT",
            "mysql": "LIMIT",
            "oracle": "FETCH FIRST N ROWS ONLY",
            "mssql": "TOP N or FETCH FIRST N ROWS ONLY",
        }
        limit_hint = limit_syntax.get(dialect, "appropriate row-limiting syntax for your dialect")

        system_prompt = f"""You are a {dialect} expert. Your task is to convert natural language questions into valid SQL queries.

IMPORTANT RULES:
1. Generate ONLY SELECT queries (read-only access)
2. NEVER use INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, TRUNCATE, GRANT, or REVOKE
3. Return ONLY the raw SQL query - no explanations, no markdown formatting, no code blocks
4. Use proper {dialect} syntax
5. Include appropriate WHERE clauses, JOINs, GROUP BY, ORDER BY as needed
6. Add {limit_hint} clauses when appropriate to avoid returning too much data
7. Use table and column names exactly as they appear in the schema
"""

        user_prompt = f"""{schema_text}
User Question: {question}

Generate a SQL query that answers this question. Return ONLY the SQL query, nothing else."""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )

        sql_query = response.choices[0].message.content.strip()

        if sql_query.startswith("```"):
            lines = sql_query.split("\n")
            sql_query = "\n".join(lines[1:-1]) if len(lines) > 2 else sql_query
            sql_query = sql_query.strip()

        if sql_query.lower().startswith("sql"):
            sql_query = sql_query[3:].strip()

        return sql_query
