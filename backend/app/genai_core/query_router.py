from openai import OpenAI

from app.config import settings


class QueryRouter:
    def __init__(self):
        self.client = OpenAI(api_key=settings.api_key, base_url=settings.openai_base_url)

    async def route(self, question: str, schema: dict, context: dict) -> dict:
        # 1. najprv deterministické pravidlá
        rule = self.rule_based(question)
        if rule:
            return rule

        # 2. ak nejednoznačné → LLM rozhodne
        return await self._llm_route(question, schema, context)

    def rule_based(self, question: str) -> dict | None:
        data_tools_keywords = [
            # TODO keywords
            ""
        ]
        if any(kw in question.lower() for kw in data_tools_keywords):
            return {"route": "data_tools", "reason": ""}
        return None

    async def _llm_route(self, question: str, schema: dict, context: dict) -> dict:
        # LLM vráti JSON: {"route": "database"|"data_tools", "reason": "..."}
        # TODO
        pass