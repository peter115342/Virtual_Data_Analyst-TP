"""
Main API Routes
TODO: Implement API endpoints according to architecture
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.auth.entra import validate_token
from app.database.connection import get_db_manager
from app.genai_core.query_generator import QueryGenerator
from app.genai_core.response_summarizer import ResponseSummarizer
from app.database.utils import build_db_connection_url
from app.database import connection, chat_history
from app.database.mongo import get_db

router = APIRouter(prefix="/api", tags=["api"])


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
    Postgres / MySQL database connect request
    """

    db_type: str
    host: str
    port: int
    username: str
    password: str
    db_name: str
    user_id: str | None = None

async def get_chat_context(session_id: str | None):
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
    last_successful_sql = ""
    
    for m in reversed(messages):
        if not previous_question and m.get("role") == "user":
            previous_question = m.get("content")
        if not previous_sql and m.get("sql_query"):
            previous_sql = m.get("sql_query")
        if not last_successful_sql and m.get("sql_query") and m.get("success"):
            last_successful_sql = m.get("sql_query")
            
    return history_text, previous_sql, previous_question, last_successful_sql

@router.post("/new-chat")
async def new_chat(_claims: dict = Depends(validate_token)):
    user_id = _claims.get("sub", "anonymous")

    session_id = await chat_history.create_session(user_id=user_id)

    return {
        "status": "success",
        "session_id": session_id,
        "message": "Kontext is empty."
    }


@router.post("/generate-sql", response_model=GenerateSQLResponse)
async def generate_sql(request: GenerateSQLRequest, _claims: dict = Depends(validate_token)):
    """
    Generate SQL query from natural language question

    This endpoint:
    1. Takes a natural language question
    2. Retrieves the database schema
    3. Uses GPT-4.1 to generate a valid SQL query

    Returns:
        - sql_query: The generated SQL query string
    """
    try:
        db = get_db_manager()
        generator = QueryGenerator()

        schema = await db.get_schema()
        history_text, previous_sql, previous_question, last_successful_sql = await get_chat_context(request.session_id)

        sql_query = await generator.generate_query( 
            question=request.question,  
            schema=schema,  
            history_text=history_text,  
            previous_sql=previous_sql,  
            previous_question=previous_question,
            last_successful_sql=last_successful_sql,   
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
                    sql_query=sql_query,
                    success=None  
                )
            except Exception as hist_err:
                print(f"Warning: failed to save chat history in generate-sql: {hist_err}")
        return GenerateSQLResponse(status="success", sql_query=sql_query)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating SQL: {str(e)}")


@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest, _claims: dict = Depends(validate_token)):
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

        schema = await db.get_schema()

        history_text, previous_sql, previous_question, last_successful_sql = await get_chat_context(request.session_id)  

        sql_query = await generator.generate_query(  
            question=request.question,  
            schema=schema,  
            history_text=history_text,  
            previous_sql=previous_sql,  
            previous_question=previous_question,
            last_successful_sql=last_successful_sql  
        )  
        data = []
        execution_success = False
        try:
            data = await db.execute_query(sql_query)
            execution_success = True
        except Exception as sql_err:
            print(f"SQL failed: {sql_err}")
        row_count = len(data)

        summary = await summarizer.summarize_query_results(
            sql_query=sql_query, data=data, context=request.question
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
                    success=execution_success,
                )
            except Exception as hist_err:
                print(f"Warning: failed to save chat history: {hist_err}")

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
async def query_and_summarize(request: QueryRequest, _claims: dict = Depends(validate_token)):
    """
    Execute SQL query and get LLM summary of the results

    Returns:
        - summary: Natural language description of the data
        - row_count: Total number of rows returned
    """
    try:
        db = get_db_manager()
        summarizer = ResponseSummarizer()

        data = await db.execute_query(request.sql_query)
        row_count = len(data)

        summary = await summarizer.summarize_query_results(
            sql_query=request.sql_query, data=data, context=request.context
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
async def schema(_claims: dict = Depends(validate_token)):
    if not connection.db_manager:
        return {"status": "not connected", "message": "Database is not connected."}
    try:
        schema = await connection.db_manager.get_schema()
        return schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schema: {str(e)}")


@router.get("/history/{session_id}")
async def get_session_history(session_id: str, _claims: dict = Depends(validate_token)):
    session = await chat_history.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
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
