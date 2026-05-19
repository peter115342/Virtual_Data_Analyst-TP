OPTIONS (SKIP=1)
LOAD DATA
INFILE '/container-entrypoint-initdb.d/data/drivers.csv'
INTO TABLE drivers
FIELDS TERMINATED BY ','
(
    driver_id,
    first_name,
    last_name,
    hire_date DATE "YYYY-MM-DD",
    termination_date DATE "YYYY-MM-DD",
    license_number,
    license_state,
    date_of_birth DATE "YYYY-MM-DD",
    home_terminal,
    employment_status,
    cdl_class,
    years_experience
)