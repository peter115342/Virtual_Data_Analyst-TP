"""
Main API Routes
TODO: Implement API endpoints according to architecture
"""

import hashlib
import re
import unicodedata
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

from app.cache import redis_client
from app.cache import semantic_qa_cache
from app.auth.entra import validate_token
from app.config import settings
from app.database import connection, chat_history
from app.database.connection import get_db_manager
from app.database.mongo import get_db
from app.database.utils import build_db_connection_url
from app.genai_core.query_generator import QueryGenerator
from app.genai_core.response_summarizer import ResponseSummarizer

router = APIRouter(prefix="/api", tags=["api"])

CACHE_PREFIX = "vda"
CACHE_METRICS_PREFIX = f"{CACHE_PREFIX}:metrics"
CACHE_METRIC_BUCKETS = (
    "schema",
    "nl2sql",
    "sql_results",
    "summary",
    "qa_semantic",
    "chat_history",
)

QUESTION_STOPWORDS = {
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
    "na",
    "o",
    "of",
    "on",
    "or",
    "po",
    "pre",
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
}


def _short_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _normalize_sql(sql_query: str) -> str:
    return re.sub(r"\s+", " ", sql_query).strip().lower()


def _normalize_question_text(question: str) -> str:
    lowered = question.strip().lower()
    ascii_question = unicodedata.normalize("NFKD", lowered).encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^a-z0-9\s]", " ", ascii_question)
    return re.sub(r"\s+", " ", cleaned).strip()


def _question_signature(question: str) -> str:
    normalized = _normalize_question_text(question)
    tokens = [
        token
        for token in normalized.split(" ")
        if token
        and token not in QUESTION_STOPWORDS
        and (token.isdigit() or len(token) > 1)
    ]

    if not tokens:
        return normalized

    return " ".join(sorted(set(tokens)))


def _db_fingerprint(db_manager: connection.DatabaseManager) -> str:
    database_url = getattr(db_manager, "database_url", "") or "no-db"
    return _short_hash(database_url)


def _schema_cache_key(db_fp: str) -> str:
    return f"{CACHE_PREFIX}:schema:{db_fp}"


def _nl2sql_cache_key(db_fp: str, question_signature: str) -> str:
    return f"{CACHE_PREFIX}:nl2sql:{db_fp}:{_short_hash(question_signature)}"


def _sql_result_cache_key(db_fp: str, sql_query: str) -> str:
    return f"{CACHE_PREFIX}:sqlres:{db_fp}:{_short_hash(_normalize_sql(sql_query))}"


def _summary_cache_key(db_fp: str, sql_query: str, context: str | None) -> str:
    normalized_sql = _normalize_sql(sql_query)
    context_hash = _short_hash((context or "").strip().lower())
    return f"{CACHE_PREFIX}:summary:{db_fp}:{_short_hash(normalized_sql)}:{context_hash}"


def _chat_cache_key(session_id: str) -> str:
    return f"{CACHE_PREFIX}:chat:{session_id}"


def _metric_key(bucket: str, outcome: str) -> str:
    return f"{CACHE_METRICS_PREFIX}:{bucket}:{outcome}"


def _hit_rate_percent(hits: int, misses: int) -> float | None:
    total = hits + misses
    if total == 0:
        return None
    return round((hits / total) * 100, 2)


def _cache_header_status(is_hit: bool) -> str:
    return "HIT" if is_hit else "MISS"


async def _record_cache_metric(bucket: str, outcome: str) -> None:
    if outcome not in {"hit", "miss"}:
        return

    await redis_client.incr(_metric_key(bucket, outcome))


async def _get_cached_schema(db: connection.DatabaseManager, db_fp: str) -> tuple[dict, bool]:
    cache_key = _schema_cache_key(db_fp)
    cached_schema = await redis_client.get_json(cache_key)
    if isinstance(cached_schema, dict):
        await _record_cache_metric("schema", "hit")
        return cached_schema, True

    await _record_cache_metric("schema", "miss")

    schema = await db.get_schema()
    await redis_client.set_json(
        cache_key,
        schema,
        ttl_seconds=settings.cache_schema_ttl_seconds,
    )
    return schema, False


async def _get_cached_sql_query(
    question: str,
    schema: dict,
    generator: QueryGenerator,
    db_fp: str,
    dialect: str,
    history_context: dict,
) -> tuple[str, bool, str]:
    signature = _question_signature(question) or _normalize_question_text(question)
    cache_key = _nl2sql_cache_key(db_fp, signature)
    cached_payload = await redis_client.get_json(cache_key)
    if isinstance(cached_payload, dict):
        cached_sql = cached_payload.get("sql_query")
        if isinstance(cached_sql, str) and cached_sql.strip():
            await _record_cache_metric("nl2sql", "hit")
            return cached_sql, True, signature

    await _record_cache_metric("nl2sql", "miss")

    sql_query = await generator.generate_query(
        question=question,
        schema=schema,
        dialect=dialect,
        chat_history_context=history_context,
    )
    await redis_client.set_json(
        cache_key,
        {
            "sql_query": sql_query,
            "question_signature": signature,
            "source_question": question,
        },
        ttl_seconds=settings.cache_nl2sql_ttl_seconds,
    )
    return sql_query, False, signature


async def _get_cached_query_results(
    db: connection.DatabaseManager,
    sql_query: str,
    db_fp: str,
) -> tuple[list[dict], bool]:
    cache_key = _sql_result_cache_key(db_fp, sql_query)
    cached_payload = await redis_client.get_json(cache_key)
    if isinstance(cached_payload, dict):
        cached_data = cached_payload.get("data")
        if isinstance(cached_data, list):
            await _record_cache_metric("sql_results", "hit")
            return cached_data, True

    await _record_cache_metric("sql_results", "miss")

    data = await db.execute_query(sql_query)

    if len(data) <= settings.cache_max_rows:
        await redis_client.set_json(
            cache_key,
            {"data": data},
            ttl_seconds=settings.cache_sql_results_ttl_seconds,
        )

    return data, False


async def _get_cached_summary(
    summarizer: ResponseSummarizer,
    sql_query: str,
    data: list[dict],
    context: str | None,
    db_fp: str,
) -> tuple[str, bool]:
    cache_key = _summary_cache_key(db_fp, sql_query, context)
    cached_payload = await redis_client.get_json(cache_key)
    if isinstance(cached_payload, dict):
        cached_summary = cached_payload.get("summary")
        if isinstance(cached_summary, str) and cached_summary.strip():
            await _record_cache_metric("summary", "hit")
            return cached_summary, True

    await _record_cache_metric("summary", "miss")

    summary = await summarizer.summarize_query_results(
        sql_query=sql_query,
        data=data,
        context=context,
    )

    await redis_client.set_json(
        cache_key,
        {"summary": summary},
        ttl_seconds=settings.cache_summary_ttl_seconds,
    )
    return summary, False


async def _append_chat_cache(
    session_id: str,
    role: str,
    content: str,
    sql_query: str | None = None,
    row_count: int | None = None,
) -> None:
    cache_key = _chat_cache_key(session_id)
    cached_payload = await redis_client.get_json(cache_key)

    messages: list[dict] = []
    if isinstance(cached_payload, dict):
        cached_messages = cached_payload.get("messages")
        if isinstance(cached_messages, list):
            messages = cached_messages

    messages.append(
        {
            "role": role,
            "content": content,
            "sql_query": sql_query,
            "row_count": row_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )

    await redis_client.set_json(
        cache_key,
        {
            "session_id": session_id,
            "messages": messages[-50:],
        },
        ttl_seconds=settings.cache_chat_ttl_seconds,
    )


class DashboardRequest(BaseModel):
    """
    Dashboard generation request
    TODO: Define proper request schema
    """

    description: str
    sketch_url: str | None = None
    additional_comments: str | None = None


class CallbackRequest(BaseModel):
    """
    Backend callback generation request
    TODO: Define proper request schema
    """

    element_id: str
    functionality_description: str


# @router.post("/generate-dashboard")
# async def generate_dashboard(request: DashboardRequest):
#     """
#     Generate dashboard layout code based on user description
#     TODO: Implement GenAI Core integration
#     TODO: Implement Router (LLM) logic
#     TODO: Implement cache checking
#     """
#     # TODO: Check Redis cache first
#     # TODO: If cache miss, use LLM to generate dashboard code
#     # TODO: Store result in cache
#     # TODO: Return generated code

#     return {
#         "status": "TODO",
#         "message": "Dashboard generation not implemented yet",
#         "code": "# TODO: Generate Dash layout code",
#     }


# @router.post("/generate-callback")
# async def generate_callback(request: CallbackRequest):
#     """
#     Generate backend callback for dashboard element
#     TODO: Implement callback generation logic
#     TODO: Implement Query Generator (LLM) if database access needed
#     """
#     # TODO: Analyze functionality description
#     # TODO: Determine if Data Tools or Database access is needed
#     # TODO: Generate appropriate Python callback code
#     # TODO: Cache result

#     return {
#         "status": "TODO",
#         "message": "Callback generation not implemented yet",
#         "code": "# TODO: Generate callback code",
#     }


# TODO: Future router-based endpoint
# @router.post("/ask-advanced")
# async def ask_advanced(question: str):
#     """
#     Advanced GenAI endpoint with Router LLM for Data Tools vs Database decision
#
#     Flow:
#     1. [Optional] Check Redis Cache for similar question
#     2. Router (LLM) decides: Data Tools vs Database query
#     3a. If Data Tools: Execute appropriate Python module
#     3b. If Database: Use ask() endpoint logic
#     4. [Optional] Store result in Redis cache
#
#     TODO: Implement Router (LLM) to decide between Data Tools and Database
#     TODO: Add Redis caching layer
#     TODO: Integrate with Data Tools modules
#     """
#     pass


class GenerateSQLRequest(BaseModel):
    """
    Natural language question for SQL generation
    """

    question: str
    session_id: str | None = None


class GenerateSQLResponse(BaseModel):
    """
    Generated SQL query response
    """

    status: str
    sql_query: str


class AskRequest(BaseModel):
    """
    Natural language question for data analysis
    """

    question: str
    session_id: str | None = None


class AskResponse(BaseModel):
    """
    Complete analysis response with summary
    """

    status: str
    question: str
    sql_query: str
    summary: str
    row_count: int
    session_id: str | None = None


class QueryRequest(BaseModel):
    """
    SQL Query request with optional context
    """

    sql_query: str
    context: str | None = None


class QueryResponse(BaseModel):
    """
    Query response with LLM summary
    """

    status: str
    summary: str
    row_count: int


class DatabaseConnectRequest(BaseModel):
    """
    Postgres / MySQL / SQL server / OracleDB database connect request
    """

    db_type: str
    host: str
    port: int
    username: str
    password: str
    db_name: str
    user_id: str | None = None


async def get_chat_context(session_id: str | None):
    """
    Fetch chat history context for SQL generation
    Returns: (history_text, previous_sql, previous_question, last_successful_sql)
    """
    if not session_id:
        return "", "", "", ""

    session = await chat_history.get_session(session_id)
    if not session or "messages" not in session:
        return "", "", "", ""

    messages = session["messages"]
    
    history_text = "\n".join(
        f"{m.get('role', '').upper()}: {m.get('content', '')}"
        for m in messages[-12:] 
    )

    previous_sql = ""
    previous_question = ""
    
    for m in reversed(messages):
        if not previous_question and m.get("role") == "user":
            previous_question = m.get("content")
        if not previous_sql and m.get("sql_query"):
            previous_sql = m.get("sql_query")

    history_context = {
        "history_text": history_text,
        "previous_sql": previous_sql,
        "previous_question": previous_question
    }
            
    return history_context


@router.post("/new-chat")
async def new_chat(_claims: dict = Depends(validate_token)):
    """
    Create a new chat session
    """
    user_id = _claims.get("sub", "anonymous")

    session_id = await chat_history.create_session(user_id=user_id)

    return {
        "status": "success",
        "session_id": session_id,
        "message": "Chat session created"
    }


@router.post("/generate-sql", response_model=GenerateSQLResponse)
async def generate_sql(
    request: GenerateSQLRequest,
    response: Response,
    _claims: dict = Depends(validate_token),
):
    """
    Generate SQL query from natural language question

    This endpoint:
    1. Takes a natural language question
    2. Retrieves the database schema
    3. Uses GPT-4.1 to generate a valid SQL query
    4. Optionally saves to chat history if session_id provided

    Returns:
        - sql_query: The generated SQL query string
    """
    try:
        db = get_db_manager()
        generator = QueryGenerator()
        db_fp = _db_fingerprint(db)

        schema, schema_hit = await _get_cached_schema(db, db_fp)
        dialect = await db.get_db_dialect()

        history_context = await get_chat_context(request.session_id)

        sql_query, nl2sql_hit, question_signature = await _get_cached_sql_query(
            request.question,
            schema,
            generator,
            db_fp,
            dialect,
            history_context=history_context
        )

        response.headers["X-Cache-Schema"] = _cache_header_status(schema_hit)
        response.headers["X-Cache-NL2SQL"] = _cache_header_status(nl2sql_hit)
        response.headers["X-Cache-NL2SQL-Signature-Hash"] = _short_hash(question_signature)
        response.headers["X-Cache-Trace"] = (
            f"schema={_cache_header_status(schema_hit)};"
            f"nl2sql={_cache_header_status(nl2sql_hit)}"
        )

        if request.session_id:
            try:
                await chat_history.add_message(
                    session_id=request.session_id,
                    role="user",
                    content=request.question,
                )
                await chat_history.add_message(
                    session_id=request.session_id,
                    role="assistant",
                    content="Generating SQL...",
                    sql_query=sql_query
                )
            except Exception as hist_err:
                print(f"Warning: failed to save chat history in generate-sql: {hist_err}")

        return GenerateSQLResponse(status="success", sql_query=sql_query)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating SQL: {str(e)}")


@router.post("/ask", response_model=AskResponse)
async def ask(
    request: AskRequest,
    response: Response,
    _claims: dict = Depends(validate_token),
):
    """
    Returns:
        - question: The original question
        - sql_query: The generated SQL query
        - summary: Natural language summary of results
        - row_count: Number of rows returned
    """
    try:
        db = get_db_manager()
        generator = QueryGenerator()
        summarizer = ResponseSummarizer()
        db_fp = _db_fingerprint(db)

        semantic_probe = await semantic_qa_cache.probe_similar_answer(db_fp, request.question)
        if semantic_probe.best_similarity is not None:
            response.headers["X-Cache-QA-Semantic-Best-Similarity"] = (
                f"{semantic_probe.best_similarity:.4f}"
            )
        response.headers["X-Cache-QA-Semantic-Threshold"] = f"{settings.semantic_cache_threshold:.4f}"

        semantic_hit = semantic_probe.hit
        if semantic_hit is not None:
            await _record_cache_metric("qa_semantic", "hit")
            response.headers["X-Cache-QA-Semantic"] = "HIT"
            response.headers["X-Cache-QA-Semantic-Similarity"] = f"{semantic_hit.similarity:.4f}"
            response.headers["X-Cache-Trace"] = "qa_semantic=HIT"

            if request.session_id:
                try:
                    await chat_history.add_message(
                        session_id=request.session_id,
                        role="user",
                        content=request.question,
                    )
                    await chat_history.add_message(
                        session_id=request.session_id,
                        role="assistant",
                        content=semantic_hit.summary,
                        sql_query=semantic_hit.sql_query,
                        row_count=semantic_hit.row_count,
                    )

                    await _append_chat_cache(
                        session_id=request.session_id,
                        role="user",
                        content=request.question,
                    )
                    await _append_chat_cache(
                        session_id=request.session_id,
                        role="assistant",
                        content=semantic_hit.summary,
                        sql_query=semantic_hit.sql_query,
                        row_count=semantic_hit.row_count,
                    )
                except Exception as hist_err:
                    print(f"Warning: failed to save chat history: {hist_err}")

            return AskResponse(
                status="success",
                question=request.question,
                sql_query=semantic_hit.sql_query,
                summary=semantic_hit.summary,
                row_count=semantic_hit.row_count,
                session_id=request.session_id,
            )

        await _record_cache_metric("qa_semantic", "miss")
        response.headers["X-Cache-QA-Semantic"] = "MISS"

        schema, schema_hit = await _get_cached_schema(db, db_fp)
        dialect = await db.get_db_dialect()

        # Fetch chat context if session_id provided
        history_context = await get_chat_context(request.session_id)

        sql_query, nl2sql_hit, question_signature = await _get_cached_sql_query(
            request.question,
            schema,
            generator,
            db_fp,
            dialect,
            history_context=history_context)

        data, sql_results_hit = await _get_cached_query_results(db, sql_query, db_fp)
        row_count = len(data)

        summary, summary_hit = await _get_cached_summary(
            summarizer=summarizer,
            sql_query=sql_query,
            data=data,
            context=request.question,
            db_fp=db_fp,
        )

        response.headers["X-Cache-Schema"] = _cache_header_status(schema_hit)
        response.headers["X-Cache-NL2SQL"] = _cache_header_status(nl2sql_hit)
        response.headers["X-Cache-SQL-Results"] = _cache_header_status(sql_results_hit)
        response.headers["X-Cache-Summary"] = _cache_header_status(summary_hit)
        response.headers["X-Cache-NL2SQL-Signature-Hash"] = _short_hash(question_signature)
        response.headers["X-Cache-Trace"] = (
            f"qa_semantic=MISS;"
            f"schema={_cache_header_status(schema_hit)};"
            f"nl2sql={_cache_header_status(nl2sql_hit)};"
            f"sql_results={_cache_header_status(sql_results_hit)};"
            f"summary={_cache_header_status(summary_hit)}"
        )

        if request.session_id:
            try:
                await chat_history.add_message(
                    session_id=request.session_id,
                    role="user",
                    content=request.question,
                )
                await chat_history.add_message(
                    session_id=request.session_id,
                    role="assistant",
                    content=summary,
                    sql_query=sql_query,
                    row_count=row_count,
                )

                await _append_chat_cache(
                    session_id=request.session_id,
                    role="user",
                    content=request.question,
                )
                await _append_chat_cache(
                    session_id=request.session_id,
                    role="assistant",
                    content=summary,
                    sql_query=sql_query,
                    row_count=row_count,
                )
            except Exception as hist_err:
                print(f"Warning: failed to save chat history: {hist_err}")

        try:
            await semantic_qa_cache.store_answer(
                db_fp=db_fp,
                question=request.question,
                sql_query=sql_query,
                summary=summary,
                row_count=row_count,
            )
        except Exception as cache_err:
            print(f"Warning: semantic cache store failed: {cache_err}")


        return AskResponse(
            status="success",
            question=request.question,
            sql_query=sql_query,
            summary=summary,
            row_count=row_count,
            session_id=request.session_id,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@router.post("/query-and-summarize", response_model=QueryResponse)
async def query_and_summarize(
    request: QueryRequest,
    response: Response,
    _claims: dict = Depends(validate_token),
):
    """
    Execute SQL query and get LLM summary of the results

    Returns:
        - summary: Natural language description of the data
        - row_count: Total number of rows returned
    """
    try:
        db = get_db_manager()
        summarizer = ResponseSummarizer()
        db_fp = _db_fingerprint(db)

        data, sql_results_hit = await _get_cached_query_results(db, request.sql_query, db_fp)
        row_count = len(data)

        summary, summary_hit = await _get_cached_summary(
            summarizer=summarizer,
            sql_query=request.sql_query,
            data=data,
            context=request.context,
            db_fp=db_fp,
        )

        response.headers["X-Cache-SQL-Results"] = _cache_header_status(sql_results_hit)
        response.headers["X-Cache-Summary"] = _cache_header_status(summary_hit)
        response.headers["X-Cache-Trace"] = (
            f"sql_results={_cache_header_status(sql_results_hit)};"
            f"summary={_cache_header_status(summary_hit)}"
        )

        return QueryResponse(status="success", summary=summary, row_count=row_count)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/connect-database")
async def connect_database(
    request: DatabaseConnectRequest, _claims: dict = Depends(validate_token)
):
    """
    Create connection to database

    Returns:
        - Status of database connection
    """

    valid_db_types = {"postgres", "mysql", "oracle", "sqlserver"}
    db_type = request.db_type

    if db_type not in valid_db_types:
        raise HTTPException(status_code=400,
                            detail=f"Invalid database type: {db_type}")

    try:
        database_url = build_db_connection_url(
            type=request.db_type,
            username=request.username,
            password=request.password,
            host=request.host,
            port=request.port,
            db_name=request.db_name,
        )

        # close old connection (if exists)
        if connection.db_manager:
            await connection.db_manager.disconnect()

        # create new connection
        connection.db_manager = connection.DatabaseManager(
            database_url=database_url,
        )

        await connection.db_manager.connect()

        await redis_client.delete_pattern(f"{CACHE_PREFIX}:schema:*")

        # Create a chat session in MongoDB
        session_id = None
        try:
            user_id = request.user_id or _claims.get("sub", "anonymous")
            session_id = await chat_history.create_session(
                user_id=user_id,
                db_type=request.db_type,
                db_host=request.host,
                db_name=request.db_name,
            )
        except Exception as hist_err:
            print(f"Warning: failed to create chat session: {hist_err}")

        return {
            "status": "success",
            "message": "Database connection established",
            "session_id": session_id,
        }

    except Exception as e:
        connection.db_manager = None
        raise HTTPException(status_code=400, detail=f"Error connecting database: {str(e)}")


class DisconnectRequest(BaseModel):
    session_id: str | None = None


@router.post("/disconnect-database")
async def disconnect_database(
    request: DisconnectRequest = None,
    _claims: dict = Depends(validate_token),
):
    """
    Remove database connection

    Returns:
        - Status of database disconnection
    """
    try:
        # close old connection (if exists)
        if connection.db_manager:
            await connection.db_manager.disconnect()
            connection.db_manager = None

            await redis_client.delete_pattern(f"{CACHE_PREFIX}:schema:*")

            if request and request.session_id:
                try:
                    await chat_history.close_session(request.session_id)
                except Exception as hist_err:
                    print(f"Warning: failed to close chat session: {hist_err}")

            return {
                "status": "success",
                "message": "Database disconnected",
            }
        else:
            return {
                "message": "Database connection was not established - disconnection not possible",
            }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error disconnecting database: {str(e)}")


@router.get("/schema")
async def schema(response: Response, _claims: dict = Depends(validate_token)):
    if not connection.db_manager:
        return {"status": "not connected", "message": "Database is not connected."}
    try:
        db_fp = _db_fingerprint(connection.db_manager)
        schema, schema_hit = await _get_cached_schema(connection.db_manager, db_fp)
        response.headers["X-Cache-Schema"] = _cache_header_status(schema_hit)
        response.headers["X-Cache-Trace"] = f"schema={_cache_header_status(schema_hit)}"
        return schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schema: {str(e)}")


@router.get("/cache-stats")
async def cache_stats(_claims: dict = Depends(validate_token)):
    if not redis_client.is_connected():
        return {
            "status": "redis_unavailable",
            "redis_connected": False,
            "message": "Redis is not connected.",
        }

    bucket_stats: dict[str, dict] = {}
    total_hits = 0
    total_misses = 0

    for bucket in CACHE_METRIC_BUCKETS:
        hits = await redis_client.get_int(_metric_key(bucket, "hit")) or 0
        misses = await redis_client.get_int(_metric_key(bucket, "miss")) or 0

        total_hits += hits
        total_misses += misses

        bucket_stats[bucket] = {
            "hits": hits,
            "misses": misses,
            "hit_rate_percent": _hit_rate_percent(hits, misses),
        }

    bucket_stats["total"] = {
        "hits": total_hits,
        "misses": total_misses,
        "hit_rate_percent": _hit_rate_percent(total_hits, total_misses),
    }

    key_counts = {
        "schema": await redis_client.count_pattern(f"{CACHE_PREFIX}:schema:*"),
        "nl2sql": await redis_client.count_pattern(f"{CACHE_PREFIX}:nl2sql:*"),
        "sql_results": await redis_client.count_pattern(f"{CACHE_PREFIX}:sqlres:*"),
        "summary": await redis_client.count_pattern(f"{CACHE_PREFIX}:summary:*"),
        "qa_entries": await redis_client.count_pattern(f"{CACHE_PREFIX}:qa:entry:*"),
        "qa_indexes": await redis_client.count_pattern(f"{CACHE_PREFIX}:qa:index:*"),
        "chat": await redis_client.count_pattern(f"{CACHE_PREFIX}:chat:*"),
        "metrics": await redis_client.count_pattern(f"{CACHE_METRICS_PREFIX}:*"),
    }

    return {
        "status": "success",
        "redis_connected": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stats": bucket_stats,
        "key_counts": key_counts,
    }


@router.get("/history/{session_id}")
async def get_session_history(
    session_id: str,
    response: Response,
    _claims: dict = Depends(validate_token),
):
    cache_key = _chat_cache_key(session_id)
    cached_session = await redis_client.get_json(cache_key)
    if isinstance(cached_session, dict):
        await _record_cache_metric("chat_history", "hit")
        response.headers["X-Cache-Chat-History"] = "HIT"
        response.headers["X-Cache-Trace"] = "chat_history=HIT"
        return cached_session

    await _record_cache_metric("chat_history", "miss")

    session = await chat_history.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await redis_client.set_json(
        cache_key,
        session,
        ttl_seconds=settings.cache_chat_ttl_seconds,
    )
    response.headers["X-Cache-Chat-History"] = "MISS"
    response.headers["X-Cache-Trace"] = "chat_history=MISS"
    return session


@router.get("/sessions")
async def list_sessions(_claims: dict = Depends(validate_token)):
    user_id = _claims.get("sub", "anonymous")
    sessions = await chat_history.list_user_sessions(user_id)
    return {"sessions": sessions}

@router.get("/mongo/sessions")
async def get_mongo_sessions(_claims: dict = Depends(validate_token)):
    try:
        db = get_db()
        collection = db["sessions"]
        user_id = _claims.get("sub", "anonymous")
        cursor = collection.find(
            {"user_id": user_id},
            {
                "_id": 1,
                "session_id": 1,
                "user_id": 1,
                "db_type": 1,
                "db_host": 1,
                "db_name": 1,
                "connected_at": 1,
                "disconnected_at": 1,
                "messages": 1,
            }
        ).sort("connected_at", -1)

        def format_message(msg: dict) -> dict:
            return {
                "role": msg.get("role"),
                "content": msg.get("content"),
                "sql_query": msg.get("sql_query"),
                "row_count": msg.get("row_count"),
                "timestamp": msg.get("timestamp"),
            }

        sessions = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            raw_messages = doc.get("messages", [])
            doc["messages"] = [format_message(m) for m in raw_messages if m]
            sessions.append(doc)

        return {
            "status": "success",
            "user_id": user_id,
            "count": len(sessions),
            "sessions": sessions
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Mongo sessions fetch failed: {str(e)}"
        )
