CREATE DATABASE LogisticsDB;
GO

USE LogisticsDB;
GO


-- =========================
-- DIMENSION TABLES
-- =========================

CREATE TABLE customers (
    customer_id NVARCHAR(20) PRIMARY KEY,
    customer_name NVARCHAR(150),
    customer_type NVARCHAR(50),
    credit_terms_days INT,
    primary_freight_type NVARCHAR(100),
    account_status NVARCHAR(20),
    contract_start_date DATE,
    annual_revenue_potential INT
);

CREATE TABLE drivers (
    driver_id NVARCHAR(20) PRIMARY KEY,
    first_name NVARCHAR(50),
    last_name NVARCHAR(50),
    hire_date DATE,
    termination_date DATE NULL,
    license_number NVARCHAR(50),
    license_state NVARCHAR(10),
    date_of_birth DATE,
    home_terminal NVARCHAR(100),
    employment_status NVARCHAR(20),
    cdl_class NVARCHAR(10),
    years_experience INT
);

CREATE TABLE trucks (
    truck_id NVARCHAR(20) PRIMARY KEY,
    unit_number INT,
    make NVARCHAR(50),
    model_year INT,
    vin NVARCHAR(50),
    acquisition_date DATE,
    acquisition_mileage INT,
    fuel_type NVARCHAR(20),
    tank_capacity_gallons INT,
    status NVARCHAR(20),
    home_terminal NVARCHAR(100)
);

CREATE TABLE trailers (
    trailer_id NVARCHAR(20) PRIMARY KEY,
    trailer_number INT,
    trailer_type NVARCHAR(50),
    length_feet INT,
    model_year INT,
    vin NVARCHAR(50),
    acquisition_date DATE,
    status NVARCHAR(20),
    current_location NVARCHAR(100)
);

CREATE TABLE facilities (
    facility_id NVARCHAR(20) PRIMARY KEY,
    facility_name NVARCHAR(150),
    facility_type NVARCHAR(50),
    city NVARCHAR(100),
    state NVARCHAR(10),
    latitude FLOAT,
    longitude FLOAT,
    dock_doors INT,
    operating_hours NVARCHAR(50)
);

CREATE TABLE routes (
    route_id NVARCHAR(20) PRIMARY KEY,
    origin_city NVARCHAR(100),
    origin_state NVARCHAR(10),
    destination_city NVARCHAR(100),
    destination_state NVARCHAR(10),
    typical_distance_miles INT,
    base_rate_per_mile FLOAT,
    fuel_surcharge_rate FLOAT,
    transit_transit_days INT
);

-- =========================
-- FACT TABLES
-- =========================

CREATE TABLE loads (
    load_id NVARCHAR(20) PRIMARY KEY,
    customer_id NVARCHAR(20),
    route_id NVARCHAR(20),
    load_date DATE,
    load_type NVARCHAR(50),
    weight_lbs INT,
    pieces INT,
    revenue FLOAT,
    fuel_surcharge FLOAT,
    accessorial_charges FLOAT,
    load_status NVARCHAR(20),
    booking_type NVARCHAR(50)
);

CREATE TABLE trips (
    trip_id NVARCHAR(20) PRIMARY KEY,
    load_id NVARCHAR(20),
    driver_id NVARCHAR(20),
    truck_id NVARCHAR(20),
    trailer_id NVARCHAR(20),
    dispatch_date DATE,
    actual_distance_miles INT,
    actual_duration_hours FLOAT,
    fuel_gallons_used FLOAT,
    average_mpg FLOAT,
    idle_time_hours FLOAT,
    trip_status NVARCHAR(20)
);

CREATE TABLE delivery_events (
    event_id NVARCHAR(20) PRIMARY KEY,
    load_id NVARCHAR(20),
    trip_id NVARCHAR(20),
    event_type NVARCHAR(20),
    facility_id NVARCHAR(20),
    scheduled_datetime DATETIME2,
    actual_datetime DATETIME2,
    detention_minutes INT,
    on_time_flag BIT,
    location_city NVARCHAR(100),
    location_state NVARCHAR(10)
);

CREATE TABLE fuel_purchases (
    fuel_purchase_id NVARCHAR(20) PRIMARY KEY,
    trip_id NVARCHAR(20),
    truck_id NVARCHAR(20),
    driver_id NVARCHAR(20) NULL,
    purchase_datetime DATETIME2,
    location_city NVARCHAR(100),
    location_state NVARCHAR(10),
    gallons FLOAT,
    price_per_gallon FLOAT,
    total_cost FLOAT,
    fuel_card_number NVARCHAR(50)
);

CREATE TABLE maintenance_records (
    maintenance_id NVARCHAR(20) PRIMARY KEY,
    truck_id NVARCHAR(20),
    maintenance_date DATE,
    maintenance_type NVARCHAR(50),
    odometer_reading INT,
    labor_hours FLOAT,
    labor_cost FLOAT,
    parts_cost FLOAT,
    total_cost FLOAT,
    facility_location NVARCHAR(100),
    downtime_hours FLOAT,
    service_description NVARCHAR(200)
);

CREATE TABLE safety_incidents (
    incident_id NVARCHAR(20) PRIMARY KEY,
    trip_id NVARCHAR(20),
    truck_id NVARCHAR(20),
    driver_id NVARCHAR(20),
    incident_date DATETIME2,
    incident_type NVARCHAR(50),
    location_city NVARCHAR(100),
    location_state NVARCHAR(10),
    at_fault_flag BIT,
    injury BIT,
    vehicle_damage_cost FLOAT,
    cargo_damage_cost FLOAT,
    claim_amount FLOAT,
    preventable_flag BIT,
    description NVARCHAR(200)
);

CREATE TABLE driver_monthly_metrics (
    driver_id NVARCHAR(20),
    month DATE,
    trips_completed INT,
    total_miles INT,
    total_revenue FLOAT,
    average_mpg FLOAT,
    fuel_used FLOAT,
    on_time_delivery_rate FLOAT,
    average_idle_hours FLOAT,
    PRIMARY KEY (driver_id, month)
);

CREATE TABLE truck_utilization_metrics (
    truck_id NVARCHAR(20),
    month DATE,
    trips_completed INT,
    total_miles INT,
    total_revenue FLOAT,
    average_mpg FLOAT,
    maintenance_events INT,
    maintenance_cost FLOAT,
    downtime_hours FLOAT,
    utilization_rate FLOAT,
    PRIMARY KEY (truck_id, month)
);