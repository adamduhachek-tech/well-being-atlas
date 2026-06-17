"""
Build data.json for "The U-Curve Across Countries".

Question: does life-evaluation (Cantril ladder) trace a midlife-dip U over age,
and where / why does the shape differ across countries?

Weighting (per DATA_MANIFEST):
  - Within a country: weight by `wgt` (Gallup within-country weight).
  - Across countries (regional / group / global age profiles): population-weight
    the per-country band means by `ctry_pop_millions`. Never an unweighted mean
    of country means.

All figures here are EVALUATIVE (Cantril ladder 0-10). Pooled across 2005-2020
to maximise age coverage per country (the shape is treated as a structural,
not a time-trend, feature; the time dimension is handled in other articles).

Run from this directory:  python build_data.py  ->  data.json
"""
import json
import numpy as np
import pandas as pd

SRC = "../../data/gallup_world.parquet"
OUT = "data.json"

COLS = ["ladder", "age", "country", "iso3", "region_global", "wgt",
        "ctry_gni_percap", "ctry_hdi", "ctry_pop_millions", "year"]

df = pd.read_parquet(SRC, columns=COLS)
df = df.dropna(subset=["ladder", "age", "iso3", "wgt"])
df = df[(df.age >= 15) & (df.age <= 99)]
df["wgt"] = df["wgt"].clip(lower=0)

# ---- age bands -------------------------------------------------------------
BANDS = [(15, 24, "15-24", 20), (25, 34, "25-34", 30), (35, 44, "35-44", 40),
         (45, 54, "45-54", 50), (55, 64, "55-64", 60), (65, 99, "65+", 72)]
def band_of(a):
    for lo, hi, lab, mid in BANDS:
        if lo <= a <= hi:
            return lab
    return None
df["band"] = df["age"].map(band_of)
BAND_MID = {lab: mid for _, _, lab, mid in BANDS}
BAND_ORDER = [lab for _, _, lab, _ in BANDS]


def wmean(d, col="ladder", w="wgt"):
    ww = d[w].to_numpy()
    s = ww.sum()
    if s <= 0:
        return np.nan
    return float((d[col].to_numpy() * ww).sum() / s)


# ---- per country x band weighted ladder mean -------------------------------
rows = []
for iso, g in df.groupby("iso3"):
    if g["wgt"].sum() <= 0:
        continue
    country = g["country"].iloc[0]
    region = g["region_global"].iloc[0]
    pop = g["ctry_pop_millions"].iloc[0]
    gni = g["ctry_gni_percap"].iloc[0]
    hdi = g["ctry_hdi"].iloc[0]
    band_means = {}
    band_n = {}
    for lab in BAND_ORDER:
        sub = g[g["band"] == lab]
        if len(sub) >= 80:                 # suppress thin band cells
            band_means[lab] = wmean(sub)
            band_n[lab] = int(len(sub))
    rows.append(dict(iso3=iso, country=country, region=region, pop=pop,
                     gni=gni, hdi=hdi, n=int(len(g)),
                     band_means=band_means, band_n=band_n))

countries = pd.DataFrame(rows)

# ---- per-country shape metrics ---------------------------------------------
def shape_metrics(bm):
    """bm: dict band->mean. Returns young/mid/old, arms, turning point, class."""
    need = ["15-24", "25-34", "35-44", "45-54", "55-64", "65+"]
    if not all(k in bm for k in need):
        return None
    young = bm["15-24"]
    # midlife trough: lowest of the 35-44 / 45-54 / 55-64 region
    mid_region = {k: bm[k] for k in ["35-44", "45-54", "55-64"]}
    mid_lab = min(mid_region, key=mid_region.get)
    mid = mid_region[mid_lab]
    old = bm["65+"]
    left_arm = young - mid          # >0 => young happier than midlife (left up)
    right_arm = old - mid           # >0 => old recovers above midlife (right up)
    # classification
    if right_arm >= 0.15 and left_arm >= 0.0:
        cls = "U-shape"             # both arms up: classic midlife dip + rebound
    elif right_arm >= 0.15 and left_arm < 0.0:
        cls = "Uphill"             # rises with age, no real youth advantage
    elif right_arm <= -0.15:
        cls = "Decline"            # falls with age, old age the unhappiest
    else:
        cls = "Flat"
    return dict(young=young, mid=mid, mid_lab=mid_lab, old=old,
                left_arm=left_arm, right_arm=right_arm, cls=cls)


def quad_turn(g):
    """Weighted quadratic ladder~age+age^2; return (convex, turn_age, b2)."""
    a = g["age"].to_numpy(float)
    y = g["ladder"].to_numpy(float)
    w = np.sqrt(g["wgt"].to_numpy(float))
    ac = a - 50.0                                    # center age to stabilise
    X = np.vstack([np.ones_like(ac), ac, ac**2]).T
    Xw = X * w[:, None]
    yw = y * w
    coef, *_ = np.linalg.lstsq(Xw, yw, rcond=None)
    b0, b1, b2 = coef
    convex = b2 > 0
    turn = np.nan
    if abs(b2) > 1e-9:
        turn = 50.0 - b1 / (2 * b2)                  # vertex in original age units
    return bool(convex), float(turn), float(b2)


metrics = []
for _, r in countries.iterrows():
    if r["n"] < 2500:
        continue
    sm = shape_metrics(r["band_means"])
    if sm is None:
        continue
    g = df[df.iso3 == r["iso3"]]
    convex, turn, b2 = quad_turn(g)
    metrics.append(dict(iso3=r["iso3"], country=r["country"], region=r["region"],
                        pop=None if pd.isna(r["pop"]) else float(r["pop"]),
                        gni=None if pd.isna(r["gni"]) else float(r["gni"]),
                        hdi=None if pd.isna(r["hdi"]) else float(r["hdi"]),
                        n=r["n"], **sm,
                        convex=convex, turn=round(turn, 1) if not np.isnan(turn) else None,
                        b2=b2,
                        band_means={k: round(v, 3) for k, v in r["band_means"].items()}))

M = pd.DataFrame(metrics)
print(f"countries with full age profile & N>=2500: {len(M)}")
print(M["cls"].value_counts())

# ---- correlation: old-age recovery (right_arm) vs national income/HDI ------
mm = M.dropna(subset=["gni"]).copy()
mm["loggni"] = np.log(mm["gni"])
def wcorr(x, y, w):
    w = np.asarray(w, float); x = np.asarray(x, float); y = np.asarray(y, float)
    mx = np.average(x, weights=w); my = np.average(y, weights=w)
    cov = np.average((x-mx)*(y-my), weights=w)
    vx = np.average((x-mx)**2, weights=w); vy = np.average((y-my)**2, weights=w)
    return float(cov/np.sqrt(vx*vy))
popw = mm["pop"].fillna(mm["pop"].median()).to_numpy()
corr_recovery_gni = wcorr(mm["loggni"], mm["right_arm"], popw)
corr_recovery_hdi = wcorr(mm.dropna(subset=["hdi"])["hdi"],
                          mm.dropna(subset=["hdi"])["right_arm"],
                          mm.dropna(subset=["hdi"])["pop"].fillna(mm["pop"].median()))
corr_recovery_gni_unw = float(np.corrcoef(mm["loggni"], mm["right_arm"])[0, 1])
print("corr(right_arm, log GNI) popw:", round(corr_recovery_gni, 3),
      " unweighted:", round(corr_recovery_gni_unw, 3))
print("corr(right_arm, HDI) popw:", round(corr_recovery_hdi, 3))

# OLS fit line for scatter (unweighted, on log GNI)
b1, b0 = np.polyfit(mm["loggni"], mm["right_arm"], 1)
print("fit right_arm = %.3f + %.3f*logGNI" % (b0, b1))

# ---- regional population-weighted age profiles -----------------------------
region_profiles = {}
for region, g in countries.groupby("region"):
    prof = []
    for lab in BAND_ORDER:
        num = 0.0; den = 0.0; nc = 0
        for _, r in g.iterrows():
            bm = r["band_means"]
            if lab in bm and not pd.isna(r["pop"]) and r["pop"] > 0:
                num += r["pop"] * bm[lab]; den += r["pop"]; nc += 1
        if den > 0 and nc >= 2:
            prof.append(dict(band=lab, mid=BAND_MID[lab],
                             ladder=round(num/den, 3), n_countries=nc))
    if len(prof) == len(BAND_ORDER):
        region_profiles[region] = prof

# region summary (recovery etc.) for ranking
region_summary = []
for region, prof in region_profiles.items():
    d = {p["band"]: p["ladder"] for p in prof}
    midlab = min(["35-44", "45-54", "55-64"], key=lambda k: d[k])
    region_summary.append(dict(
        region=region, young=d["15-24"], mid=d[midlab], mid_lab=midlab,
        old=d["65+"], right_arm=round(d["65+"]-d[midlab], 3),
        left_arm=round(d["15-24"]-d[midlab], 3),
        overall=round(sum(d.values())/len(d), 3)))
region_summary.sort(key=lambda r: r["right_arm"], reverse=True)

# ---- thematic group aggregates (population-weighted) -----------------------
GROUPS = {
    "Anglosphere": ["USA", "GBR", "AUS", "CAN", "IRL", "NZL"],
    "Post-Soviet states": ["RUS", "UKR", "BLR", "MDA", "GEO", "ARM", "AZE",
                            "KAZ", "KGZ", "TJK", "UZB", "TKM", "LTU", "LVA",
                            "EST"],
    "Western Europe": ["DEU", "FRA", "ESP", "ITA", "NLD", "BEL", "AUT", "CHE",
                       "PRT", "GRC", "SWE", "NOR", "DNK", "FIN"],
    "Latin America": ["BRA", "MEX", "COL", "ARG", "CHL", "PER", "VEN", "ECU",
                      "BOL", "GTM", "URY", "DOM", "CRI", "PRY"],
}
def group_profile(isos):
    rows_g = countries[countries["iso3"].isin(isos)]
    prof = []
    for lab in BAND_ORDER:
        num = 0.0; den = 0.0; nc = 0
        for _, r in rows_g.iterrows():
            bm = r["band_means"]
            if lab in bm and not pd.isna(r["pop"]) and r["pop"] > 0:
                num += r["pop"] * bm[lab]; den += r["pop"]; nc += 1
        if den > 0:
            prof.append(dict(band=lab, mid=BAND_MID[lab],
                             ladder=round(num/den, 3), n_countries=nc))
    return prof
group_profiles = {g: group_profile(isos) for g, isos in GROUPS.items()}

# ---- global population-weighted age profile --------------------------------
global_profile = []
for lab in BAND_ORDER:
    num = 0.0; den = 0.0; nc = 0
    for _, r in countries.iterrows():
        bm = r["band_means"]
        if lab in bm and not pd.isna(r["pop"]) and r["pop"] > 0:
            num += r["pop"] * bm[lab]; den += r["pop"]; nc += 1
    global_profile.append(dict(band=lab, mid=BAND_MID[lab],
                               ladder=round(num/den, 3), n_countries=nc))

# ---- exemplar countries for small multiples --------------------------------
EXEMPLARS = ["USA", "GBR", "AUS", "CAN",            # Anglo U-shape
             "DEU", "FRA", "ESP",                    # W Europe
             "RUS", "UKR", "GEO",                    # post-Soviet decline
             "BRA", "MEX", "COL",                    # Latin America
             "ZWE", "TZA", "UGA",                    # Sub-Saharan Africa
             "IND", "CHN", "JPN", "KOR"]             # Asia
ex_rows = []
mbyiso = {r["iso3"]: r for r in metrics}
for iso in EXEMPLARS:
    if iso in mbyiso:
        r = mbyiso[iso]
        ex_rows.append(dict(iso3=iso, country=r["country"], region=r["region"],
                            band_means=r["band_means"], cls=r["cls"],
                            right_arm=round(r["right_arm"], 3),
                            left_arm=round(r["left_arm"], 3),
                            turn=r["turn"], gni=r["gni"]))

# headline numbers
n_total = int(df.shape[0])
n_countries_used = int(len(M))

out = dict(
    meta=dict(
        title="The U-Curve, Redrawn",
        dataset="Gallup World Poll",
        years="2005-2020",
        construct="evaluative (Cantril ladder, 0-10)",
        weight="within-country wgt; cross-country population-weighted by ctry_pop_millions",
        note="Age profiles pool all survey years to maximise per-country age coverage; "
             "band cells with raw N<80 suppressed; only countries with all six age "
             "bands present and total N>=2500 enter the cross-country comparison.",
        n_interviews=n_total,
        n_countries=n_countries_used,
    ),
    bands=BAND_ORDER,
    band_mid=BAND_MID,
    global_profile=global_profile,
    region_profiles=region_profiles,
    group_profiles=group_profiles,
    region_summary=region_summary,
    countries=metrics,                 # full list with shape metrics
    scatter=dict(
        corr_recovery_loggni_popw=round(corr_recovery_gni, 3),
        corr_recovery_loggni_unw=round(corr_recovery_gni_unw, 3),
        corr_recovery_hdi_popw=round(corr_recovery_hdi, 3),
        fit_intercept=round(float(b0), 4),
        fit_slope=round(float(b1), 4),
        points=[dict(iso3=r["iso3"], country=r["country"], region=r["region"],
                     loggni=round(float(np.log(r["gni"])), 3),
                     gni=r["gni"], right_arm=round(r["right_arm"], 3),
                     cls=r["cls"], pop=r["pop"])
                for r in metrics if r["gni"]],
    ),
    exemplars=ex_rows,
    class_counts={k: int(v) for k, v in M["cls"].value_counts().items()},
)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
print("wrote", OUT)
print("class counts:", out["class_counts"])
print("\nregion summary (by old-age recovery):")
for r in region_summary:
    print(f"  {r['region']:<38} young {r['young']:.2f}  trough({r['mid_lab']}) {r['mid']:.2f}  "
          f"old {r['old']:.2f}  recovery {r['right_arm']:+.2f}")
