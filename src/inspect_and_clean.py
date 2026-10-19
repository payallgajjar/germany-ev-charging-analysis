from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = (
    PROJECT_DIR/ "data"/ "raw"/ "charging_infrastructure.xlsx"
)

OUTPUT_DIR = PROJECT_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if not RAW_FILE.exists():
    raise FileNotFoundError(
        f"Excel file not found: {RAW_FILE}"
    )

excel_file = pd.ExcelFile(RAW_FILE)

print("WORKBOOK SHEETS")
print("=" * 40)

for sheet in excel_file.sheet_names:
    print(sheet)


states_raw = pd.read_excel(
    RAW_FILE,
    sheet_name=" 2. Current Overview BL",
    header=None
)

states = states_raw.iloc[12:28, [5, 7, 8, 9, 10, 11]].copy()

states.columns = [
    "federal_state",
    "normal_charging_points",
    "fast_charging_points",
    "total_charging_points",
    "previous_year_total",
    "annual_change_pct"
]
states["federal_state"] = (
    states["federal_state"].astype("string").str.strip()
)

numeric_columns = [
    "normal_charging_points",
    "fast_charging_points",
    "total_charging_points",
    "previous_year_total",
    "annual_change_pct"
]

for col in numeric_columns:
    states[col] = pd.to_numeric(states[col], errors="coerce")

states = states.dropna(subset=["federal_state"])
states = states.drop_duplicates(subset=["federal_state"])


history_raw = pd.read_excel(
    RAW_FILE,
    sheet_name=" 3.1 Charging points",
    header=None
)

dates = pd.to_datetime(
    history_raw.iloc[6, 5:44],
    errors="coerce"
)

history_parts = []

for excel_row, category in [
    (7, "normal"),
    (8, "fast"),
    (9, "total")
]:
    values = pd.to_numeric(
        history_raw.iloc[excel_row, 5:44],
        errors="coerce"
    )

    part = pd.DataFrame({
        "date": dates.to_numpy(),
        "charging_type": category,
        "charging_points": values.to_numpy()
    })

    history_parts.append(part)

history = pd.concat(history_parts, ignore_index=True)
history = history.dropna(subset=["date", "charging_points"])

district_raw = pd.read_excel(
    RAW_FILE,
    sheet_name=" 4.3 charging points per circle",
    header=None
)

districts = district_raw.iloc[8:409, [4, 5, 120, 121, 122]].copy()

districts.columns = [
    "district",
    "federal_state",
    "normal_charging_points",
    "fast_charging_points",
    "total_charging_points"
]

districts["district"] = (
    districts["district"].astype("string").str.strip()
)

districts["federal_state"] = (
    districts["federal_state"].astype("string").str.strip()
)

district_numeric = [
    "normal_charging_points",
    "fast_charging_points",
    "total_charging_points"
]

for col in district_numeric:
    districts[col] = pd.to_numeric(districts[col], errors="coerce")

districts = districts.dropna(
    subset=["district", "federal_state", "total_charging_points"]
)


states.to_csv(
    OUTPUT_DIR / "charging_points_by_state.csv",
    index=False
)

history.to_csv(
    OUTPUT_DIR / "historical_charging_points.csv",
    index=False,
    date_format="%Y-%m-%d"
)

districts.to_csv(
    OUTPUT_DIR / "charging_points_by_district.csv",
    index=False
)



print("\nCLEANING COMPLETE")
print("=" * 40)

for name, df in [
    ("States", states),
    ("Historical data", history),
    ("Districts", districts)
]:
    print(f"\n{name}")
    print("Rows:", len(df))
    print("Columns:", list(df.columns))
    print("Missing values:")
    print(df.isna().sum().to_dict())

print("\nTop 5 states by charging points:")
print(
    states.sort_values(
        "total_charging_points",
        ascending=False
    )[["federal_state", "total_charging_points"]].head(5)
)

print("\nFiles saved to:", OUTPUT_DIR)