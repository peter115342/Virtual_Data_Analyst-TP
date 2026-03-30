OPTIONS (SKIP=1)
LOAD DATA
INFILE '/container-entrypoint-initdb.d/data/maintenance_records.csv'
INTO TABLE appuser.maintenance_records
FIELDS TERMINATED BY ','
(
    maintenance_id,
    truck_id,
    maintenance_date DATE "YYYY-MM-DD",
    maintenance_type,
    odometer_reading,
    labor_hours,
    labor_cost,
    parts_cost,
    total_cost,
    facility_location,
    downtime_hours,
    service_description
)