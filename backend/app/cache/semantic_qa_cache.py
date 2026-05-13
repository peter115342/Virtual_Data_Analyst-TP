import math
import re
import time
import uuid
from dataclasses import dataclass

from openai import OpenAI

from app.cache import redis_client
from app.config import settings


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return -1.0

    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b, strict=False):
        dot += x * y
        na += x * x
        nb += y * y

    denom = math.sqrt(na) * math.sqrt(nb)
    if denom == 0.0:
        return -1.0
    return dot / denom


def _qa_index_key(db_fp: str) -> str:
    return f"vda:qa:index:{db_fp}"


def _qa_entry_key(db_fp: str, entry_id: str) -> str:
    return f"vda:qa:entry:{db_fp}:{entry_id}"


_STOPWORDS = {
    "a",
    "aj",
    "ak",
    "ako",
    "ale",
    "and",
    "an",
    "are",
    "co",
    "do",
    "for",
    "how",
    "in",
    "is",
    "je",
    "kolko",
    "many",
    "mi",
    "na",
    "o",
    "of",
    "on",
    "or",
    "po",
    "pre",
    "pri",
    "s",
    "sa",
    "si",
    "su",
    "the",
    "to",
    "u",
    "v",
    "vo",
    "what",
    "z",
    "za",
    "ze",
}


_QUANTITY_WORDS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "first": "1",
    "second": "2",
    "third": "3",
    "fourth": "4",
    "fifth": "5",
    "sixth": "6",
    "seventh": "7",
    "eighth": "8",
    "ninth": "9",
    "tenth": "10",
    "jeden": "1",
    "jedna": "1",
    "jedno": "1",
    "dva": "2",
    "dve": "2",
    "tri": "3",
    "styri": "4",
    "pat": "5",
    "sest": "6",
    "sedem": "7",
    "osem": "8",
    "devat": "9",
    "desat": "10",
    "prvy": "1",
    "prva": "1",
    "prve": "1",
    "prvych": "1",
    "druhy": "2",
    "druha": "2",
    "druhe": "2",
    "druhych": "2",
    "treti": "3",
    "tretia": "3",
    "trete": "3",
    "stvrty": "4",
    "stvrta": "4",
    "stvrte": "4",
    "paty": "5",
    "sesty": "6",
    "siesty": "6",
    "siedmy": "7",
    "osmy": "8",
    "deviaty": "9",
    "desiaty": "10",
}


def _quantity_signature(question: str) -> tuple[str, ...]:
    normalized = re.sub(r"\s+", " ", question.strip().lower())
    ascii_question = normalized.encode("ascii", "ignore").decode("ascii")
    tokens: list[str] = []

    for token in re.findall(r"\b\w+\b", ascii_question):
        if token.isdigit():
            tokens.append(token)
            continue

        mapped = _QUANTITY_WORDS.get(token)
        if mapped is not None:
            tokens.append(mapped)

    return tuple(sorted(set(tokens)))


def _normalize_text(text: str) -> str:
    lowered = text.strip().lower()
    ascii_text = lowered.encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^a-z0-9\s]", " ", ascii_text)
    return re.sub(r"\s+", " ", cleaned).strip()


def _keyword_signature(question: str) -> set[str]:
    normalized = _normalize_text(question)
    tokens: set[str] = set()
    for token in normalized.split(" "):
        if not token or token in _STOPWORDS:
            continue
        if token.isdigit():
            continue
        if len(token) < 2:
            continue
        tokens.add(token)
    return tokens


def _keyword_similarity(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


@dataclass(frozen=True)
class SemanticQACacheHit:
    similarity: float
    cached_question: str
    sql_query: str
    summary: str
    row_count: int
    entry_id: str


@dataclass(frozen=True)
class SemanticQACacheProbe:
    hit: SemanticQACacheHit | None
    best_similarity: float | None
    best_entry_id: str | None


async def _embed_question(question: str) -> list[float] | None:
    if not settings.api_key:
        return None

    client = OpenAI(api_key=settings.api_key, base_url=settings.openai_base_url)
    try:
        resp = client.embeddings.create(
            model=settings.semantic_cache_embedding_model,
            input=question,
        )
        embedding = resp.data[0].embedding
        if isinstance(embedding, list) and embedding and isinstance(embedding[0], (int, float)):
            return [float(x) for x in embedding]
        return None
    except Exception as exc:
        print(f"Semantic cache embedding warning: {exc}")
        return None


async def probe_similar_answer(db_fp: str, question: str) -> SemanticQACacheProbe:
    if not settings.semantic_cache_enabled or not redis_client.is_connected():
        return SemanticQACacheProbe(hit=None, best_similarity=None, best_entry_id=None)

    query_vec = await _embed_question(question)
    if not query_vec:
        return SemanticQACacheProbe(hit=None, best_similarity=None, best_entry_id=None)

    index_key = _qa_index_key(db_fp)
    candidate_ids = await redis_client.zrevrange(
        index_key, 0, max(0, settings.semantic_cache_max_candidates - 1)
    )
    if not candidate_ids:
        return SemanticQACacheProbe(hit=None, best_similarity=None, best_entry_id=None)

    best: SemanticQACacheHit | None = None
    best_score = -1.0
    best_id: str | None = None
    query_quantity_signature = _quantity_signature(question)
    query_keywords = _keyword_signature(question)

    for entry_id in candidate_ids:
        payload = await redis_client.get_json(_qa_entry_key(db_fp, entry_id))
        if not isinstance(payload, dict):
            continue

        emb = payload.get("embedding")
        if not isinstance(emb, list):
            continue

        try:
            emb_vec = [float(x) for x in emb]
        except (TypeError, ValueError):
            continue

        score = _cosine_similarity(query_vec, emb_vec)
        if score > best_score:
            question_value = payload.get("question")
            sql_value = payload.get("sql_query")
            summary_value = payload.get("summary")
            row_count_value = payload.get("row_count")

            cached_question = question_value if isinstance(question_value, str) else ""
            sql_query = sql_value if isinstance(sql_value, str) else ""
            summary = summary_value if isinstance(summary_value, str) else ""
            row_count = row_count_value if isinstance(row_count_value, int) else 0
            cached_quantity_signature = _quantity_signature(cached_question)
            cached_keywords = _keyword_signature(cached_question)
            keyword_sim = _keyword_similarity(query_keywords, cached_keywords)

            if query_keywords and cached_keywords:
                if keyword_sim < float(settings.semantic_cache_keyword_threshold):
                    continue

            if query_quantity_signature and cached_quantity_signature != query_quantity_signature:
                continue

            if sql_query and summary:
                if query_keywords and cached_keywords:
                    weight = float(settings.semantic_cache_keyword_weight)
                    score = (score * (1.0 - weight)) + (keyword_sim * weight)

                best_score = score
                best_id = entry_id
                best = SemanticQACacheHit(
                    similarity=score,
                    cached_question=cached_question,
                    sql_query=sql_query,
                    summary=summary,
                    row_count=row_count,
                    entry_id=entry_id,
                )

    best_similarity = None if best_score < 0 else float(best_score)
    if best is None:
        return SemanticQACacheProbe(
            hit=None, best_similarity=best_similarity, best_entry_id=best_id
        )

    if best.similarity < float(settings.semantic_cache_threshold):
        return SemanticQACacheProbe(
            hit=None, best_similarity=best_similarity, best_entry_id=best_id
        )

    return SemanticQACacheProbe(hit=best, best_similarity=best_similarity, best_entry_id=best_id)


async def find_similar_answer(db_fp: str, question: str) -> SemanticQACacheHit | None:
    probe = await probe_similar_answer(db_fp, question)
    return probe.hit


async def store_answer(
    db_fp: str,
    question: str,
    sql_query: str,
    summary: str,
    row_count: int,
) -> None:
    if (
        not settings.semantic_cache_enabled
        or not redis_client.is_connected()
        or not question.strip()
        or not sql_query.strip()
        or not summary.strip()
    ):
        return

    emb = await _embed_question(question)
    if not emb:
        return

    entry_id = uuid.uuid4().hex
    entry_key = _qa_entry_key(db_fp, entry_id)
    index_key = _qa_index_key(db_fp)

    await redis_client.set_json(
        entry_key,
        {
            "id": entry_id,
            "question": question,
            "sql_query": sql_query,
            "summary": summary,
            "row_count": row_count,
            "embedding": emb,
            "created_at": int(time.time()),
        },
        ttl_seconds=settings.semantic_cache_ttl_seconds,
    )

    now = float(time.time())
    await redis_client.zadd(index_key, {entry_id: now})
    await redis_client.expire(index_key, settings.semantic_cache_ttl_seconds)

    max_entries = int(settings.semantic_cache_max_entries)
    if max_entries > 0:
        await redis_client.zremrangebyrank(index_key, 0, -(max_entries + 1))
