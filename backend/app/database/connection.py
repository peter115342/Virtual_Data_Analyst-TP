# TODO: Implement PostgreSQL connection with READ-ONLY access


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DatabaseManager:
    def __init__(self, database_url: str, readonly: bool = True):
        """
        TODO: Initialize database connection
        TODO: Ensure read-only mode is enforced
        """
        self.readonly = readonly
        self.engine = None
        self.session_maker = None

    async def connect(self):
        """
        TODO: Establish database connection
        TODO: Configure for read-only if readonly=True
        """
        pass

    async def disconnect(self):
        """
        TODO: Close database connection
        """
        pass

    async def execute_query(self, sql: str) -> list[dict]:
        """
        Execute SQL query (read-only)

        TODO: Implement query execution
        TODO: Add safety checks to prevent write operations
        TODO: Return results as list of dictionaries
        """
        pass

    async def get_schema(self) -> dict:
        """
        Get database schema for LLM context

        TODO: Query information_schema
        TODO: Return formatted schema information
        """
        pass
