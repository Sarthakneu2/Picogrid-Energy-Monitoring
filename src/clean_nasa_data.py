
from pathlib import Path
import pandas as pd

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_FILE = PROJECT_ROOT / "data" / "raw" / "nasa_power_dhulikhel_2025.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "nasa_power_dhulikhel_cleaned.csv"

# Read NASA POWER CSV.
# NASA files contain metadata before the actual CSV table.
df = pd.read_csv(RAW_FILE, skiprows=15)

# Create a proper date column
df["date"] = pd.to_datetime(
    df[["YEAR", "MO", "DY"]].rename(
        columns={"YEAR": "year", "MO": "month", "DY": "day"}
    )
)

# Remove unnecessary date components
df = df.drop(columns=["YEAR", "MO", "DY"])

# Replace NASA's missing-data marker
df = df.replace(-999, pd.NA)

# Convert measurements to numeric values
for column in df.columns:
    if column != "date":
        df[column] = pd.to_numeric(df[column], errors="coerce")

# Sort by date and remove duplicate dates
df = df.sort_values("date")
df = df.drop_duplicates(subset=["date"])

# Save cleaned dataset
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)

# Display validation summary
print("PicoGrid: NASA POWER data processing complete!")
print(f"Records: {len(df)}")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print(f"Missing values:\n{df.isnull().sum()}")
print(f"Saved to: {OUTPUT_FILE}")
