
ALTER SESSION SET CONTAINER = FREEPDB1;

-- ALTER TABLE bank_accounts ADD PRIMARY KEY (id);

-- LOADS
ALTER TABLE appuser.loads
ADD CONSTRAINT fk_loads_customers
FOREIGN KEY (customer_id) REFERENCES appuser.customers(customer_id);

ALTER TABLE appuser.loads
ADD CONSTRAINT fk_loads_routes
FOREIGN KEY (route_id) REFERENCES appuser.routes(route_id);

-- TRIPS
ALTER TABLE appuser.trips
ADD CONSTRAINT fk_trips_loads
FOREIGN KEY (load_id) REFERENCES appuser.loads(load_id);

ALTER TABLE appuser.trips
ADD CONSTRAINT fk_trips_drivers
FOREIGN KEY (driver_id) REFERENCES appuser.drivers(driver_id);

ALTER TABLE appuser.trips
ADD CONSTRAINT fk_trips_trucks
FOREIGN KEY (truck_id) REFERENCES appuser.trucks(truck_id);

ALTER TABLE appuser.trips
ADD CONSTRAINT fk_trips_trailers
FOREIGN KEY (trailer_id) REFERENCES appuser.trailers(trailer_id);

-- DELIVERY EVENTS
ALTER TABLE appuser.delivery_events
ADD CONSTRAINT fk_delivery_events_loads
FOREIGN KEY (load_id) REFERENCES appuser.loads(load_id);

ALTER TABLE appuser.delivery_events
ADD CONSTRAINT fk_delivery_events_trips
FOREIGN KEY (trip_id) REFERENCES appuser.trips(trip_id);

ALTER TABLE appuser.delivery_events
ADD CONSTRAINT fk_delivery_events_facilities
FOREIGN KEY (facility_id) REFERENCES appuser.facilities(facility_id);

-- FUEL
ALTER TABLE appuser.fuel_purchases
ADD CONSTRAINT fk_fuel_trips
FOREIGN KEY (trip_id) REFERENCES appuser.trips(trip_id);

ALTER TABLE appuser.fuel_purchases
ADD CONSTRAINT fk_fuel_trucks
FOREIGN KEY (truck_id) REFERENCES appuser.trucks(truck_id);

ALTER TABLE appuser.fuel_purchases
ADD CONSTRAINT fk_fuel_drivers
FOREIGN KEY (driver_id) REFERENCES appuser.drivers(driver_id);

-- MAINTENANCE
ALTER TABLE appuser.maintenance_records
ADD CONSTRAINT fk_maintenance_trucks
FOREIGN KEY (truck_id) REFERENCES appuser.trucks(truck_id);

-- SAFETY
ALTER TABLE appuser.safety_incidents
ADD CONSTRAINT fk_safety_trips
FOREIGN KEY (trip_id) REFERENCES appuser.trips(trip_id);

ALTER TABLE appuser.safety_incidents
ADD CONSTRAINT fk_safety_trucks
FOREIGN KEY (truck_id) REFERENCES appuser.trucks(truck_id);

ALTER TABLE appuser.safety_incidents
ADD CONSTRAINT fk_safety_drivers
FOREIGN KEY (driver_id) REFERENCES appuser.drivers(driver_id);

-- METRICS
ALTER TABLE appuser.driver_monthly_metrics
ADD CONSTRAINT fk_driver_metrics
FOREIGN KEY (driver_id) REFERENCES appuser.drivers(driver_id);

ALTER TABLE appuser.truck_utilization_metrics
ADD CONSTRAINT fk_truck_metrics
FOREIGN KEY (truck_id) REFERENCES appuser.trucks(truck_id);