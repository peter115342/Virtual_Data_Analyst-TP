# PostgreSQL connection with READ-ONLY access


import re

from sqlalchemy import create_engine, text, inspect, select, literal
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
                dialect = self.engine.dialect.name

                if dialect == "postgresql":
                    conn.execute(text(
                        "SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY"))
                elif dialect == "mysql":
                    conn.execute(text("SET SESSION TRANSACTION READ ONLY"))
                elif dialect == "mssql":
                    # TODO Read-only is not fully implemented
                    pass
                elif dialect == "oracle":
                    conn.execute(text("SET TRANSACTION READ ONLY"))
                else:
                    raise ValueError(f"Unsupported database dialect {dialect}")

            # conn.execute(text("SELECT 1"))
            conn.execute(select(literal(1)))

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

        inspector = inspect(self.engine)

        schema = {}
        for table_name in inspector.get_table_names():
            columns_info = inspector.get_columns(table_name)
            schema[table_name] = [
                {
                    "column": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                }
                for col in columns_info
            ]

        return schema


db_manager: DatabaseManager | None = None


def get_db_manager() -> DatabaseManager:
    """Dependency to get database manager instance"""
    if db_manager is None:
        raise RuntimeError("Database manager not initialized")
    return db_manager
