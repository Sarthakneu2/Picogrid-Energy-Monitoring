
from pathlib import Path
import numpy as np
import pandas as pd

# --------------------------------------------------
# PICOGRID: SENSOR TELEMETRY ENGINE
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

WEATHER_FILE = (
    ROOT / "data" / "processed"
    / "nasa_power_dhulikhel_cleaned.csv"
)

SOLAR_FILE = (
    ROOT / "data" / "processed"
    / "solar_generation_daily.csv"
)

OUTPUT_DIR = ROOT / "data" / "simulated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "energy_telemetry.csv"

# System configuration
PV_CAPACITY_KWP = 10.0
BATTERY_CAPACITY_KWH = 20.0
INITIAL_BATTERY_SOC = 55.0

MIN_SOC = 15.0
MAX_SOC = 95.0

INVERTER_LIMIT_KW = 10.0
BATTERY_MAX_POWER_KW = 5.0

AC_VOLTAGE_REFERENCE = 230.0
AC_FREQUENCY_REFERENCE = 50.0

CHARGE_EFFICIENCY = 0.95
DISCHARGE_EFFICIENCY = 0.95

INTERVAL_MINUTES = 5
INTERVAL_HOURS = INTERVAL_MINUTES / 60

# Reproducible test run
rng = np.random.default_rng(42)


# --------------------------------------------------
# LOAD ENVIRONMENTAL AND SOLAR DATA
# --------------------------------------------------

weather = pd.read_csv(WEATHER_FILE, parse_dates=["date"])
solar = pd.read_csv(SOLAR_FILE, parse_dates=["date"])

df = weather.merge(
    solar[["date", "estimated_solar_generation_kwh"]],
    on="date",
    how="inner"
)

if df.empty:
    raise ValueError("No matching weather and solar records found.")

df = df.sort_values("date").reset_index(drop=True)


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def daylight_profile(hour):
    """
    Approximate daylight generation profile.
    Zero outside the modelled daylight window.
    """
    sunrise = 6.0
    sunset = 18.0

    if hour <= sunrise or hour >= sunset:
        return 0.0

    position = (hour - sunrise) / (sunset - sunrise)
    return max(0.0, np.sin(np.pi * position)) ** 1.5


def load_profile(hour):
    """
    Modelled household/community AC demand.
    """
    base_load = 0.65

    morning_peak = 1.1 * np.exp(
        -((hour - 8.0) / 1.8) ** 2
    )

    evening_peak = 1.8 * np.exp(
        -((hour - 19.5) / 2.5) ** 2
    )

    afternoon_load = 0.45 * np.exp(
        -((hour - 14.0) / 3.0) ** 2
    )

    return base_load + morning_peak + evening_peak + afternoon_load


# --------------------------------------------------
# GENERATE FIVE-MINUTE SENSOR TELEMETRY
# --------------------------------------------------

records = []
battery_soc = INITIAL_BATTERY_SOC
cumulative_energy_kwh = 0.0

for _, day in df.iterrows():

    date = day["date"].normalize()

    daily_solar_energy = max(
        0.0,
        float(day["estimated_solar_generation_kwh"])
    )

    # Build 288 five-minute intervals
    timestamps = pd.date_range(
        start=date,
        periods=288,
        freq="5min"
    )

    # Distribute daily solar energy across daylight hours
    weights = np.array([
        daylight_profile(ts.hour + ts.minute / 60)
        for ts in timestamps
    ])

    if weights.sum() > 0:
        solar_energy_intervals = (
            weights / weights.sum()
        ) * daily_solar_energy
    else:
        solar_energy_intervals = np.zeros(288)

    for ts, solar_energy in zip(
        timestamps, solar_energy_intervals
    ):

        hour = ts.hour + ts.minute / 60

        # PV output power in kW
        pv_power = solar_energy / INTERVAL_HOURS

        pv_power = clamp(
            pv_power + rng.normal(0, 0.025),
            0,
            PV_CAPACITY_KWP
        )

        # Modelled AC demand
        load_power = load_profile(hour)
        load_power += rng.normal(0, 0.04)
        load_power = clamp(load_power, 0.2, 5.0)

        # Inverter conversion
        inverter_efficiency = 0.96

        available_ac_power = min(
            pv_power * inverter_efficiency,
            INVERTER_LIMIT_KW
        )

        # Power balance
        surplus_power = max(
            0.0, available_ac_power - load_power
        )

        deficit_power = max(
            0.0, load_power - available_ac_power
        )

        battery_power = 0.0
        battery_status = "IDLE"

        battery_energy = (
            BATTERY_CAPACITY_KWH * battery_soc / 100
        )

        minimum_energy = (
            BATTERY_CAPACITY_KWH * MIN_SOC / 100
        )

        maximum_energy = (
            BATTERY_CAPACITY_KWH * MAX_SOC / 100
        )

        # Charge battery using excess solar
        if surplus_power > 0 and battery_energy < maximum_energy:

            charge_power = min(
                surplus_power,
                BATTERY_MAX_POWER_KW,
                (maximum_energy - battery_energy)
                / (INTERVAL_HOURS * CHARGE_EFFICIENCY)
            )

            battery_energy += (
                charge_power
                * INTERVAL_HOURS
                * CHARGE_EFFICIENCY
            )

            battery_power = charge_power
            battery_status = "CHARGING"

        # Discharge battery when solar is insufficient
        elif deficit_power > 0 and battery_energy > minimum_energy:

            discharge_power = min(
                deficit_power,
                BATTERY_MAX_POWER_KW,
                (battery_energy - minimum_energy)
                * DISCHARGE_EFFICIENCY
                / INTERVAL_HOURS
            )

            battery_energy -= (
                discharge_power
                * INTERVAL_HOURS
                / DISCHARGE_EFFICIENCY
            )

            battery_power = -discharge_power
            battery_status = "DISCHARGING"

        battery_soc = clamp(
            battery_energy / BATTERY_CAPACITY_KWH * 100,
            MIN_SOC,
            MAX_SOC
        )

        # Remaining grid import/export
        grid_import = max(
            0.0,
            deficit_power - abs(min(battery_power, 0))
        )

        grid_export = max(
            0.0,
            surplus_power - max(battery_power, 0)
        )

        # AC meter readings
        ac_voltage = AC_VOLTAGE_REFERENCE + rng.normal(0, 1.0)
        power_factor = clamp(
            0.97 + rng.normal(0, 0.008),
            0.90,
            1.0
        )

        ac_current = (
            load_power * 1000
            / (ac_voltage * power_factor)
        )

        ac_frequency = (
            AC_FREQUENCY_REFERENCE + rng.normal(0, 0.015)
        )

        # Provisional DC battery bus model.
        # Replace with actual battery specifications later.
        battery_voltage = 51.2 + rng.normal(0, 0.35)

        battery_current = (
            abs(battery_power) * 1000 / battery_voltage
        )

        if battery_power < 0:
            battery_current *= -1

        # Energy accumulation
        interval_energy = load_power * INTERVAL_HOURS
        cumulative_energy_kwh += interval_energy

        records.append({
            "timestamp": ts,
            "site": "Dhulikhel_Pilot",

            "pv_power_kw": round(pv_power, 3),
            "load_power_kw": round(load_power, 3),

            "ac_voltage_v": round(ac_voltage, 2),
            "ac_current_a": round(ac_current, 3),
            "ac_frequency_hz": round(ac_frequency, 3),
            "power_factor": round(power_factor, 3),

            "battery_voltage_v": round(battery_voltage, 2),
            "battery_current_a": round(battery_current, 3),
            "battery_power_kw": round(battery_power, 3),
            "battery_soc_pct": round(battery_soc, 2),
            "battery_status": battery_status,

            "grid_import_kw": round(grid_import, 3),
            "grid_export_kw": round(grid_export, 3),

            "inverter_efficiency": inverter_efficiency,
            "inverter_ac_output_kw": round(
                available_ac_power, 3
            ),

            "load_energy_cumulative_kwh": round(
                cumulative_energy_kwh, 3
            ),

            "measurement_interval_seconds": 300,

            # Explicit provenance for development data
            "data_origin": "modelled_test_telemetry",
            "hardware_connected": False
        })


# --------------------------------------------------
# SAVE TELEMETRY
# --------------------------------------------------

telemetry = pd.DataFrame(records)

telemetry.to_csv(OUTPUT_FILE, index=False)

print("\nPICOGRID TELEMETRY ENGINE")
print("--------------------------------")
print("Generation completed successfully!")

print(f"Total records: {len(telemetry):,}")
print(f"Start: {telemetry['timestamp'].min()}")
print(f"End: {telemetry['timestamp'].max()}")

print("\nTELEMETRY OVERVIEW")
print(
    telemetry[
        [
            "pv_power_kw",
            "load_power_kw",
            "battery_soc_pct",
            "ac_voltage_v",
            "ac_current_a"
        ]
    ].describe().round(2)
)

print("\nBATTERY STATUS COUNTS")
print(telemetry["battery_status"].value_counts())

print(f"\nSaved to: {OUTPUT_FILE}")
