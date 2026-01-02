# connection urls

def build_postgres_url(
        username: str,
        password: str,
        host: str,
        port: int,
        database: str,
) -> str:
    return f"postgresql://{username}:{password}@{host}:{port}/{database}"

# def build_mysql_url()