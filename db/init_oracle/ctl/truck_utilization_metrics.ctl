OPTIONS (SKIP=1)
LOAD DATA
INFILE '/container-entrypoint-initdb.d/data/truck_utilization_metrics.csv'
INTO TABLE truck_utilization_metrics
FIELDS TERMINATED BY ','
(
    truck_id,
    month DATE "YYYY-MM-DD",
    trips_completed,
    total_miles,
    total_revenue,
    average_mpg,
    maintenance_events,
    maintenance_cost,
    downtime_hours,
    utilization_rate
)