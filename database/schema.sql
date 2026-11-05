
-- ============================================
-- PICOGRID ENERGY MONITORING DATABASE
-- PostgreSQL
-- ============================================

CREATE TABLE IF NOT EXISTS sites (
    site_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    site_name VARCHAR(150) NOT NULL,
    location VARCHAR(200),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    pv_capacity_kwp DECIMAL(10,2),
    battery_capacity_kwh DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS devices (
    device_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    site_id BIGINT REFERENCES sites(site_id),
    device_name VARCHAR(150) NOT NULL,
    device_type VARCHAR(80) NOT NULL,
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(150) UNIQUE,
    installation_date DATE,
    status VARCHAR(30) DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sensors (
    sensor_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    device_id BIGINT REFERENCES devices(device_id),
    sensor_name VARCHAR(150) NOT NULL,
    sensor_type VARCHAR(80) NOT NULL,
    measurement_unit VARCHAR(30),
    calibration_offset DECIMAL(12,5) DEFAULT 0,
    calibration_factor DECIMAL(12,5) DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS environmental_readings (
    reading_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    site_id BIGINT REFERENCES sites(site_id),
    recorded_at TIMESTAMPTZ NOT NULL,
    solar_radiation DECIMAL(12,4),
    temperature_c DECIMAL(8,3),
    rainfall_mm DECIMAL(10,3),
    humidity_pct DECIMAL(8,3),
    wind_speed_ms DECIMAL(8,3),
    data_source VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(site_id, recorded_at)
);

CREATE TABLE IF NOT EXISTS energy_readings (
    reading_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    site_id BIGINT REFERENCES sites(site_id),
    device_id BIGINT REFERENCES devices(device_id),
    recorded_at TIMESTAMPTZ NOT NULL,

    pv_power_kw DECIMAL(12,4),
    load_power_kw DECIMAL(12,4),

    ac_voltage_v DECIMAL(12,4),
    ac_current_a DECIMAL(12,4),
    ac_frequency_hz DECIMAL(8,4),
    power_factor DECIMAL(6,4),

    grid_import_kw DECIMAL(12,4),
    grid_export_kw DECIMAL(12,4),

    inverter_output_kw DECIMAL(12,4),

    data_origin VARCHAR(50) NOT NULL,
    hardware_connected BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(site_id, recorded_at)
);

CREATE TABLE IF NOT EXISTS battery_readings (
    reading_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    site_id BIGINT REFERENCES sites(site_id),
    device_id BIGINT REFERENCES devices(device_id),
    recorded_at TIMESTAMPTZ NOT NULL,

    voltage_v DECIMAL(12,4),
    current_a DECIMAL(12,4),
    power_kw DECIMAL(12,4),
    state_of_charge_pct DECIMAL(7,3),
    energy_kwh DECIMAL(12,4),
    temperature_c DECIMAL(8,3),

    battery_status VARCHAR(30),
    equivalent_full_cycles DECIMAL(12,4),

    data_origin VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(site_id, recorded_at)
);

CREATE TABLE IF NOT EXISTS system_events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    site_id BIGINT REFERENCES sites(site_id),
    device_id BIGINT REFERENCES devices(device_id),
    event_type VARCHAR(80) NOT NULL,
    severity VARCHAR(20) DEFAULT 'INFO',
    description TEXT,
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

-- ============================================
-- PERFORMANCE INDEXES
-- ============================================

CREATE INDEX IF NOT EXISTS idx_energy_recorded_at
ON energy_readings(recorded_at);

CREATE INDEX IF NOT EXISTS idx_battery_recorded_at
ON battery_readings(recorded_at);

CREATE INDEX IF NOT EXISTS idx_environment_recorded_at
ON environmental_readings(recorded_at);

CREATE INDEX IF NOT EXISTS idx_events_recorded_at
ON system_events(recorded_at);

CREATE INDEX IF NOT EXISTS idx_devices_site
ON devices(site_id);

-- ============================================
-- INITIAL SITE
-- ============================================

INSERT INTO sites (
    site_name,
    location,
    latitude,
    longitude,
    pv_capacity_kwp,
    battery_capacity_kwh
)
SELECT
    'PicoGrid Dhulikhel Pilot',
    'Dhulikhel, Kavrepalanchok, Nepal',
    27.6221,
    85.5428,
    10.0,
    20.0
WHERE NOT EXISTS (
    SELECT 1 FROM sites
    WHERE site_name = 'PicoGrid Dhulikhel Pilot'
);
