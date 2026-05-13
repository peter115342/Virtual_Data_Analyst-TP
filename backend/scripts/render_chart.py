import json
import os
from typing import Any

import matplotlib.pyplot as plt
import requests

DEFAULT_API_URL = "http://localhost:8000/api/ask"
DEFAULT_OUTPUT = "chart_output.png"


def _pick_field(row: dict, preferred: str | None) -> str | None:
    if preferred and preferred in row:
        return preferred
    for key in row.keys():
        return key
    return None


def _coerce_number(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _load_chart_payload(question: str) -> dict:
    api_url = os.getenv("VDA_API_URL", DEFAULT_API_URL)
    token = os.getenv("VDA_TOKEN", "").strip()

    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    payload = {"question": question}
    resp = requests.post(api_url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.json()


def _resolve_xy(chart_intent: dict | None, rows: list[dict]) -> tuple[str | None, str | None]:
    if not rows:
        return None, None
    x_pref = None
    y_pref = None
    if chart_intent:
        x_pref = chart_intent.get("x") or None
        y_pref = chart_intent.get("y") or None

    x_field = _pick_field(rows[0], x_pref)
    y_field = _pick_field(rows[0], y_pref)
    if x_field == y_field:
        keys = list(rows[0].keys())
        if len(keys) > 1:
            y_field = keys[1]
    return x_field, y_field


def _axis_label(preferred: str | None, fallback: str) -> str:
    if not preferred or preferred in {"x", "y"}:
        return fallback
    return preferred


def _render_chart(response_data: dict, output_path: str) -> None:
    chart_intent = response_data.get("chart_intent") or {}
    chart_data = response_data.get("chart_data") or []

    if not chart_data:
        raise RuntimeError("No chart_data in response. Ask a chart question.")

    chart_type = (chart_intent.get("chart_type") or "bar").lower()
    title = chart_intent.get("title") or "Chart"

    x_field, y_field = _resolve_xy(chart_intent, chart_data)
    if not x_field or not y_field:
        raise RuntimeError("Unable to determine chart x/y fields from data.")

    x_label = _axis_label((chart_intent or {}).get("x"), x_field)
    y_label = _axis_label((chart_intent or {}).get("y"), y_field)

    x_values = [row.get(x_field) for row in chart_data]
    y_values = [_coerce_number(row.get(y_field)) for row in chart_data]

    if any(v is None for v in y_values):
        raise RuntimeError("Y values are not numeric. Check chart_data.")

    plt.figure(figsize=(10, 5))
    if chart_type in {"line", "area"}:
        plt.plot(x_values, y_values, marker="o")
        if chart_type == "area":
            plt.fill_between(range(len(y_values)), y_values, alpha=0.3)
            plt.xticks(range(len(x_values)), x_values, rotation=45, ha="right")
    elif chart_type == "scatter":
        plt.scatter(x_values, y_values)
    elif chart_type == "pie":
        plt.pie(y_values, labels=x_values, autopct="%1.1f%%")
    else:
        x_labels = [str(v) for v in x_values]
        x_pos = range(len(x_labels))
        plt.bar(x_pos, y_values)
        plt.xticks(x_pos, x_labels, rotation=45, ha="right")

    if chart_type != "pie":
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        if chart_type not in {"bar"}:
            plt.xticks(rotation=45, ha="right")

        if y_values:
            y_max = max(y_values)
            if y_max > 0:
                plt.ylim(0, y_max * 1.15)

    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def main() -> None:
    question = os.getenv("VDA_QUESTION", "")
    output_path = os.getenv("VDA_OUTPUT", DEFAULT_OUTPUT)

    if not question:
        print("Set VDA_QUESTION to a chart request (e.g. 'Plot sales by month').")
        return

    response_data = _load_chart_payload(question)
    print(json.dumps(response_data.get("chart_intent"), indent=2))
    _render_chart(response_data, output_path)
    print(f"Chart saved to {output_path}")


if __name__ == "__main__":
    main()
