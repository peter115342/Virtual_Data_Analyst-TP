# LLM-based response formatting and summarization

from openai import OpenAI

from app.config import settings
from app.genai_core.prompts import SUMMARIZER_SYSTEM_PROMPT, summarizer_user_prompt


class ResponseSummarizer:
    def __init__(self):
        self.client = OpenAI(api_key=settings.api_key, base_url=settings.openai_base_url)
        self.model = "vertex_ai.gemini-2.5-flash"

    async def summarize_query_results(
        self, sql_query: str, data: list[dict], context: str | None = None
    ) -> str:
        question = context or "Summarize the results."
        row_count = len(data)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SUMMARIZER_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": summarizer_user_prompt(question, sql_query, data, row_count),
                },
            ],
            temperature=0.3,
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("LLM response did not include summary content")

        return content
