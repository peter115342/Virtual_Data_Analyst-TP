# LLM-based chart intent detection

import json

from openai import OpenAI

from app.config import settings
from app.genai_core.prompts import CHART_INTENT_SYSTEM_PROMPT, chart_intent_user_prompt

_DEFAULT_INTENT = {
    "requested": False,
    "chart_type": "none",
    "x": "",
    "y": "",
    "aggregation": "none",
    "time_bucket": "none",
    "filters": [],
    "title": "",
}


class ChartIntentDetector:
    def __init__(self):
        self.client = OpenAI(api_key=settings.api_key, base_url=settings.openai_base_url)
        self.model = "azure.gpt-4.1"

    async def detect_intent(self, question: str) -> dict:
        if not settings.api_key:
            return dict(_DEFAULT_INTENT)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": CHART_INTENT_SYSTEM_PROMPT},
                {"role": "user", "content": chart_intent_user_prompt(question)},
            ],
            temperature=0.0,
        )

        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1]).strip()
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()

        try:
            intent = json.loads(raw)
        except json.JSONDecodeError:
            return dict(_DEFAULT_INTENT)

        if not isinstance(intent, dict):
            return dict(_DEFAULT_INTENT)

        normalized = dict(_DEFAULT_INTENT)
        for key in normalized:
            if key in intent:
                normalized[key] = intent[key]

        if not isinstance(normalized.get("requested"), bool):
            normalized["requested"] = False

        return normalized
