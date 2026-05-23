# connection urls

from urllib.parse import quote_plus

def build_db_connection_url(
    type: str,
    username: str,
    password: str,
    host: str,
    port: int,
    db_name: str,
) -> str:

    u = quote_plus(username)
    p = quote_plus(password)

    if type == "postgres":
        return f"postgresql+psycopg2://{u}:{p}@{host}:{port}/{db_name}"
    if type == "mysql":
        return f"mysql+pymysql://{u}:{p}@{host}:{port}/{db_name}"
    if type == "sqlserver":
        return f"mssql+pyodbc://{u}:{p}@{host}:{port}/{db_name}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&ApplicationIntent=ReadOnly"
    if type == "oracle":
        return f"oracle+oracledb://{u}:{p}@{host}:{port}?service_name={db_name}"
    else:
        raise ValueError(f"Unsupported database type: {type}")
