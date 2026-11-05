print("PicoGrid solar model is starting...")
from pathlib import Path
import pandas as pd

# Project paths
ROOT = Path(__file__).resolve().parent.parent

INPUT = ROOT / "data" / "processed" / "nasa_power_dhulikhel_cleaned.csv"
OUTPUT = ROOT / "data" / "processed" / "solar_generation_daily.csv"

# Hypothetical pilot system specifications
PV_CAPACITY_KWP = 10.0
PERFORMANCE_RATIO = 0.78

# Read cleaned NASA POWER data
df = pd.read_csv(INPUT, parse_dates=["date"])

# NASA daily solar radiation:
# ALLSKY_SFC_SW_DWN is expressed in kWh/m²/day.
df["solar_irradiation_kwh_m2"] = df["ALLSKY_SFC_SW_DWN"]

# Initial energy estimate
df["estimated_solar_generation_kwh"] = (
    PV_CAPACITY_KWP
    * df["solar_irradiation_kwh_m2"]
    * PERFORMANCE_RATIO
)

# Basic theoretical capacity factor
df["capacity_factor"] = (
    df["estimated_solar_generation_kwh"]
    / (PV_CAPACITY_KWP * 24)
)

# Monthly summary
monthly = (
    df.set_index("date")
    .resample("ME")
    .agg({
        "estimated_solar_generation_kwh": "sum",
        "solar_irradiation_kwh_m2": "mean",
        "capacity_factor": "mean"
    })
)

# Save outputs
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT, index=False)

monthly.to_csv(
    ROOT / "data" / "processed" / "solar_generation_monthly.csv"
)

# Display results
print("\nPICOGRID SOLAR GENERATION MODEL")
print("--------------------------------")
print(f"PV capacity: {PV_CAPACITY_KWP} kWp")
print(f"Performance ratio: {PERFORMANCE_RATIO}")

print("\nANNUAL ESTIMATED GENERATION:")
print(
    round(df["estimated_solar_generation_kwh"].sum(), 2),
    "kWh"
)

print("\nMONTHLY ESTIMATED GENERATION:")
print(monthly.round(2))

print("\nFiles saved successfully!")
