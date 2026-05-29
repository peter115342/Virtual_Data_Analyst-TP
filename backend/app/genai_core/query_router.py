import json
import re

from openai import OpenAI

from app.config import settings
from app.genai_core.prompts import ROUTER_SYSTEM_PROMPT, format_schema


class QueryRouter:
    VALID_ROUTES = {"database", "data_tools"}
    VALID_TOOLS = {"null_values", "outliers", "select_star"}

    TOOL_KEYWORDS = {
        "null_values": (
            "missing value",
            "missing values",
            "null value",
            "null values",
            "nulls",
            "empty value",
            "empty values",
            "blank",
            "blanks",
            "incomplete",
            "chybajuce",
            "chyba",
            "chyby",
            "null hodnot",
            "prazdne",
            "neuplne",
        ),
        "outliers": (
            "outlier",
            "outliers",
            "anomaly",
            "anomalies",
            "anomal",
            "extreme value",
            "extreme values",
            "unusual value",
            "unusual values",
            "suspicious value",
            "suspicious values",
            "odlah",
            "vychyl",
            "anomalie",
        ),
        "select_star": (
            "select *",
            "select star",
            "select_star",
            "profile",
            "profil",
            "profiling",
            "describe table",
            "table overview",
            "data overview",
            "dataset overview",
            "basic statistics",
            "basic stats",
            "summary of table",
            "prehlad dat",
            "prehlad tabul",
        ),
    }

    DATABASE_KEYWORDS = (
        "count",
        "how many",
        "kolko",
        "sum",
        "total",
        "average",
        "avg",
        "minimum",
        "maximum",
        "top",
        "bottom",
        "filter",
        "where",
        "group by",
        "order by",
        "list",
        "show",
        "najviac",
        "najmenej",
    )

    def __init__(self, client=None, model: str = "azure.gpt-4.1"):
        self.client = client or OpenAI(api_key=settings.api_key, base_url=settings.openai_base_url)
        self.model = model

    async def route(self, question: str, schema: dict, context: dict) -> dict:
        rule = self.rule_based(question)
        if rule:
            return rule

        return await self._llm_route(question, schema, context)

    def rule_based(self, question: str) -> dict | None:
        normalized = self._normalize_question(question)
        if not normalized:
            return {
                "route": "database",
                "tool": None,
                "reason": "Empty question; defaulting to database route.",
            }

        for tool, keywords in self.TOOL_KEYWORDS.items():
            if any(keyword in normalized for keyword in keywords):
                return {
                    "route": "data_tools",
                    "tool": tool,
                    "reason": f"Matched deterministic {tool} keyword.",
                }

        if any(keyword in normalized for keyword in self.DATABASE_KEYWORDS):
            return {
                "route": "database",
                "tool": None,
                "reason": "Matched deterministic database keyword.",
            }

        return None

    async def _llm_route(self, question: str, schema: dict, context: dict) -> dict:
        if not settings.api_key:
            return self._database_fallback("Router LLM disabled because API key is not configured.")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
                    {"role": "user", "content": self._user_prompt(question, schema, context)},
                ],
                temperature=0.0,
            )
            content = response.choices[0].message.content
            return self._parse_llm_decision(content)
        except Exception:
            return self._database_fallback("Router LLM failed; defaulting to database route.")

    def _parse_llm_decision(self, content: str | None) -> dict:
        if not content:
            return self._database_fallback("Router LLM returned empty content.")

        raw_json = self._strip_json_fence(content.strip())
        try:
            payload = json.loads(raw_json)
        except json.JSONDecodeError:
            return self._database_fallback("Router LLM returned invalid JSON.")

        if not isinstance(payload, dict):
            return self._database_fallback("Router LLM returned non-object JSON.")

        route = payload.get("route")
        tool = payload.get("tool")
        reason = payload.get("reason") or "Router LLM decision."

        if route not in self.VALID_ROUTES:
            return self._database_fallback("Router LLM returned unsupported route.")

        if route == "database":
            return {"route": "database", "tool": None, "reason": str(reason)}

        if tool not in self.VALID_TOOLS:
            return self._database_fallback("Router LLM returned unsupported data tool.")

        return {"route": "data_tools", "tool": tool, "reason": str(reason)}

    def _user_prompt(self, question: str, schema: dict, context: dict) -> str:
        sections = [
            "### SCHEMA",
            format_schema(schema),
            "### QUESTION",
            question,
        ]

        history_text = context.get("history_text") if isinstance(context, dict) else ""
        previous_question = context.get("previous_question") if isinstance(context, dict) else ""
        previous_sql = context.get("previous_sql") if isinstance(context, dict) else ""

        if history_text:
            sections.extend(["### CONVERSATION HISTORY", str(history_text)])
        if previous_question:
            sections.extend(["### PREVIOUS QUESTION", str(previous_question)])
        if previous_sql:
            sections.extend(["### PREVIOUS SQL", str(previous_sql)])

        return "\n".join(sections)

    @staticmethod
    def _normalize_question(question: str) -> str:
        lowered = question.strip().lower()
        return re.sub(r"\s+", " ", lowered)

    @staticmethod
    def _strip_json_fence(content: str) -> str:
        if content.startswith("```"):
            lines = content.splitlines()
            if len(lines) >= 3:
                return "\n".join(lines[1:-1]).strip()
        if content.lower().startswith("json"):
            return content[4:].strip()
        return content

    @staticmethod
    def _database_fallback(reason: str) -> dict:
        return {"route": "database", "tool": None, "reason": reason}
