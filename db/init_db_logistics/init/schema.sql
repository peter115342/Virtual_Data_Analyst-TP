CREATE TABLE customers (
    ID INT PRIMARY KEY,
    Name NVARCHAR(100)
);

CREATE TABLE delivery_events (
    ID INT PRIMARY KEY,
    Amount DECIMAL(10,2)
);

CREATE TABLE driver_monthly_metrics (
    ID INT PRIMARY KEY,
);

CREATE TABLE drivers (
    ID INT PRIMARY KEY,
);

CREATE TABLE facilities (
    ID INT PRIMARY KEY,
);

CREATE TABLE fuel_purchases (
    ID INT PRIMARY KEY,
);

CREATE TABLE loads (
    ID INT PRIMARY KEY,
);

CREATE TABLE maintenance_records (
    ID INT PRIMARY KEY,
);

CREATE TABLE routes (
    ID INT PRIMARY KEY,
);

CREATE TABLE safety_incidents (
    ID INT PRIMARY KEY,
);

CREATE TABLE trailers (
    ID INT PRIMARY KEY,
);

CREATE TABLE trips (
    ID INT PRIMARY KEY,
);

CREATE TABLE truck_utilization_metrics (
    ID INT PRIMARY KEY,
);

CREATE TABLE trucks (
    ID INT PRIMARY KEY,
);