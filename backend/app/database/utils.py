# connection urls

def build_postgres_url(
        username: str,
        password: str,
        host: str,
        port: int,
        db_name: str,
) -> str:
    return f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}"

def build_mysql_url(
        username: str,
        password: str,
        host: str,
        port: int, # 3306
        db_name: str,
) -> str:
    return f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}"