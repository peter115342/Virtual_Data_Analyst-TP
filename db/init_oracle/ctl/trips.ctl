OPTIONS (SKIP=1)
LOAD DATA
INFILE '/container-entrypoint-initdb.d/data/trips.csv'
INTO TABLE appuser.trips
FIELDS TERMINATED BY ','
(
    trip_id,
    load_id,
    driver_id,
    truck_id,
    trailer_id,
    dispatch_date DATE "YYYY-MM-DD",
    actual_distance_miles,
    actual_duration_hours,
    fuel_gallons_used,
    average_mpg,
    idle_time_hours,
    trip_status
)