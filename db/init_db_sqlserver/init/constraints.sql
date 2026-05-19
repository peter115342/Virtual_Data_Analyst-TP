USE BikeStoresDB;
GO

ALTER TABLE products
ADD CONSTRAINT FK_products_categories
FOREIGN KEY (category_id) REFERENCES categories(category_id);

ALTER TABLE products
ADD CONSTRAINT FK_products_brands
FOREIGN KEY (brand_id) REFERENCES brands(brand_id);

ALTER TABLE staffs
ADD CONSTRAINT FK_staffs_stores
FOREIGN KEY (store_id) REFERENCES stores(store_id);

ALTER TABLE staffs
ADD CONSTRAINT FK_staffs_staffs
FOREIGN KEY (manager_id) REFERENCES staffs(staff_id);

ALTER TABLE orders
ADD CONSTRAINT FK_orders_customers
FOREIGN KEY (customer_id) REFERENCES customers(customer_id);

ALTER TABLE orders
ADD CONSTRAINT FK_orders_stores
FOREIGN KEY (store_id) REFERENCES stores(store_id);

ALTER TABLE orders
ADD CONSTRAINT FK_orders_staffs
FOREIGN KEY (staff_id) REFERENCES staffs(staff_id);

ALTER TABLE order_items
ADD CONSTRAINT FK_orderitems_orders
FOREIGN KEY (order_id) REFERENCES orders(order_id);

ALTER TABLE order_items
ADD CONSTRAINT FK_orderitems_products
FOREIGN KEY (product_id) REFERENCES products(product_id);

ALTER TABLE stocks
ADD CONSTRAINT FK_stocks_stores
FOREIGN KEY (store_id) REFERENCES stores(store_id);

ALTER TABLE stocks
ADD CONSTRAINT FK_stocks_products
FOREIGN KEY (product_id) REFERENCES products(product_id);