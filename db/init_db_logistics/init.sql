
CREATE DATABASE logistics_operations;
GO

USE logistics_operations;
GO

CREATE TABLE trucks (
    Id INT,
    Name VARCHAR(100),
);
GO

BULK INSERT trucks
FROM '/csv/trucks.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    TABLOCK
)
GO