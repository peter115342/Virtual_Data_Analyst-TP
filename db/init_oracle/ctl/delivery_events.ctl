OPTIONS (SKIP=1)
LOAD DATA
INFILE '/container-entrypoint-initdb.d/data/delivery_events.csv'
INTO TABLE appuser.delivery_events
FIELDS TERMINATED BY ','
(
    event_id,
    load_id,
    trip_id,
    event_type,
    facility_id,
    scheduled_datetime "TO_TIMESTAMP(:scheduled_datetime, 'YYYY-MM-DD HH24:MI:SS.FF6')",
    actual_datetime "TO_TIMESTAMP(:actual_datetime, 'YYYY-MM-DD HH24:MI:SS.FF6')",
    detention_minutes,
    on_time_flag "CASE WHEN :on_time_flag='True' THEN 1 ELSE 0 END",
    location_city,
    location_state
)