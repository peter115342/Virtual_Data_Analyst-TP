#!/bin/bash

SA_PASSWORD = ${MSSQL_SA_PASSWORD:-example_password}

echo " Waiting for SQL Server..."
sleep 20

echo " Creating database..."

/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -Q "
IF DB_ID('LogisticsDB') IS NULL
CREATE DATABASE LogisticsDB;
"

echo " Creating schema (tables without FK)..."

/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -d LogisticsDB -i /init/schema.sql

echo " Importing CSV data..."

for file in /csv/*.csv
do
  filename=$(basename "$file")
  tablename="${filename%.*}"

  echo " Importing $tablename"

  /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -d LogisticsDB -Q "
  BULK INSERT [$tablename]
  FROM '/csv/$filename'
  WITH (
      FIRSTROW = 2,
      FIELDTERMINATOR = ',',
      ROWTERMINATOR = '\n',
      TABLOCK,
      CODEPAGE = '65001'
  );
  "
done

echo " Adding foreign keys and constraints..."

/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -d LogisticsDB -i /init/constraints.sql

echo " DONE"