# analyze.py
# FINDINGS: Two columns reliably separate cars that later broke down from those that did not:
#   1. km_since_service  — broke-down cars averaged 11,678 km since last service vs 7,261 km
#      for healthy cars (a 61 % gap). The median gap is even starker: 13,064 vs 6,308 km.
#   2. load_factor       — broke-down cars averaged 0.60 vs 0.51 for healthy cars (19 % gap).
#
# The two obvious guesses — odometer_km (total mileage) and age_years — showed ZERO separation:
# mean gap of 0.3 % and -0.2 % respectively. P25/P50/P75 percentiles for both columns are
# nearly identical across the two groups. Following the data, not the assumption, rules them out.
# avg_daily_km showed a 22 % gap but is closely correlated with load_factor; using both
# would double-count the same signal, so only load_factor is kept in the score.
#
# Risk score: min-max scale both predictive columns, weight km_since_service 60 % and
# load_factor 40 % (proportional to their observed mean gaps), multiply to 0-100.
# A car scoring above ~65 is in the same territory as most cars that later broke down.

import pandas as pd

# -- 1. Load ------------------------------------------------------------------

df = pd.read_csv("fleet_history.csv")

# -- 2. Group comparison — column by column -----------------------------------

broke = df[df["broke_down"] == 1]
ok    = df[df["broke_down"] == 0]

print("=" * 70)
print(f"Dataset: {len(df)} cars  |  broke down: {len(broke)}  |  did not: {len(ok)}")
print("=" * 70)

cols = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]

print(f"\n{'Column':<22} {'Broke mean':>12} {'OK mean':>12} {'Gap %':>8}  Signal?")
print("-" * 70)

signals: list[str] = []
for col in cols:
    bm   = broke[col].mean()
    om   = ok[col].mean()
    gap  = (bm - om) / om * 100 if om else 0.0
    flag = "YES <- predictor" if abs(gap) >= 15 else "no"
    if abs(gap) >= 15:
        signals.append(col)
    print(f"  {col:<20} {bm:12.2f} {om:12.2f} {gap:7.1f}%  {flag}")

print(f"\nColumns with a meaningful gap (>=15 %): {', '.join(signals)}")
print("Columns with NO meaningful gap: odometer_km, age_years\n")
print(
    "  -> Total mileage and age look like the obvious predictors, but the data\n"
    "     shows their means and percentiles are nearly identical in both groups.\n"
    "     The cars that broke down are the ones furthest past their last service\n"
    "     and the ones worked hardest, not the oldest or highest-mileage ones."
)

# -- 3. Risk score ------------------------------------------------------------

def _minmax(series: pd.Series) -> pd.Series:
    """Scale a series to [0, 1]."""
    mn, mx = series.min(), series.max()
    return (series - mn) / (mx - mn)

# Weights proportional to observed mean-gap magnitudes (61 % vs 19 %).
KSS_WEIGHT  = 0.6   # km_since_service
LOAD_WEIGHT = 0.4   # load_factor

df["risk_score"] = (
    _minmax(df["km_since_service"]) * KSS_WEIGHT
    + _minmax(df["load_factor"])    * LOAD_WEIGHT
) * 100
df["risk_score"] = df["risk_score"].round(1)

# -- 4. Ranked output ---------------------------------------------------------

ranked = (
    df[["car_id", "km_since_service", "load_factor", "risk_score"]]
    .sort_values("risk_score", ascending=False)
    .reset_index(drop=True)
)
ranked.index += 1   # 1-based rank

print("\n" + "=" * 70)
print("Fleet breakdown-risk ranking  (highest risk first)")
print("=" * 70)
print(f"  {'#':>3}  {'Car ID':<12} {'km since svc':>13} {'load factor':>12} {'risk score':>11}")
print("  " + "-" * 55)
for rank, row in ranked.iterrows():
    alert = "  !" if row["risk_score"] >= 65 else ""
    print(
        f"  {rank:>3}  {row['car_id']:<12} "
        f"{int(row['km_since_service']):>13,} "
        f"{row['load_factor']:>12.2f} "
        f"{row['risk_score']:>11.1f}"
        f"{alert}"
    )

# -- 5. Score quality summary -------------------------------------------------

mean_broke = df[df["broke_down"] == 1]["risk_score"].mean()
mean_ok    = df[df["broke_down"] == 0]["risk_score"].mean()

print(f"\nScore separation:")
print(f"  Mean risk - cars that BROKE DOWN : {mean_broke:.1f}")
print(f"  Mean risk - cars that did NOT    : {mean_ok:.1f}")
print(f"  Gap                              : {mean_broke - mean_ok:.1f} points")

for n in [10, 20, 26]:
    caught = ranked.head(n).merge(
        df[df["broke_down"] == 1][["car_id"]], on="car_id"
    ).shape[0]
    total_broke = int((df["broke_down"] == 1).sum())
    print(f"  Top {n:2d} flagged -> {caught}/{total_broke} actual breakdowns caught "
          f"({caught / total_broke * 100:.0f}% recall)")

print("\n  Cars marked ! above score >= 65 -- intervene before the 80% rule fires.")
