-- SQL Initialization Script
CREATE TABLE events (
    event_id BIGSERIAL PRIMARY KEY,
    event_time TIMESTAMP NOT NULL,            -- čas udalosti (UTC)
    event_type VARCHAR(20) NOT NULL CHECK (event_type IN ('view','cart','remove_from_cart','purchase')),
    product_id BIGINT NOT NULL,               -- ID produktu
    category_id BIGINT,                       -- ID kategórie
    category_code VARCHAR(255),               -- názov kategórie, ak existuje
    brand VARCHAR(255),                       -- značka produktu, ak existuje
    price NUMERIC(10, 2),                     -- cena produktu
    user_id BIGINT NOT NULL,                  -- ID používateľa
    user_session VARCHAR(100)                 -- session ID používateľa
);


-- Indexy pre rýchle vyhľadávanie
CREATE INDEX idx_event_time ON events(event_time);
CREATE INDEX idx_event_type ON events(event_type);
CREATE INDEX idx_product_id ON events(product_id);
CREATE INDEX idx_user_id ON events(user_id);
CREATE INDEX idx_category_code ON events(category_code);
