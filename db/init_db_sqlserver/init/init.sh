#!/bin/bash

echo " Waiting for SQL Server..."

until /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$SA_PASSWORD" -C -Q "SELECT 1" > /dev/null 2>&1
do
  echo "SQL Server not ready yet..."
  sleep 2
done

echo "SQL Server is ready"

echo "Running schema.sql"
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$SA_PASSWORD" -C -i /init/schema.sql

echo "Loading CSV data"
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$SA_PASSWORD" -C -i /init/data.sql

echo "Running constraints.sql"
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$SA_PASSWORD" -C -i /init/constraints.sql

echo " DONE"