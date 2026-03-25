#!/bin/bash

echo " Waiting for SQL Server..."

for i in {1..40}; do
  /opt/mssql-tools/bin/sqlcmd -S db -U sa -P "$SA_PASSWORD" -Q "SELECT 1" > /dev/null 2>&1 && break
  echo " SQL Server not ready yet..."
  sleep 2
done

echo " Creating schema (tables without FK)..."

/opt/mssql-tools/bin/sqlcmd -S db -U sa -P $SA_PASSWORD -i /init/schema.sql

echo " Importing CSV data..."

for file in /csv/*.csv
do
  filename=$(basename "$file")
  tablename="${filename%.*}"

  echo " Importing table: $tablename"

  /opt/mssql-tools/bin/sqlcmd -S db -U sa -P $SA_PASSWORD -d LogisticsDB -Q "
  BULK INSERT [$tablename]
  FROM '/csv/$filename'
  WITH (
      FIRSTROW = 2,
      FIELDTERMINATOR = ',',
      ROWTERMINATOR = '0x0a',
      TABLOCK,
      CODEPAGE = '65001'
  );
  "
done

echo " Adding foreign keys and constraints..."

/opt/mssql-tools/bin/sqlcmd -S db -U sa -P $SA_PASSWORD -d LogisticsDB -i /init/constraints.sql

echo " DONE"