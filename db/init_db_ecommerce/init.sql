-- Create Schema
CREATE DATABASE IF NOT EXISTS ecommerce_analytics;

-- TABLES
-- =====================================================
CREATE TABLE campaigns(
    campaign_id INT PRIMARY KEY,
    channel VARCHAR(50),
    objective VARCHAR(50),
    start_date DATE,
    end_date DATE,
    target_segment VARCHAR(100),
    expected_uplift DECIMAL(6,4)
);

CREATE TABLE customers(
    customer_id INT PRIMARY KEY,
    signup_date DATE,
    country CHAR(2),
    age INT,
    gender VARCHAR(10),
    loyalty_tier VARCHAR(20),
    acquisition_channel VARCHAR(50)
);

CREATE TABLE products(
    product_id INT PRIMARY KEY,
    category VARCHAR(100),
    brand VARCHAR(100),
    base_price DECIMAL(10,2),
    launch_date DATE,
    is_premium BOOLEAN,
);

CREATE TABLE events(
    event_id INT PRIMARY KEY,
    event_timestamp DATETIME,
    customer_id INT,
    session_id BIGINT,
    event_type VARCHAR(50),
    product_id INT,
    device_type VARCHAR(50),
    traffic_source VARCHAR(50),
    campaign_id INT,
    page_category VARCHAR(30),
    session_duration_sec DECIMAL(10,2),
    experiment_group VARCHAR(20)
);

CREATE TABLE transactions(
    transaction_id INT PRIMARY KEY,
    transaction_timestamp DATETIME,
    customer_id INT,
    product_id INT,
    quantity INT,
    discount_applied DECIMAL(5,2),
    gross_revenue DECIMAL(10,2),
    refund_flag BOOLEAN
);

-- INDEXES FOR PERFORMANCE
-- =====================================================
CREATE INDEX idx_events_customer ON events(customer_id);
CREATE INDEX idx_events_product ON events(product_id);
CREATE INDEX idx_events_campaign ON events(campaign_id);

CREATE INDEX idx_transaction_customer ON transactions(customer_id);
CREATE INDEX idx_transactions_product ON transactions(product_id);

-- LOAD DATA FROM CSV FILES
-- =====================================================
LOAD DATA INFILE '/docker-entrypoint-initdb.d/campaigns.csv'
INTO TABLE campaigns
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE '/docker-entrypoint-initdb.d/customers.csv'
INTO TABLE customers
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE '/docker-entrypoint-initdb.d/events.csv'
INTO TABLE events
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(event_id,
event_timestamp,
customer_id,
session_id,
event_type,
@product_id,
device_type,
traffic_source,
campaign_id,
page_category,
session_duration_sec,
experiment_group)
SET product_id = CAST(@product_id AS UNSIGNED);

LOAD DATA INFILE '/docker-entrypoint-initdb.d/products.csv'
INTO TABLE products
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE '/docker-entrypoint-initdb.d/transactions.csv'
INTO TABLE transactions
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(transaction_id,
transaction_timestamp,
customer_id,
@product_id,
quantity,
discount_applied,
gross_revenue,
campaign_id,
refund_flag)
SET product_id = CAST(@product_id AS UNSIGNED);;