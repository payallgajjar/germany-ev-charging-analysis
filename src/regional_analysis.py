from pathlib import Path
import pandas as pd 
import matplotlib.pyplot as plt

PROJECT_DIR=Path(__file__).resolve().parent.parent
DATA_DIR=PROJECT_DIR/"data"/"processed"
VISUALS_DIR=PROJECT_DIR/"visuals"
OUTPUT_DIR=DATA_DIR
VISUALS_DIR.mkdir(parents=True,exist_ok=True)


states = pd.read_csv(DATA_DIR / "charging_points_by_state.csv")
districts = pd.read_csv(DATA_DIR / "charging_points_by_district.csv")

states["charging_point_share_pct"]=(states["total_charging_points"]/
                                    states["total_charging_points"].sum()*100)
states["fast_charging_share_pct"]=(states["fast_charging_points"]/
                                   states["total_charging_points"]*100)
states["normal_charging_share_pct"]=(states["normal_charging_points"]/
                                     states["total_charging_points"]*100)

states["annual_increase_points"]=(states["total_charging_points"]-states["previous_year_total"])
states["charging_share_check_pct"]=(states["normal_charging_share_pct"]+states["fast_charging_share_pct"])

print("\nCHARGING MIX VALIDATION")
print("="*50)

print(states[["federal_state","normal_charging_share_pct","fast_charging_share_pct","charging_share_check_pct"]]
      .round(2).to_string(index=False))


top_states=states.nlargest(10,"total_charging_points")

print("\nTOP 10 FEDERAL STATES")
print("="*50)

print(top_states[[ "federal_state","total_charging_points","charging_point_share_pct","fast_charging_share_pct",]]
            .round(2).to_string(index=False))

fast_share_ranking=states.sort_values("fast_charging_share_pct",ascending=False)

print("\nSTATES RANKED BY FAST-CHARGING SHARE")
print("="*50)

print(fast_share_ranking[["federal_state","fast_charging_points","total_charging_points","fast_charging_share_pct"]]
      .round(2).to_string(index=False))

top_districts=districts.nlargest(10,"total_charging_points")
bottom_districts=districts.nsmallest(10,"total_charging_points")

print("\nTOP 10 DISTRICTS")
print("="*50)

print(top_districts[["district","federal_state","total_charging_points"]].round(2).to_string(index=False))
print("\nBOTTOM 10 DISTRICTS")
print("="*50)
print(bottom_districts[["district","federal_state","total_charging_points"]].round(2).to_string(index=False))


plt.figure(figsize=(12,7))
plt.barh(top_states[ "federal_state"].iloc[::-1],top_states["total_charging_points"].iloc[::-1],color="green")
plt.title("Top 10 German States by Charging Points")
plt.xlabel("Number of Charging Points")
plt.ylabel("Federal State")
plt.tight_layout()
plt.savefig(VISUALS_DIR / "top_10_states.png",dpi=150)
plt.show()
plt.close()


fast_chart=fast_share_ranking.sort_values("fast_charging_share_pct")
plt.figure(figsize=(12,7))
plt.barh(fast_chart["federal_state"],fast_chart["fast_charging_share_pct"],color="Purple")
plt.title("Fast-Charging Share by German Federal State")
plt.xlabel("Fast-Charging Points (%)")
plt.ylabel("Federal State")
plt.tight_layout()
plt.savefig(VISUALS_DIR / "fast_charging_share_by_state.png",dpi=150)
plt.show()
plt.close()

states.to_csv(OUTPUT_DIR/"state_analysis.csv",index=False)

top_districts.to_csv(OUTPUT_DIR/"top_10_districts.csv",index=False)

bottom_districts.to_csv(OUTPUT_DIR/"bottom_10_districts.csv",index=False)

states.to_csv(DATA_DIR / "state_analysis.csv",index=False)

print("\nSaved state_analysis.csv")

print("\nREGIONAL ANALYSIS COMPLETE")
print("Charts saved to:", VISUALS_DIR)
print("Analysis tables saved to:", OUTPUT_DIR)

"""## Regional Analysis — Key Findings

- North Rhine-Westphalia recorded the highest number of public charging points in the state overview, with 42,066.
- Bavaria ranked second with 40,874, followed by Baden-Württemberg with 35,963.
- North Rhine-Westphalia and Bavaria together accounted for approximately 38.7% of the charging points in the state-level dataset.
- Saxony-Anhalt had the highest fast-charging share among the 16 federal states, at 39.82%.
- Berlin, Hamburg, Stuttgart, Munich, and Hanover Region were among the leading districts by total charging points in the July 2026 district snapshot.
- District comparisons use a different reporting date from the current state overview. The dates must be considered when interpreting differences.

**Limitation:** These findings compare absolute charging-point counts and charging-type shares. 
They do not measure infrastructure adequacy, accessibility, utilization, or charging points per electric vehicle.
"""


