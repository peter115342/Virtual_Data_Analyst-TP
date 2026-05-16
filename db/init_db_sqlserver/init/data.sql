USE BikeStoresDB;
GO

BULK INSERT categories
FROM '/csv/categories.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\r\n',
    ERRORFILE = '/csv/log/categories_errors.log'
);
GO

BULK INSERT brands
FROM '/csv/brands.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\r\n',
    ERRORFILE = '/csv/log/brands_errors.log'
);
GO

BULK INSERT products
FROM '/csv/products.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    ERRORFILE = '/csv/log/products_errors.log'
);
GO

BULK INSERT stores
FROM '/csv/stores.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    ERRORFILE = '/csv/log/stores_errors.log'
);
GO

BULK INSERT staffs
FROM '/csv/staffs.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    ERRORFILE = '/csv/log/staffs_errors.log'
);
GO

BULK INSERT customers
FROM '/csv/customers.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    ERRORFILE = '/csv/log/customers_errors.log'
);
GO

BULK INSERT orders
FROM '/csv/orders.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    ERRORFILE = '/csv/log/orders_errors.log'
);
GO

BULK INSERT order_items
FROM '/csv/order_items.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    ERRORFILE = '/csv/log/orderitems_errors.log'
);
GO

BULK INSERT stocks
FROM '/csv/stocks.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    ERRORFILE = '/csv/log/stocks_errors.log'
);
GO