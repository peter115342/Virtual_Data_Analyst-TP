import io
from typing import Any

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")


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


def render_chart_png(chart_data: list[dict], chart_intent: dict | None) -> bytes:
    if not chart_data:
        raise ValueError("No chart data to render.")

    chart_type = (chart_intent or {}).get("chart_type") or "bar"
    chart_type = chart_type.lower()
    title = (chart_intent or {}).get("title") or "Chart"

    x_field, y_field = _resolve_xy(chart_intent, chart_data)
    if not x_field or not y_field:
        raise ValueError("Unable to determine chart x/y fields from data.")

    x_label = _axis_label((chart_intent or {}).get("x"), x_field)
    y_label = _axis_label((chart_intent or {}).get("y"), y_field)

    x_values = [row.get(x_field) for row in chart_data]
    y_values = [_coerce_number(row.get(y_field)) for row in chart_data]

    if any(v is None for v in y_values):
        raise ValueError("Y values are not numeric.")

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

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", dpi=150)
    plt.close()
    buffer.seek(0)
    return buffer.getvalue()
