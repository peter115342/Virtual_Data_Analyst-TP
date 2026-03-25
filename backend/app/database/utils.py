# connection urls

# def build_postgres_url(
#         username: str,
#         password: str,
#         host: str,
#         port: int,
#         db_name: str,
# ) -> str:
#     return f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}"
#
# def build_mysql_url(
#         username: str,
#         password: str,
#         host: str,
#         port: int, # 3306
#         db_name: str,
# ) -> str:
#     return f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}"

# def build_mssql_url(
#         username: str,
#         password: str,
#         host: str,
#         port: int,
#         db_name: str,
# ) -> str:
#     return f"mssql+pyodbc://{username}:{password}@{host}:{port}/{db_name}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"


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
    else:
        # ZLE - OPRAVIT bud ENUM alebo neviem co
        return "bad"