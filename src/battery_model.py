
from pathlib import Path
import numpy as np
import pandas as pd

# ==================================================
# PICOGRID BATTERY MANAGEMENT SYSTEM
# ==================================================

ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    ROOT / "data" / "simulated"
    / "energy_telemetry.csv"
)

OUTPUT_DIR = ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = (
    OUTPUT_DIR / "battery_management_telemetry.csv"
)

# --------------------------------------------------
# BATTERY CONFIGURATION
# --------------------------------------------------

BATTERY_CAPACITY_KWH = 20.0
BATTERY_NOMINAL_VOLTAGE = 51.2

INITIAL_SOC = 55.0
MIN_SOC = 15.0
MAX_SOC = 95.0

MAX_CHARGE_POWER_KW = 5.0
MAX_DISCHARGE_POWER_KW = 5.0

CHARGE_EFFICIENCY = 0.95
DISCHARGE_EFFICIENCY = 0.95

INTERVAL_HOURS = 5 / 60

# Provisional temperature model
AMBIENT_TEMPERATURE = 25.0

# --------------------------------------------------
# LOAD TELEMETRY
# --------------------------------------------------

df = pd.read_csv(
    INPUT_FILE,
    parse_dates=["timestamp"]
)

df = df.sort_values("timestamp").reset_index(drop=True)

required_columns = [
    "timestamp",
    "pv_power_kw",
    "load_power_kw"
]

missing = [
    column for column in required_columns
    if column not in df.columns
]

if missing:
    raise ValueError(
        f"Missing required columns: {missing}"
    )

if df.empty:
    raise ValueError("Input telemetry file is empty.")

# --------------------------------------------------
# BATTERY STATE INITIALIZATION
# --------------------------------------------------

battery_energy = (
    BATTERY_CAPACITY_KWH * INITIAL_SOC / 100
)

minimum_energy = (
    BATTERY_CAPACITY_KWH * MIN_SOC / 100
)

maximum_energy = (
    BATTERY_CAPACITY_KWH * MAX_SOC / 100
)

equivalent_full_cycles = 0.0
cumulative_charge_kwh = 0.0
cumulative_discharge_kwh = 0.0

records = []

# --------------------------------------------------
# BATTERY MANAGEMENT LOOP
# --------------------------------------------------

for _, row in df.iterrows():

    timestamp = row["timestamp"]

    pv_power = max(
        0.0, float(row["pv_power_kw"])
    )

    load_power = max(
        0.0, float(row["load_power_kw"])
    )

    # Approximate PV-to-AC conversion
    inverter_efficiency = 0.96
    available_pv_ac = pv_power * inverter_efficiency

    net_power = available_pv_ac - load_power

    battery_power = 0.0
    battery_status = "IDLE"

    charge_energy = 0.0
    discharge_energy = 0.0

    # ----------------------------------------------
    # CHARGING
    # Positive battery power = charging
    # ----------------------------------------------

    if net_power > 0 and battery_energy < maximum_energy:

        charge_power = min(
            net_power,
            MAX_CHARGE_POWER_KW,
            (
                maximum_energy - battery_energy
            ) / (
                INTERVAL_HOURS * CHARGE_EFFICIENCY
            )
        )

        charge_energy = (
            charge_power
            * INTERVAL_HOURS
            * CHARGE_EFFICIENCY
        )

        battery_energy += charge_energy

        battery_power = charge_power
        battery_status = "CHARGING"

        cumulative_charge_kwh += charge_energy

    # ----------------------------------------------
    # DISCHARGING
    # Negative battery power = discharging
    # ----------------------------------------------

    elif net_power < 0 and battery_energy > minimum_energy:

        discharge_power = min(
            abs(net_power),
            MAX_DISCHARGE_POWER_KW,
            (
                battery_energy - minimum_energy
            ) * DISCHARGE_EFFICIENCY
            / INTERVAL_HOURS
        )

        discharge_energy = (
            discharge_power
            * INTERVAL_HOURS
            / DISCHARGE_EFFICIENCY
        )

        battery_energy -= discharge_energy

        battery_power = -discharge_power
        battery_status = "DISCHARGING"

        cumulative_discharge_kwh += discharge_energy

    # ----------------------------------------------
    # BATTERY STATE
    # ----------------------------------------------

    battery_soc = (
        battery_energy / BATTERY_CAPACITY_KWH
    ) * 100

    battery_current = (
        abs(battery_power) * 1000
        / BATTERY_NOMINAL_VOLTAGE
    )

    if battery_power < 0:
        battery_current *= -1

    # Simplified modelled battery voltage
    battery_voltage = (
        BATTERY_NOMINAL_VOLTAGE
        + (battery_soc - 50) * 0.035
    )

    # Simplified thermal estimate.
    # Not an actual temperature sensor reading.
    battery_temperature = (
        AMBIENT_TEMPERATURE
        + abs(battery_power) * 0.7
    )

    # Equivalent full cycles based on discharged energy
    equivalent_full_cycles = (
        cumulative_discharge_kwh
        / BATTERY_CAPACITY_KWH
    )

    # ----------------------------------------------
    # RECORD RESULTS
    # ----------------------------------------------

    records.append({
        "timestamp": timestamp,

        "battery_voltage_v": round(
            battery_voltage, 3
        ),

        "battery_current_a": round(
            battery_current, 3
        ),

        "battery_power_kw": round(
            battery_power, 3
        ),

        "battery_soc_pct": round(
            battery_soc, 3
        ),

        "battery_energy_kwh": round(
            battery_energy, 3
        ),

        "battery_temperature_c": round(
            battery_temperature, 2
        ),

        "battery_status": battery_status,

        "charge_energy_kwh": round(
            charge_energy, 5
        ),

        "discharge_energy_kwh": round(
            discharge_energy, 5
        ),

        "cumulative_charge_kwh": round(
            cumulative_charge_kwh, 3
        ),

        "cumulative_discharge_kwh": round(
            cumulative_discharge_kwh, 3
        ),

        "equivalent_full_cycles": round(
            equivalent_full_cycles, 4
        ),

        "min_soc_limit_pct": MIN_SOC,
        "max_soc_limit_pct": MAX_SOC,

        "data_origin": "modelled_battery_test"
    })


# --------------------------------------------------
# SAVE RESULTS
# --------------------------------------------------

battery_df = pd.DataFrame(records)

battery_df.to_csv(
    OUTPUT_FILE,
    index=False
)

# --------------------------------------------------
# VALIDATION AND SUMMARY
# --------------------------------------------------

print("\nPICOGRID BATTERY MANAGEMENT SYSTEM")
print("-----------------------------------")

print(f"Total records: {len(battery_df):,}")

print(
    f"Initial SOC: {INITIAL_SOC:.2f}%"
)

print(
    f"Final SOC: "
    f"{battery_df['battery_soc_pct'].iloc[-1]:.2f}%"
)

print(
    f"Minimum observed SOC: "
    f"{battery_df['battery_soc_pct'].min():.2f}%"
)

print(
    f"Maximum observed SOC: "
    f"{battery_df['battery_soc_pct'].max():.2f}%"
)

print(
    f"Total charged energy: "
    f"{cumulative_charge_kwh:.2f} kWh"
)

print(
    f"Total discharged energy: "
    f"{cumulative_discharge_kwh:.2f} kWh"
)

print(
    f"Equivalent full cycles: "
    f"{equivalent_full_cycles:.3f}"
)

print("\nBATTERY OPERATING STATUS")
print(battery_df["battery_status"].value_counts())

print("\nSOC VALIDATION")

assert battery_df["battery_soc_pct"].between(
    MIN_SOC - 0.001,
    MAX_SOC + 0.001
).all(), "SOC limit validation failed!"

print("SOC limits: PASSED")

print(f"\nSaved to: {OUTPUT_FILE}")
