
from pathlib import Path
import pandas as pd
import numpy as np

# ============================================
# PICOGRID DATA INTEGRATION PIPELINE
# ============================================

ROOT = Path(__file__).resolve().parent.parent

TELEMETRY_FILE = (
    ROOT / "data" / "simulated"
    / "energy_telemetry.csv"
)

BATTERY_FILE = (
    ROOT / "data" / "processed"
    / "battery_management_telemetry.csv"
)

OUTPUT_DIR = ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "picogrid_master_dataset.csv"

BATTERY_CAPACITY_KWH = 20.0
MIN_SOC = 15.0
MAX_SOC = 95.0
MAX_BATTERY_POWER_KW = 5.0

# ============================================
# LOAD DATA
# ============================================

print("\nPICOGRID DATA PIPELINE")
print("======================")

telemetry = pd.read_csv(
    TELEMETRY_FILE,
    parse_dates=["timestamp"]
)

battery = pd.read_csv(
    BATTERY_FILE,
    parse_dates=["timestamp"]
)

print(f"Energy telemetry records: {len(telemetry):,}")
print(f"Battery records: {len(battery):,}")

# ============================================
# VALIDATE INPUTS
# ============================================

if telemetry.empty or battery.empty:
    raise ValueError("An input dataset is empty.")

if telemetry["timestamp"].duplicated().any():
    raise ValueError("Duplicate telemetry timestamps found.")

if battery["timestamp"].duplicated().any():
    raise ValueError("Duplicate battery timestamps found.")

# Use the battery model as the authoritative
# source for battery state variables.
battery_columns = [
    "timestamp",
    "battery_voltage_v",
    "battery_current_a",
    "battery_power_kw",
    "battery_soc_pct",
    "battery_energy_kwh",
    "battery_temperature_c",
    "battery_status",
    "charge_energy_kwh",
    "discharge_energy_kwh",
    "cumulative_charge_kwh",
    "cumulative_discharge_kwh",
    "equivalent_full_cycles"
]

battery = battery[battery_columns]

# Remove earlier simplified battery estimates.
telemetry = telemetry.drop(
    columns=[
        "battery_voltage_v",
        "battery_current_a",
        "battery_power_kw",
        "battery_soc_pct",
        "battery_status"
    ],
    errors="ignore"
)

# ============================================
# INTEGRATE DATA
# ============================================

df = telemetry.merge(
    battery,
    on="timestamp",
    how="inner",
    validate="one_to_one"
)

df = df.sort_values("timestamp").reset_index(drop=True)

if len(df) != len(telemetry):
    raise ValueError(
        "Some telemetry records did not match battery records."
    )

print(f"Integrated records: {len(df):,}")

# ============================================
# RECONCILE POWER FLOW
# ============================================

inverter_efficiency = 0.96

df["pv_ac_available_kw"] = (
    df["pv_power_kw"] * inverter_efficiency
)

# Positive battery power means charging.
# Negative battery power means discharging.
df["grid_import_kw"] = np.maximum(
    0,
    df["load_power_kw"]
    - df["pv_ac_available_kw"]
    + df["battery_power_kw"]
)

df["grid_export_kw"] = np.maximum(
    0,
    df["pv_ac_available_kw"]
    - df["load_power_kw"]
    - df["battery_power_kw"]
)

# Residual power balance check.
df["power_balance_residual_kw"] = (
    df["pv_ac_available_kw"]
    + df["grid_import_kw"]
    - df["load_power_kw"]
    - df["battery_power_kw"]
    - df["grid_export_kw"]
)

# ============================================
# DATA QUALITY CHECKS
# ============================================

checks = {}

checks["No missing timestamps"] = (
    df["timestamp"].notna().all()
)

checks["No duplicate timestamps"] = (
    not df["timestamp"].duplicated().any()
)

checks["SOC within operating limits"] = (
    df["battery_soc_pct"].between(
        MIN_SOC - 0.001,
        MAX_SOC + 0.001
    ).all()
)

checks["Battery energy within capacity"] = (
    df["battery_energy_kwh"].between(
        BATTERY_CAPACITY_KWH * MIN_SOC / 100 - 0.001,
        BATTERY_CAPACITY_KWH * MAX_SOC / 100 + 0.001
    ).all()
)

checks["Battery power within limits"] = (
    df["battery_power_kw"].abs().le(
        MAX_BATTERY_POWER_KW + 0.001
    ).all()
)

checks["Non-negative PV power"] = (
    df["pv_power_kw"].ge(0).all()
)

checks["Non-negative load power"] = (
    df["load_power_kw"].ge(0).all()
)

checks["Power balance reconciled"] = (
    df["power_balance_residual_kw"].abs().max() < 0.001
)

print("\nDATA QUALITY REPORT")
print("-------------------")

for name, passed in checks.items():
    print(f"{'PASS' if passed else 'FAIL'}: {name}")

if not all(checks.values()):
    raise ValueError(
        "Data validation failed. Review the checks above."
    )

# ============================================
# ENERGY SUMMARY
# ============================================

df["load_interval_energy_kwh"] = (
    df["load_power_kw"] * (5 / 60)
)

df["pv_interval_energy_kwh"] = (
    df["pv_power_kw"] * (5 / 60)
)

summary = {
    "records": len(df),
    "pv_energy_kwh": df["pv_interval_energy_kwh"].sum(),
    "load_energy_kwh": df["load_interval_energy_kwh"].sum(),
    "grid_import_kwh": (df["grid_import_kw"] * 5 / 60).sum(),
    "grid_export_kwh": (df["grid_export_kw"] * 5 / 60).sum(),
    "final_battery_soc_pct": df["battery_soc_pct"].iloc[-1]
}

# ============================================
# SAVE MASTER DATASET
# ============================================

df.to_csv(OUTPUT_FILE, index=False)

print("\nANNUAL ENERGY SUMMARY")
print("---------------------")

for key, value in summary.items():
    print(f"{key}: {value:.2f}" if isinstance(value, (float, np.floating)) else f"{key}: {value}")

print("\nPIPELINE COMPLETED SUCCESSFULLY")
print(f"Master dataset: {OUTPUT_FILE}")
