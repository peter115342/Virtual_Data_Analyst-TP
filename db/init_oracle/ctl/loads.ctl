OPTIONS (SKIP=1)
LOAD DATA
INFILE '/container-entrypoint-initdb.d/data/loads.csv'
INTO TABLE appuser.loads
FIELDS TERMINATED BY ','
(
    load_id,
    customer_id,
    route_id,
    load_date DATE "YYYY-MM-DD",
    load_type,
    weight_lbs,
    pieces,
    revenue,
    fuel_surcharge,
    accessorial_charges,
    load_status,
    booking_type
)