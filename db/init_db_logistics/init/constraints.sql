USE LogisticsDB;
GO

-- loads
ALTER TABLE loads
ADD CONSTRAINT FK_loads_customers
FOREIGN KEY (customer_id) REFERENCES customers(customer_id);

ALTER TABLE loads
ADD CONSTRAINT FK_loads_routes
FOREIGN KEY (route_id) REFERENCES routes(route_id);

-- trips
ALTER TABLE trips
ADD CONSTRAINT FK_trips_loads
FOREIGN KEY (load_id) REFERENCES loads(load_id);

ALTER TABLE trips
ADD CONSTRAINT FK_trips_drivers
FOREIGN KEY (driver_id) REFERENCES drivers(driver_id);

ALTER TABLE trips
ADD CONSTRAINT FK_trips_trucks
FOREIGN KEY (truck_id) REFERENCES trucks(truck_id);

ALTER TABLE trips
ADD CONSTRAINT FK_trips_trailers
FOREIGN KEY (trailer_id) REFERENCES trailers(trailer_id);

-- delivery events
ALTER TABLE delivery_events
ADD CONSTRAINT FK_delivery_events_loads
FOREIGN KEY (load_id) REFERENCES loads(load_id);

ALTER TABLE delivery_events
ADD CONSTRAINT FK_delivery_events_trips
FOREIGN KEY (trip_id) REFERENCES trips(trip_id);

ALTER TABLE delivery_events
ADD CONSTRAINT FK_delivery_events_facilities
FOREIGN KEY (facility_id) REFERENCES facilities(facility_id);

-- fuel
ALTER TABLE fuel_purchases
ADD CONSTRAINT FK_fuel_trips
FOREIGN KEY (trip_id) REFERENCES trips(trip_id);

ALTER TABLE fuel_purchases
ADD CONSTRAINT FK_fuel_trucks
FOREIGN KEY (truck_id) REFERENCES trucks(truck_id);

ALTER TABLE fuel_purchases
ADD CONSTRAINT FK_fuel_drivers
FOREIGN KEY (driver_id) REFERENCES drivers(driver_id);

-- maintenance
ALTER TABLE maintenance_records
ADD CONSTRAINT FK_maintenance_trucks
FOREIGN KEY (truck_id) REFERENCES trucks(truck_id);

-- safety
ALTER TABLE safety_incidents
ADD CONSTRAINT FK_safety_trips
FOREIGN KEY (trip_id) REFERENCES trips(trip_id);

ALTER TABLE safety_incidents
ADD CONSTRAINT FK_safety_trucks
FOREIGN KEY (truck_id) REFERENCES trucks(truck_id);

ALTER TABLE safety_incidents
ADD CONSTRAINT FK_safety_drivers
FOREIGN KEY (driver_id) REFERENCES drivers(driver_id);

-- metrics
ALTER TABLE driver_monthly_metrics
ADD CONSTRAINT FK_driver_metrics
FOREIGN KEY (driver_id) REFERENCES drivers(driver_id);

ALTER TABLE truck_utilization_metrics
ADD CONSTRAINT FK_truck_metrics
FOREIGN KEY (truck_id) REFERENCES trucks(truck_id);