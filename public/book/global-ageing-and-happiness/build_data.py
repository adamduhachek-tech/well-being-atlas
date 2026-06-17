# -*- coding: utf-8 -*-
"""
Build data.json for "The Two Clocks of Growing Old" — global ageing & the
experiential texture of well-being.

Construct: chiefly EXPERIENTIAL (yesterday-affect binaries: worry, stress,
anger, sadness, enjoyment, physical pain; plus the pos/neg affect indices and
social support / health-limits), set against the EVALUATIVE ladder for contrast.
Never conflated — each series is tagged.

Weighting (per DATA_MANIFEST):
  - Within a country: Gallup within-country weight `wgt`.
  - Across countries (global / income-group / region age profiles):
    population-weight per-country band means by `ctry_pop_millions`.

Pooled 2005-2020. Gallup WORLD affect items have ~95% coverage and, unlike the
Gallup US Daily file, no 2013 sampling break (checked in explore.py); they are
safe to profile by age across the whole pooled period.

Run from this directory:  python build_data.py  ->  data.json
"""
import json
import numpy as np
import pandas as pd

SRC = "../../data/gallup_world.parquet"
OUT = "data.json"

ITEMS = ["ladder", "pos_affect", "neg_affect", "worry", "stress", "anger",
         "sadness", "enjoyment", "physical_pain", "social_support",
         "health_limits", "well_rested"]
CONSTRUCT = {
    "ladder": "evaluative", "pos_affect": "experiential", "neg_affect": "experiential",
    "worry": "experiential", "stress": "experiential", "anger": "experiential",
    "sadness": "experiential", "enjoyment": "experiential",
    "physical_pain": "experiential", "social_support": "social",
    "health_limits": "health", "well_rested": "experiential",
}

COLS = ["age", "iso3", "region_global", "wgt", "ctry_pop_millions",
        "ctry_income_group"] + ITEMS
df = pd.read_parquet(SRC, columns=COLS)
df = df.dropna(subset=["age", "wgt"])
df = df[(df.age >= 15) & (df.age <= 99)]
df["wgt"] = df["wgt"].clip(lower=0)

BANDS = [(15, 24, "15-24"), (25, 34, "25-34"), (35, 44, "35-44"),
         (45, 54, "45-54"), (55, 64, "55-64"), (65, 99, "65+")]
ORDER = [b[2] for b in BANDS]
def band_of(a):
    for lo, hi, lab in BANDS:
        if lo <= a <= hi:
            return lab
df["band"] = df["age"].map(band_of)

INCOME_ORDER = ["Low income", "Lower middle income",
                "Upper middle income", "High income"]


def wmean(d, col):
    sub = d.dropna(subset=[col])
    w = sub["wgt"].to_numpy()
    if w.sum() <= 0:
        return np.nan
    return float((sub[col].to_numpy() * w).sum() / w.sum())


# ---- per (iso3, band) weighted means + pop/region/income -------------------
recs = []
for iso, g in df.groupby("iso3"):
    pop = g["ctry_pop_millions"].iloc[0]
    region = g["region_global"].iloc[0]
    inc = g["ctry_income_group"].iloc[0]
    for lab in ORDER:
        sub = g[g["band"] == lab]
        if len(sub) < 80:                       # suppress thin band cells
            continue
        rec = dict(iso3=iso, band=lab, n=int(len(sub)),
                   pop=None if pd.isna(pop) else float(pop),
                   region=region, income=inc)
        for it in ITEMS:
            rec[it] = wmean(sub, it)
        recs.append(rec)
cb = pd.DataFrame(recs)


def popweight_profile(frame, item):
    """population-weighted band profile for `item` over the rows in `frame`."""
    out = []
    for lab in ORDER:
        s = frame[(frame.band == lab) & frame[item].notna() & frame["pop"].notna()
                  & (frame["pop"] > 0)]
        if len(s) == 0:
            out.append(None)
            continue
        out.append(round(float((s["pop"] * s[item]).sum() / s["pop"].sum()), 4))
    return out


# ---- GLOBAL age profiles for every item ------------------------------------
global_profiles = {it: popweight_profile(cb, it) for it in ITEMS}

# young->old change per item (15-24 vs 65+)
changes = {}
for it in ITEMS:
    p = global_profiles[it]
    if p[0] is not None and p[-1] is not None:
        changes[it] = round(p[-1] - p[0], 4)

# peak band per item (where in life it is highest / lowest)
peaks = {}
for it in ITEMS:
    p = [(ORDER[i], v) for i, v in enumerate(global_profiles[it]) if v is not None]
    peaks[it] = dict(max_band=max(p, key=lambda t: t[1])[0],
                     min_band=min(p, key=lambda t: t[1])[0])

# ---- WORRY / STRESS / PAIN by income group x band --------------------------
by_income = {}
for it in ["worry", "stress", "physical_pain", "enjoyment", "ladder"]:
    by_income[it] = {}
    for inc in INCOME_ORDER:
        frame = cb[cb.income == inc]
        by_income[it][inc] = popweight_profile(frame, it)

# ---- SOCIAL SUPPORT (and pain) by region x band ----------------------------
REGIONS = sorted(cb["region"].dropna().unique().tolist())
by_region = {}
for it in ["social_support", "physical_pain"]:
    by_region[it] = {}
    for reg in REGIONS:
        frame = cb[cb.region == reg]
        by_region[it][reg] = popweight_profile(frame, it)

# region social-support summary (old-age level + midlife dip recovery)
soc_summary = []
for reg in REGIONS:
    p = by_region["social_support"][reg]
    if None in p:
        continue
    young, old = p[0], p[-1]
    trough = min(p)
    soc_summary.append(dict(region=reg, young=young, old=old, trough=round(trough, 3),
                            old_minus_trough=round(old - trough, 3),
                            old_level=old))
soc_summary.sort(key=lambda r: r["old_level"], reverse=True)

# ---- headline N ------------------------------------------------------------
n_total = int(len(df))
n_countries = int(cb["iso3"].nunique())

out = dict(
    meta=dict(
        title="The Two Clocks of Growing Old",
        dataset="Gallup World Poll",
        years="2005-2020",
        weight="within-country wgt; cross-country population-weighted by ctry_pop_millions",
        construct_note="Experiential yesterday-affect (worry/stress/anger/sadness/"
                       "enjoyment/pain) and social/health items, contrasted with the "
                       "evaluative ladder. Tagged per series; never conflated.",
        affect_note="Unlike Gallup US Daily, the Gallup World affect items have ~95% "
                    "coverage with no 2013 break; safe to profile by age over the pooled period.",
        n_interviews=n_total,
        n_countries=n_countries,
        suppression="band cells with raw N<80 suppressed before aggregation",
    ),
    bands=ORDER,
    construct=CONSTRUCT,
    item_labels={
        "ladder": "Life rating (ladder, 0-10)",
        "pos_affect": "Positive affect index",
        "neg_affect": "Negative affect index",
        "worry": "Worry",
        "stress": "Stress",
        "anger": "Anger",
        "sadness": "Sadness",
        "enjoyment": "Enjoyment",
        "physical_pain": "Physical pain",
        "social_support": "Has someone to count on",
        "health_limits": "Health limits daily activity",
        "well_rested": "Well-rested",
    },
    global_profiles=global_profiles,
    changes=changes,
    peaks=peaks,
    by_income=by_income,
    income_order=INCOME_ORDER,
    by_region=by_region,
    region_order=REGIONS,
    soc_summary=soc_summary,
)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

print("wrote", OUT, "| interviews", f"{n_total:,}", "| countries", n_countries)
print("\nGLOBAL age profiles (share reporting yesterday, or index):")
print(f"{'item':<16}" + "".join(f"{l:>8}" for l in ORDER) + "   chg")
for it in ITEMS:
    p = global_profiles[it]
    s = "".join(f"{(v if v is not None else float('nan')):>8.3f}" for v in p)
    print(f"{it:<16}{s}  {changes.get(it, float('nan')):+.3f}")
print("\nWorry by income group x band:")
for inc in INCOME_ORDER:
    p = by_income["worry"][inc]
    print(f"  {inc:<22}" + "".join(f"{v:>8.3f}" for v in p))
print("\nSocial support by region (old-age level desc):")
for r in soc_summary:
    print(f"  {r['region'][:30]:<31} young {r['young']:.2f}  trough {r['trough']:.2f}  old {r['old']:.2f}")
