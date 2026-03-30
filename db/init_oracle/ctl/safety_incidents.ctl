OPTIONS (SKIP=1)
LOAD DATA
INFILE '/container-entrypoint-initdb.d/data/safety_incidents.csv'
INTO TABLE appuser.safety_incidents
FIELDS TERMINATED BY ','
(
    incident_id,
    trip_id,
    truck_id,
    driver_id,
    incident_date "TO_TIMESTAMP(:incident_date, 'YYYY-MM-DD HH24:MI:SS')",
    incident_type,
    location_city,
    location_state,
    at_fault_flag "CASE WHEN :at_fault_flag='True' THEN 1 ELSE 0 END",
    injury "CASE WHEN :injury='True' THEN 1 ELSE 0 END",
    vehicle_damage_cost,
    cargo_damage_cost,
    claim_amount,
    preventable_flag "CASE WHEN :preventable_flag='True' THEN 1 ELSE 0 END",
    description
)