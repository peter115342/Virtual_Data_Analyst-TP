# LLM-based response formatting and summarization

import json

from openai import OpenAI

from app.config import settings


class ResponseSummarizer:
    def __init__(self):
        """Initialize LLM client for summarization"""
        self.client = OpenAI(api_key=settings.api_key, base_url=settings.openai_base_url)
        self.model = "vertex_ai.gemini-2.5-flash"

    async def summarize_query_results(
        self, sql_query: str, data: list[dict], context: str | None = None
    ) -> str:
        # TODO ??
        #  change syntax to ORM ??
        """
        Generate a human-readable summary of database query results using LLM

        Args:
            sql_query: The SQL query that was executed
            data: The query results as a list of dictionaries
            context: Optional user context to guide the summary

        Returns:
            A natural language summary of the results
        """
        row_count = len(data)
        data_preview = data[:10] if len(data) > 10 else data
        data_json = json.dumps(data_preview, default=str, indent=2)

        user_context = f"\n\nUser context: {context}" if context else ""
        prompt = f"""Analyze and summarize the following database query results.

SQL Query:
{sql_query}

Results (showing {len(data_preview)} of {row_count} rows):
{data_json}{user_context}

Provide a clear, concise summary that:
1. Describes what the data shows
2. Highlights key insights or patterns
3. Mentions any notable values or trends
4. Is understandable for non-technical users

Keep the summary to 2-4 paragraphs."""

        response = self.client.chat.completions.create(
            model=self.model, messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content
