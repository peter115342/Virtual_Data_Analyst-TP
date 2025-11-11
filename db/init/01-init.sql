-- SQL Initialization Script
CREATE TABLE events (
    event_id BIGSERIAL PRIMARY KEY,
    event_time TIMESTAMP NOT NULL,            
    event_type VARCHAR(20) NOT NULL CHECK (event_type IN ('view','cart','remove_from_cart','purchase')),
    product_id BIGINT NOT NULL,               
    category_id BIGINT,                       
    category_code VARCHAR(255),               
    brand VARCHAR(255),                       
    price NUMERIC(10, 2),                     
    user_id BIGINT NOT NULL,                  
    user_session VARCHAR(100)                 
);

-- Indexy pre rýchle vyhľadávanie
CREATE INDEX idx_event_time ON events(event_time);
CREATE INDEX idx_event_type ON events(event_type);
CREATE INDEX idx_product_id ON events(product_id);
CREATE INDEX idx_user_id ON events(user_id);
CREATE INDEX idx_category_code ON events(category_code);

-- Download the CSV file from Kaggle and save it in db/init/ as 2019Nov_clean_small.csv
-- Dataset from Kaggle: https://www.kaggle.com/datasets/mkechinov/ecommerce-behavior-data-from-multi-category-store
COPY events(
    event_time, event_type, product_id, category_id,
    category_code, brand, price, user_id, user_session
)
FROM '/docker-entrypoint-initdb.d/2019Nov_clean_small.csv'
DELIMITER ','
CSV HEADER;
