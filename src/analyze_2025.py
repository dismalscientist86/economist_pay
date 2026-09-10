"""
The 2025 update: has the number and pay of federal economists changed?

Compares OPM FedScope's September 2024 and (preliminary) March 2025 snapshots
of occupational series 0110, using the tables built by clean_fedscope.py. All
outputs go to output/tables/ with a `fedscope_` prefix; src/make_figures.py
turns them into the slide-deck figures.

Read docs/2025_update_plan.md for the full method and caveats. In brief:
  - 6-month window, not 12.
  - March 2025 is preliminary and still counts administrative-leave / deferred-
    resignation staff as employed, so headcount loss is understated.
  - No gender.
  - No record-level September 2024: totals and mean pay are exact, but the
    agency/grade breakdown covers only ~76% of economists (small cells
    suppressed on both dates), and the September 2024 pay distribution is not
    available.

Usage:
    python src/analyze_2025.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

PROCESSED = Path(__file__).parent.parent / "data" / "processed"
TABLES = Path(__file__).parent.parent / "output" / "tables"

SNAP0, SNAP1 = 202409, 202503  # September 2024, March 2025

# --------------------------------------------------------------------------
# Reference constants (documented, so the module stays offline/reproducible)
# --------------------------------------------------------------------------
# BLS, retrieved 2026-09-09 via the public API.
#   CPI-U, U.S. city average, all items, NSA (CUUR0000SA0, 1982-84=100)
#   ECI, wages & salaries, all civilian workers (CIU2020000000000I, Dec 2005=100)
CPI_U = {202409: 315.301, 202503: 319.799}          # monthly
ECI_WAGES = {202409: 169.1, 202503: 171.9}          # 2024 Q3, 2025 Q1

# January 2025 federal pay adjustment (Executive Order 14139, Dec 23 2024):
# 1.7% across-the-board base increase + 0.3% average locality = 2.0% overall.
GS_RAISE_2025 = 0.020

# FedsDataCenter historical panel (FY2015-2024) is a different universe
# (annual FOIA extract vs. EHRI month-end status). Used only for long-run
# context on the trend charts, always labelled as a source break.


# --------------------------------------------------------------------------
# Loaders
# --------------------------------------------------------------------------

def _load(name: str, **kw) -> pd.DataFrame:
    path = PROCESSED / name
    if not path.exists():
        raise FileNotFoundError(f"{path} missing. Run: python src/clean_fedscope.py")
    return pd.read_csv(path, **kw)


def load_records() -> pd.DataFrame:
    """Record-level March 2025 economists (series 0110 only)."""
    df = _load("fedscope_economists_202503.csv",
               dtype={"series": str, "grade": str})
    return df[df["series_label"] == "economist"].copy()


def load_totals() -> pd.DataFrame:
    df = _load("fedscope_economist_totals.csv", dtype={"series": str})
    return df[df["series_label"] == "economist"].set_index("snapshot")


def load_cells() -> pd.DataFrame:
    df = _load("fedscope_economist_cells.csv", dtype={"series": str, "grade": str})
    return df[df["series_label"] == "economist"].copy()


def load_flows() -> pd.DataFrame:
    df = _load("fedscope_economist_flows.csv", dtype={"series": str, "grade": str})
    return df[df["series_label"] == "economist"].copy()


# --------------------------------------------------------------------------
# 1. Headcount and pay: the headline
# --------------------------------------------------------------------------

def headline(totals: pd.DataFrame) -> pd.DataFrame:
    h0, h1 = totals.loc[SNAP0, "headcount"], totals.loc[SNAP1, "headcount"]
    p0, p1 = totals.loc[SNAP0, "mean_salary"], totals.loc[SNAP1, "mean_salary"]
    l0, l1 = totals.loc[SNAP0, "mean_los"], totals.loc[SNAP1, "mean_los"]

    cpi_infl = CPI_U[SNAP1] / CPI_U[SNAP0] - 1
    eci_infl = ECI_WAGES[SNAP1] / ECI_WAGES[SNAP0] - 1

    rows = [
        ("headcount", h0, h1, h1 - h0, h1 / h0 - 1),
        ("mean_salary_nominal", p0, p1, p1 - p0, p1 / p0 - 1),
        ("mean_salary_real_cpi", p0, p1 / (1 + cpi_infl), p1 / (1 + cpi_infl) - p0,
         (p1 / (1 + cpi_infl)) / p0 - 1),
        ("mean_salary_real_eci", p0, p1 / (1 + eci_infl), p1 / (1 + eci_infl) - p0,
         (p1 / (1 + eci_infl)) / p0 - 1),
        ("mean_length_of_service", l0, l1, l1 - l0, l1 / l0 - 1),
    ]
    out = pd.DataFrame(rows, columns=["measure", "sep_2024", "mar_2025",
                                      "change", "pct_change"])
    out["change"] = out["change"].round(1)
    out["pct_change"] = out["pct_change"].round(4)
    out["cpi_inflation_6mo"] = round(cpi_infl, 4)
    out["eci_inflation_6mo"] = round(eci_infl, 4)
    _write(out, "fedscope_headline_2024_2025.csv", index=False)
    return out


# --------------------------------------------------------------------------
# 2. Long-run headcount / pay trend (FedsDataCenter 2015-2024 + FedScope)
# --------------------------------------------------------------------------

def trend(totals: pd.DataFrame) -> pd.DataFrame:
    rows = []
    panel_path = PROCESSED / "economists_panel.csv"
    if panel_path.exists():
        panel = pd.read_csv(panel_path)
        for yr, g in panel.groupby("fiscal_year"):
            pos = g[g["salary"] > 0]
            rows.append({"period": f"FY{yr}", "sort": yr * 100 + 9,
                         "source": "FedsDataCenter (FOIA annual)",
                         "headcount": len(g),
                         "mean_salary": round(pos["salary"].mean()),
                         "median_salary": round(pos["salary"].median())})
    recs = load_records()
    for snap, lbl in ((SNAP0, "Sep 2024"), (SNAP1, "Mar 2025")):
        row = {"period": lbl, "sort": snap, "source": "FedScope (EHRI status)",
               "headcount": int(totals.loc[snap, "headcount"]),
               "mean_salary": int(totals.loc[snap, "mean_salary"]),
               "median_salary": np.nan}
        if snap == SNAP1:
            row["median_salary"] = round(recs["salary"].median())
        rows.append(row)

    out = pd.DataFrame(rows).sort_values("sort").drop(columns="sort")
    _write(out, "fedscope_headcount_pay_trend.csv", index=False)
    return out


# --------------------------------------------------------------------------
# 3. Mean-pay change decomposition (GS cells, ~76% coverage)
# --------------------------------------------------------------------------

def pay_decomposition(cells: pd.DataFrame) -> pd.DataFrame:
    gs = cells[(cells["pay_plan"] == "GS") & cells["grade_num"].notna()].copy()
    gs["wsum"] = gs["headcount"] * gs["mean_salary"]

    grade = (gs.groupby(["snapshot", "grade_num"])
               .agg(headcount=("headcount", "sum"), wsum=("wsum", "sum"))
               .reset_index())
    grade["mean_salary"] = grade["wsum"] / grade["headcount"]

    w = grade.pivot(index="grade_num", columns="snapshot", values="headcount").fillna(0)
    s = grade.pivot(index="grade_num", columns="snapshot", values="mean_salary")
    w0, w1 = w[SNAP0] / w[SNAP0].sum(), w[SNAP1] / w[SNAP1].sum()
    s0, s1 = s[SNAP0], s[SNAP1]
    common = s0.notna() & s1.notna()
    w0, w1, s0, s1 = w0[common], w1[common], s0[common], s1[common]

    m0, m1 = (w0 * s0).sum(), (w1 * s1).sum()
    within = (w0 * (s1 - s0)).sum()               # Laspeyres: Sep weights
    mix = ((w1 - w0) * s0).sum()                  # Sep salaries
    interaction = ((w1 - w0) * (s1 - s0)).sum()
    scheduled = GS_RAISE_2025 * m0                # the ~2.0% Jan 2025 raise
    step_promo = within - scheduled               # steps, within-grade promotions

    rows = [
        ("GS mean pay, Sep 2024 (shown cells)", m0, np.nan),
        ("GS mean pay, Mar 2025 (shown cells)", m1, np.nan),
        ("total change", m1 - m0, 1.0),
        ("  Jan 2025 pay raise (2.0%)", scheduled, scheduled / (m1 - m0)),
        ("  within-grade steps / promotions", step_promo, step_promo / (m1 - m0)),
        ("  grade-mix shift", mix, mix / (m1 - m0)),
        ("  interaction", interaction, interaction / (m1 - m0)),
    ]
    out = pd.DataFrame(rows, columns=["component", "dollars", "share_of_change"])
    out["dollars"] = out["dollars"].round(0)
    out["share_of_change"] = out["share_of_change"].round(3)
    _write(out, "fedscope_pay_change_decomp.csv", index=False)
    return out


# --------------------------------------------------------------------------
# 4. March 2025 pay distribution (record-level)
# --------------------------------------------------------------------------

def pay_distribution(records: pd.DataFrame, totals: pd.DataFrame) -> pd.DataFrame:
    sal = records["salary"].dropna()
    qs = [0.10, 0.25, 0.50, 0.75, 0.90, 0.95]
    out = pd.DataFrame({
        "statistic": ["n", "mean", "std"] + [f"p{int(q * 100)}" for q in qs],
        "mar_2025": [len(sal), round(sal.mean()), round(sal.std())]
        + [round(sal.quantile(q)) for q in qs],
    })
    # September 2024 reference: only the mean is public
    out["sep_2024"] = np.nan
    out.loc[out["statistic"] == "mean", "sep_2024"] = totals.loc[SNAP0, "mean_salary"]
    _write(out, "fedscope_pay_distribution_2025.csv", index=False)
    return out


# --------------------------------------------------------------------------
# 5. Change by agency group (cells)
# --------------------------------------------------------------------------

def by_agency(cells: pd.DataFrame, totals: pd.DataFrame) -> pd.DataFrame:
    cells = cells.copy()
    cells["wsum"] = cells["headcount"] * cells["mean_salary"]
    agg = (cells.groupby(["agency_group", "snapshot"])
                .agg(headcount=("headcount", "sum"), wsum=("wsum", "sum"))
                .reset_index())
    agg["mean_salary"] = agg["wsum"] / agg["headcount"]

    h = agg.pivot(index="agency_group", columns="snapshot", values="headcount").fillna(0)
    p = agg.pivot(index="agency_group", columns="snapshot", values="mean_salary")
    out = pd.DataFrame({
        "headcount_sep_2024": h[SNAP0].astype(int),
        "headcount_mar_2025": h[SNAP1].astype(int),
        "headcount_change": (h[SNAP1] - h[SNAP0]).astype(int),
        "mean_salary_sep_2024": p[SNAP0].round(),
        "mean_salary_mar_2025": p[SNAP1].round(),
    }).sort_values("headcount_mar_2025", ascending=False)

    # Cells with <=10 employees are suppressed on each date independently, so a
    # small agency can gain/lose "all" its economists just by crossing that
    # threshold. Only trust the change where both snapshots show a solid count.
    solid = (out[["headcount_sep_2024", "headcount_mar_2025"]].min(axis=1) >= 25)
    out["coverage"] = np.where(solid, "ok", "partial - small-cell suppression")
    out["pct_change"] = np.where(
        solid, (out["headcount_mar_2025"] / out["headcount_sep_2024"] - 1).round(3), np.nan)
    _write(out, "fedscope_by_agency_change.csv")

    # Companion: how much of the workforce the cell breakdown actually covers.
    shown = h.sum()
    cov = pd.DataFrame({
        "snapshot": [SNAP0, SNAP1],
        "official_total": [int(totals.loc[SNAP0, "headcount"]),
                           int(totals.loc[SNAP1, "headcount"])],
        "shown_in_cells": [int(shown[SNAP0]), int(shown[SNAP1])],
    })
    cov["coverage_pct"] = (cov["shown_in_cells"] / cov["official_total"]).round(3)
    _write(cov, "fedscope_cell_coverage_2025.csv", index=False)
    return out


# --------------------------------------------------------------------------
# 6. Change by GS grade (cells) + March 2025 grade distribution (record-level)
# --------------------------------------------------------------------------

def by_grade(cells: pd.DataFrame) -> pd.DataFrame:
    gs = cells[(cells["pay_plan"] == "GS") & cells["grade_num"].notna()].copy()
    gs["wsum"] = gs["headcount"] * gs["mean_salary"]
    agg = (gs.groupby(["grade_num", "snapshot"])
             .agg(headcount=("headcount", "sum"), wsum=("wsum", "sum"))
             .reset_index())
    agg["mean_salary"] = agg["wsum"] / agg["headcount"]
    h = agg.pivot(index="grade_num", columns="snapshot", values="headcount").fillna(0)
    p = agg.pivot(index="grade_num", columns="snapshot", values="mean_salary")

    out = pd.DataFrame({
        "gs_grade": h.index.astype(int),
        "headcount_sep_2024": h[SNAP0].astype(int).values,
        "headcount_mar_2025": h[SNAP1].astype(int).values,
        "share_sep_2024": (h[SNAP0] / h[SNAP0].sum()).round(3).values,
        "share_mar_2025": (h[SNAP1] / h[SNAP1].sum()).round(3).values,
        "mean_salary_sep_2024": p[SNAP0].round().values,
        "mean_salary_mar_2025": p[SNAP1].round().values,
    })
    _write(out, "fedscope_by_grade_change.csv", index=False)
    return out


# --------------------------------------------------------------------------
# 7. March 2025 workforce profile (record-level, single snapshot)
# --------------------------------------------------------------------------

def profile_2025(records: pd.DataFrame) -> pd.DataFrame:
    records = records.copy()
    records["appointment"] = np.where(records["is_permanent"], "permanent", "non-permanent")
    records["gs14plus"] = records["grade_num"] >= 14

    records["pay_plan_group"] = np.where(records["pay_plan"] == "GS", "GS",
                                  np.where(records["pay_plan"] == "ES", "SES/ES", "other"))
    records["gs_grade"] = np.where(records["pay_plan"] == "GS",
                                   records["grade_num"], np.nan)

    blocks = []
    for dim in ["pay_plan_group", "gs_grade", "appointment", "supervisory",
                "age_band", "education"]:
        g = (records.groupby(dim)
                    .agg(n=("salary", "size"),
                         mean_salary=("salary", "mean"),
                         mean_los=("los", "mean"))
                    .reset_index()
                    .rename(columns={dim: "category"}))
        g.insert(0, "dimension", dim)
        g["mean_salary"] = g["mean_salary"].round()
        g["mean_los"] = g["mean_los"].round(1)
        g["share"] = (g["n"] / g["n"].sum()).round(3)
        blocks.append(g.sort_values("n", ascending=False))

    out = pd.concat(blocks, ignore_index=True)
    _write(out, "fedscope_profile_2025.csv", index=False)
    return out


# --------------------------------------------------------------------------
# 8. Flows: accessions & separations
# --------------------------------------------------------------------------

def flows(fl: pd.DataFrame) -> pd.DataFrame:
    monthly = (fl.groupby(["month", "direction"]).size()
                 .unstack(fill_value=0)
                 .rename(columns={"accession": "accessions", "separation": "separations"}))
    monthly["net"] = monthly["accessions"] - monthly["separations"]
    monthly = monthly.reset_index()
    _write(monthly, "fedscope_flows_monthly_2025.csv", index=False)

    # Are leavers more senior or junior than joiners / the stock?
    prof = (fl.groupby("direction")
              .agg(n=("salary", "size"),
                   mean_salary=("salary", "mean"),
                   mean_los=("los", "mean"),
                   share_gs13plus=("grade", lambda s: np.mean(
                       pd.to_numeric(s, errors="coerce") >= 13)))
              .round(1))
    _write(prof, "fedscope_flows_profile_2025.csv")

    q = fl.copy()
    q["quarter"] = np.where(q["month"] <= 202406, "2024Q2",
                    np.where(q["month"] <= 202409, "2024Q3",
                     np.where(q["month"] <= 202412, "2024Q4", "2025Q1")))
    quarterly = (q.groupby(["quarter", "direction"]).size().unstack(fill_value=0)
                   .rename(columns={"accession": "accessions", "separation": "separations"}))
    quarterly["net"] = quarterly["accessions"] - quarterly["separations"]
    _write(quarterly, "fedscope_flows_quarterly_2025.csv")
    return monthly


# --------------------------------------------------------------------------

def _write(df: pd.DataFrame, name: str, index: bool = True) -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    df.to_csv(TABLES / name, index=index)
    print(f"  wrote {name}")


def run_all() -> None:
    totals = load_totals()
    records = load_records()
    cells = load_cells()
    fl = load_flows()

    print("1. headline headcount + pay")
    h = headline(totals)
    print(h.to_string(index=False), "\n")

    print("2. long-run trend")
    trend(totals)

    print("3. pay-change decomposition (GS)")
    d = pay_decomposition(cells)
    print(d.to_string(index=False), "\n")

    print("4. March 2025 pay distribution")
    pay_distribution(records, totals)

    print("5. change by agency")
    by_agency(cells, totals)

    print("6. change by GS grade")
    by_grade(cells)

    print("7. March 2025 workforce profile")
    profile_2025(records)

    print("8. flows")
    flows(fl)

    print(f"\nAll tables -> {TABLES}/")
    print("Figures: python src/make_figures.py")


if __name__ == "__main__":
    run_all()
