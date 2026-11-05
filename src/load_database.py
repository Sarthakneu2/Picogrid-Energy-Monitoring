
import os
import pandas as pd
import psycopg

from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------
# 1. DATABASE CONFIGURATION
# --------------------------------------------------

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "picogrid_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}

TIMEZONE = os.getenv("DB_TIMEZONE", "Asia/Kathmandu")

CSV_PATH = "data/processed/picogrid_master_dataset.csv"

BATCH_SIZE = 5000
SITE_ID = 1


# --------------------------------------------------
# 2. ENERGY TABLE INSERTION
# --------------------------------------------------

ENERGY_SQL = """
INSERT INTO energy_readings (
    site_id,
    device_id,
    recorded_at,
    pv_power_kw,
    load_power_kw,
    ac_voltage_v,
    ac_current_a,
    ac_frequency_hz,
    power_factor,
    grid_import_kw,
    grid_export_kw,
    inverter_output_kw,
    data_origin,
    hardware_connected
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s
)
ON CONFLICT (site_id, recorded_at)
DO UPDATE SET
    pv_power_kw = EXCLUDED.pv_power_kw,
    load_power_kw = EXCLUDED.load_power_kw,
    ac_voltage_v = EXCLUDED.ac_voltage_v,
    ac_current_a = EXCLUDED.ac_current_a,
    ac_frequency_hz = EXCLUDED.ac_frequency_hz,
    power_factor = EXCLUDED.power_factor,
    grid_import_kw = EXCLUDED.grid_import_kw,
    grid_export_kw = EXCLUDED.grid_export_kw,
    inverter_output_kw = EXCLUDED.inverter_output_kw,
    data_origin = EXCLUDED.data_origin,
    hardware_connected = EXCLUDED.hardware_connected;
"""


# --------------------------------------------------
# 3. BATTERY TABLE INSERTION
# --------------------------------------------------

BATTERY_SQL = """
INSERT INTO battery_readings (
    site_id,
    device_id,
    recorded_at,
    voltage_v,
    current_a,
    power_kw,
    state_of_charge_pct,
    energy_kwh,
    temperature_c,
    battery_status,
    equivalent_full_cycles,
    data_origin
)
VALUES (
    %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s
)
ON CONFLICT (site_id, recorded_at)
DO UPDATE SET
    voltage_v = EXCLUDED.voltage_v,
    current_a = EXCLUDED.current_a,
    power_kw = EXCLUDED.power_kw,
    state_of_charge_pct = EXCLUDED.state_of_charge_pct,
    energy_kwh = EXCLUDED.energy_kwh,
    temperature_c = EXCLUDED.temperature_c,
    battery_status = EXCLUDED.battery_status,
    equivalent_full_cycles = EXCLUDED.equivalent_full_cycles,
    data_origin = EXCLUDED.data_origin;
"""


# --------------------------------------------------
# 4. DATA PREPARATION
# --------------------------------------------------

def prepare_data():

    print("\nLoading PicoGrid master dataset...")

    df = pd.read_csv(CSV_PATH)

    print(f"Records found: {len(df):,}")

    required_columns = [
        "timestamp",
        "pv_power_kw",
        "load_power_kw",
        "ac_voltage_v",
        "ac_current_a",
        "ac_frequency_hz",
        "power_factor",
        "grid_import_kw",
        "grid_export_kw",
        "inverter_ac_output_kw",
        "data_origin",
        "hardware_connected",
        "battery_voltage_v",
        "battery_current_a",
        "battery_power_kw",
        "battery_soc_pct",
        "battery_energy_kwh",
        "battery_temperature_c",
        "battery_status",
        "equivalent_full_cycles",
    ]

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if df["timestamp"].isna().any():
        raise ValueError("Missing timestamps found.")

    if df["timestamp"].duplicated().any():
        raise ValueError("Duplicate timestamps found in master dataset.")

    # Timestamps are local Nepal time.
    df["timestamp"] = (
        pd.to_datetime(df["timestamp"], errors="raise")
        .dt.tz_localize(TIMEZONE)
    )

    if df["data_origin"].isna().any():
        raise ValueError("Missing data_origin values found.")

    if df["data_origin"].astype(str).str.len().gt(50).any():
        raise ValueError("data_origin exceeds database column length.")

    if df["battery_status"].dropna().astype(str).str.len().gt(30).any():
        raise ValueError("battery_status exceeds database column length.")

    print("Data preparation completed.")

    return df


# --------------------------------------------------
# 5. CONVERT VALUES FOR POSTGRESQL
# --------------------------------------------------

def clean_value(value):

    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return value


# --------------------------------------------------
# 6. MAIN DATABASE LOADER
# --------------------------------------------------

def main():

    if not DB_CONFIG["password"]:
        raise ValueError("DB_PASSWORD is missing from .env")

    df = prepare_data()

    print("\nConnecting to PostgreSQL...")

    with psycopg.connect(**DB_CONFIG) as conn:

        with conn.cursor() as cur:

            cur.execute(
                "SELECT site_id FROM sites WHERE site_id = %s",
                (SITE_ID,)
            )

            if cur.fetchone() is None:
                raise ValueError(
                    f"Site ID {SITE_ID} does not exist in the sites table."
                )

            print("PostgreSQL connection successful.")
            print(f"Using site ID: {SITE_ID}")

            total = len(df)

            for start in range(0, total, BATCH_SIZE):

                batch = df.iloc[start:start + BATCH_SIZE]

                energy_rows = []
                battery_rows = []

                for row in batch.itertuples(index=False):

                    data = row._asdict()

                    timestamp = data["timestamp"].to_pydatetime()

                    energy_rows.append((
                        SITE_ID,
                        None,
                        timestamp,
                        clean_value(data["pv_power_kw"]),
                        clean_value(data["load_power_kw"]),
                        clean_value(data["ac_voltage_v"]),
                        clean_value(data["ac_current_a"]),
                        clean_value(data["ac_frequency_hz"]),
                        clean_value(data["power_factor"]),
                        clean_value(data["grid_import_kw"]),
                        clean_value(data["grid_export_kw"]),
                        clean_value(data["inverter_ac_output_kw"]),
                        clean_value(data["data_origin"]),
                        clean_value(data["hardware_connected"]),
                    ))

                    battery_rows.append((
                        SITE_ID,
                        None,
                        timestamp,
                        clean_value(data["battery_voltage_v"]),
                        clean_value(data["battery_current_a"]),
                        clean_value(data["battery_power_kw"]),
                        clean_value(data["battery_soc_pct"]),
                        clean_value(data["battery_energy_kwh"]),
                        clean_value(data["battery_temperature_c"]),
                        clean_value(data["battery_status"]),
                        clean_value(data["equivalent_full_cycles"]),
                        clean_value(data["data_origin"]),
                    ))

                cur.executemany(ENERGY_SQL, energy_rows)
                cur.executemany(BATTERY_SQL, battery_rows)

                processed = min(start + len(batch), total)

                print(
                    f"Processed {processed:,} / {total:,} records"
                )

            # Verify the final database counts.
            cur.execute(
                """
                SELECT COUNT(*)
                FROM energy_readings
                WHERE site_id = %s
                """,
                (SITE_ID,)
            )

            energy_count = cur.fetchone()[0]

            cur.execute(
                """
                SELECT COUNT(*)
                FROM battery_readings
                WHERE site_id = %s
                """,
                (SITE_ID,)
            )

            battery_count = cur.fetchone()[0]

    print("\n" + "=" * 45)
    print("PICOGRID DATABASE LOADING REPORT")
    print("=" * 45)

    print(f"Master dataset records: {len(df):,}")
    print(f"Energy database records: {energy_count:,}")
    print(f"Battery database records: {battery_count:,}")

    print("\nDATABASE LOADING COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()
