CREATE DATABASE BikeStoresDB;
GO

USE BikeStoresDB;
GO


CREATE TABLE categories (
    category_id INT PRIMARY KEY,
    category_name NVARCHAR(255) NOT NULL
);

CREATE TABLE brands (
    brand_id INT PRIMARY KEY,
    brand_name NVARCHAR(255) NOT NULL
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name NVARCHAR(255) NOT NULL,
    brand_id INT NOT NULL,
    category_id INT NOT NULL,
    model_year SMALLINT NOT NULL,
    list_price DECIMAL(10,2) NOT NULL
);

CREATE TABLE stores (
    store_id INT PRIMARY KEY,
    store_name NVARCHAR(255) NOT NULL,
    phone NVARCHAR(25),
    email NVARCHAR(255),
    street NVARCHAR(255),
    city NVARCHAR(255),
    state NVARCHAR(10),
    zip_code INT
);

CREATE TABLE staffs (
    staff_id INT PRIMARY KEY,
    first_name NVARCHAR(50) NOT NULL,
    last_name NVARCHAR(50) NOT NULL,
    email NVARCHAR(255) NOT NULL UNIQUE,
    phone NVARCHAR(25),
    active BIT NOT NULL,
    store_id INT NOT NULL,
    manager_id INT NULL
);

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    first_name NVARCHAR(255) NOT NULL,
    last_name NVARCHAR(255) NOT NULL,
    email NVARCHAR(255) NOT NULL,
    street NVARCHAR(255),
    city NVARCHAR(50),
    state NVARCHAR(25),
    zip_code INT
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_status SMALLINT NOT NULL,
    order_date DATE NOT NULL,
    required_date DATE NOT NULL,
    shipped_date DATE,
    store_id INT NOT NULL,
    staff_id INT NOT NULL
);

CREATE TABLE order_items (
    order_id INT,
    item_id INT,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    list_price DECIMAL(10,2) NOT NULL,
    discount DECIMAL(4,2) NOT NULL DEFAULT 0,
    PRIMARY KEY (order_id, item_id)
);

CREATE TABLE stocks (
    store_id INT,
    product_id INT,
    quantity INT,
    PRIMARY KEY (store_id, product_id),
);

