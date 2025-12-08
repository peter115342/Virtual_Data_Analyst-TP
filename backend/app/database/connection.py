# PostgreSQL connection with READ-ONLY access


import re

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


class DatabaseManager:
    def __init__(self, database_url: str, readonly: bool = True):
        """
        Initialize database connection
        Ensure read-only mode is enforced
        """
        self.readonly = readonly
        self.database_url = database_url
        self.engine = None
        self.session_maker = None

    async def connect(self):
        """
        Establish database connection
        Configure for read-only if readonly=True
        """
        self.engine = create_engine(
            self.database_url, pool_size=5, max_overflow=10, pool_pre_ping=True, echo=False
        )

        self.session_maker = sessionmaker(bind=self.engine)

        with self.engine.connect() as conn:
            if self.readonly:
                conn.execute(text("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY"))
            conn.execute(text("SELECT 1"))

    async def disconnect(self):
        """
        Close database connection
        """
        if self.engine:
            self.engine.dispose()

    async def execute_query(self, sql: str) -> list[dict]:
        """
        Execute SQL query (read-only)
        Add safety checks to prevent write operations
        Return results as list of dictionaries
        """
        if not self.engine:
            raise RuntimeError("Database not connected. Call connect() first.")

        if self.readonly:
            dangerous_keywords = [
                r"\bINSERT\b",
                r"\bUPDATE\b",
                r"\bDELETE\b",
                r"\bDROP\b",
                r"\bCREATE\b",
                r"\bALTER\b",
                r"\bTRUNCATE\b",
                r"\bGRANT\b",
                r"\bREVOKE\b",
            ]
            for keyword in dangerous_keywords:
                if re.search(keyword, sql, re.IGNORECASE):
                    raise ValueError("Write operation not allowed in read-only mode")

        with self.engine.connect() as conn:
            if self.readonly:
                conn.execute(text("SET TRANSACTION READ ONLY"))

            result = conn.execute(text(sql))

            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]

            return rows

    async def get_schema(self) -> dict:
        """
        Get database schema for LLM context
        Query information_schema
        Return formatted schema information
        """
        if not self.engine:
            raise RuntimeError("Database not connected. Call connect() first.")

        schema_query = """
        SELECT
            table_name,
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
        """

        rows = await self.execute_query(schema_query)

        schema = {}
        for row in rows:
            table = row["table_name"]
            if table not in schema:
                schema[table] = []
            schema[table].append(
                {
                    "column": row["column_name"],
                    "type": row["data_type"],
                    "nullable": row["is_nullable"] == "YES",
                }
            )

        return schema


db_manager: DatabaseManager | None = None


def get_db_manager() -> DatabaseManager:
    """Dependency to get database manager instance"""
    if db_manager is None:
        raise RuntimeError("Database manager not initialized")
    return db_manager
