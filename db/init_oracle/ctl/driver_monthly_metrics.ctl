OPTIONS (SKIP=1)
LOAD DATA
INFILE '/container-entrypoint-initdb.d/data/driver_monthly_metrics.csv'
INTO TABLE appuser.driver_monthly_metrics
FIELDS TERMINATED BY ','
(
    driver_id,
    month DATE "YYYY-MM-DD",
    trips_completed,
    total_miles,
    total_revenue,
    average_mpg,
    fuel_used,
    on_time_delivery_rate,
    average_idle_hours
)