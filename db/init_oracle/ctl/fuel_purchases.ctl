OPTIONS (SKIP=1)
LOAD DATA
INFILE '/container-entrypoint-initdb.d/data/fuel_purchases.csv'
INTO TABLE fuel_purchases
FIELDS TERMINATED BY ','
(
    fuel_purchase_id,
    trip_id,
    truck_id,
    driver_id,
    purchase_datetime "TO_TIMESTAMP(:purchase_datetime, 'YYYY-MM-DD HH24:MI:SS')",
    location_city,
    location_state,
    gallons,
    price_per_gallon,
    total_cost,
    fuel_card_number
)