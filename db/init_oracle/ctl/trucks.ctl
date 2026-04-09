OPTIONS (SKIP=1)
LOAD DATA
INFILE '/container-entrypoint-initdb.d/data/trucks.csv'
INTO TABLE trucks
FIELDS TERMINATED BY ','
(
    truck_id,
    unit_number,
    make,
    model_year,
    vin,
    acquisition_date DATE "YYYY-MM-DD",
    acquisition_mileage,
    fuel_type,
    tank_capacity_gallons,
    status,
    home_terminal
)