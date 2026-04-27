# connection urls

def build_db_connection_url(
        type: str,
        username: str,
        password: str,
        host: str,
        port: int,
        db_name: str,
) -> str:
    if type == "postgres":
        return f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}"
    if type == "mysql":
        return f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}"
    if type == "sqlserver":
        return f"mssql+pyodbc://{username}:{password}@{host}:{port}/{db_name}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&ApplicationIntent=ReadOnly"
    if type == "oracle":
        return f"oracle+oracledb://{username}:{password}@{host}:{port}?service_name={db_name}"
    else:
        # ZLE - OPRAVIT bud ENUM alebo neviem co
        return "bad"