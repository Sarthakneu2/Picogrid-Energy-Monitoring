
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data" / "processed" / "nasa_power_dhulikhel_cleaned.csv"
OUTPUT = ROOT / "reports"

OUTPUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT, parse_dates=["date"])
df = df.sort_values("date")

# Monthly averages and totals
monthly = df.set_index("date").resample("ME").agg({
    "ALLSKY_SFC_SW_DWN": "mean",
    "T2M": "mean",
    "PRECTOTCORR": "sum",
    "RH2M": "mean"
})

print("\nMONTHLY ENVIRONMENTAL SUMMARY")
print(monthly.round(2))

print("\nYEARLY SUMMARY")
print(df.describe().round(2))

# Monthly solar radiation
monthly["ALLSKY_SFC_SW_DWN"].plot(
    kind="bar", figsize=(10, 5),
    title="Monthly Average Solar Radiation - Dhulikhel 2025"
)
plt.ylabel("Solar radiation (kWh/m²/day)")
plt.tight_layout()
plt.savefig(OUTPUT / "monthly_solar_radiation.png")
plt.close()

# Daily temperature
plt.figure(figsize=(12, 5))
plt.plot(df["date"], df["T2M"])
plt.title("Daily Average Temperature - Dhulikhel 2025")
plt.ylabel("Temperature (°C)")
plt.tight_layout()
plt.savefig(OUTPUT / "daily_temperature.png")
plt.close()

# Monthly rainfall
monthly["PRECTOTCORR"].plot(
    kind="bar", figsize=(10, 5),
    title="Monthly Rainfall - Dhulikhel 2025"
)
plt.ylabel("Rainfall (mm)")
plt.tight_layout()
plt.savefig(OUTPUT / "monthly_rainfall.png")
plt.close()

monthly.to_csv(OUTPUT / "monthly_weather_summary.csv")

print("\nExploration completed successfully!")
print(f"Reports saved in: {OUTPUT}")
