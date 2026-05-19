OPTIONS (SKIP=1)
LOAD DATA
INFILE '/container-entrypoint-initdb.d/data/trailers.csv'
INTO TABLE trailers
FIELDS TERMINATED BY ','
(
    trailer_id,
    trailer_number,
    trailer_type,
    length_feet,
    model_year,
    vin,
    acquisition_date DATE "YYYY-MM-DD",
    status,
    current_location
)