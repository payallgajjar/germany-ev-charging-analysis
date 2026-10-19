from pathlib import Path
import pandas as pd 
import matplotlib.pyplot as plt

PROJECT_DIR=Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "processed"
VISUALS_DIR = PROJECT_DIR / "visuals"

VISUALS_DIR.mkdir(parents=True, exist_ok=True)

states = pd.read_csv(DATA_DIR / "charging_points_by_state.csv")

history = pd.read_csv(DATA_DIR / "historical_charging_points.csv",parse_dates=["date"])

districts = pd.read_csv(DATA_DIR / "charging_points_by_district.csv")

print("\nDATASET DIMENSIONS")
print("=" * 40)

print("States:", states.shape)
print("Historical data:", history.shape)
print("Districts:", districts.shape)

print("\n MISSING VALUES")
print("="*40)

print("\nStates:")
print(states.isna().sum())
print("\nHistorical Data:")
print(history.isna().sum())
print("\nDistricts:")
print(districts.isna().sum())

latest_date=history["date"].max()

latest_total = history.loc[(history["date"] == latest_date)
    & (history["charging_type"] == "total"),"charging_points"].sum()
first_total= history.loc[(history["date"]==history["date"].min())
    & (history["charging_type"]=="total"),"charging_points"].sum()

growth_pct=((latest_total-first_total)/first_total)*100

print("\nHISTORICAL KPIs")
print("="*40)
print("First recorded date:",history["date"].min().date())
print("Last recorded date:",latest_date.date())
print("Charging points at first date:",int(first_total))
print("Charging points at last date:",int(latest_total))
print(f"Growth since first date: {growth_pct:.2f}%")


states=states.sort_values("total_charging_points",ascending=False)

print("\n TOP 5 FEDERAL STATES")
print("="*40)

print(states[["federal_state","total_charging_points"]].head(5).to_string(index=False))

print("\n BOTTOM 5 FEDERAL STATES")
print("="*40)

print(states.sort_values("total_charging_points",ascending=True)
      [["federal_state","total_charging_points"]].head(5).to_string(index=False))

total_history= history[history["charging_type"]=="total"].sort_values("date")

plt.figure(figsize=(12,6))
plt.plot(
    total_history["date"],
    total_history["charging_points"],marker="o",linewidth=2,color="Red")
plt.title("Growth of Public EV Charging Points in Germany")
plt.xlabel("Date")
plt.ylabel("Number of Charging Points")
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(VISUALS_DIR / "total_charging_points_growth.png",dpi=150)

plt.show()
plt.close()

charging_comparison=history[history["charging_type"].isin(["normal","fast"])
                    ].pivot(index="date",columns="charging_type",
                            values="charging_points").sort_index()
plt.figure(figsize=(12,6))
plt.plot(charging_comparison.index,charging_comparison["normal"],label="Normal charging points",
         marker="o",color="Pink")
plt.plot(charging_comparison.index,charging_comparison["fast"],label="Fast charging points",
         marker="s",color="Purple")
plt.title("Normal vs Fast Charging Points in Germany")
plt.xlabel("Date")
plt.ylabel("Number of Charging Points")
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    VISUALS_DIR / "normal_vs_fast_charging.png",
    dpi=150
)

plt.show()
plt.close()

print("\n ANALYSIS COMPLETE")
print("Charts saved in:",VISUALS_DIR)


print("\n DATA QUALITY CHECK")
print("="*40)

print("\n Duplicate States records:", states.duplicated(subset=["federal_state"]).sum())
print("Duplicate Historical records:",history.duplicated(subset=["date","charging_type"]).sum())
print("Duplicate District records:",districts.duplicated(subset=["district", "federal_state"]).sum())

print("\nNegative values in State totals:",(states["total_charging_points"] < 0).sum())
print("Negative values in Historical data:",(history["charging_points"]<0).sum())
print("Negative values in District total:",(districts["total_charging_points"]<0).sum())

states_difference=(states["normal_charging_points"]+states["fast_charging_points"]-states["total_charging_points"])

print("\nStates where normal + fast != total:",(states_difference.abs() > 0.01).sum())

district_difference = (districts["normal_charging_points"] + districts["fast_charging_points"]
                       - districts["total_charging_points"])
print("Districts where normal + fast != total:",(district_difference.abs()>0.01).sum())

history_wide = history.pivot(index="date",columns="charging_type",values="charging_points")
history_difference = (history_wide["normal"]+ history_wide["fast"]- history_wide["total"])

print("Historical data where normal+fast != total:",(history_difference.abs()>0.01).sum())

print("\n State total:",states["total_charging_points"].sum())
print("District total:",districts["total_charging_points"].sum())

print("\n DATA QUALITY CHECKS COMPLETE")


