"""
Descriptive analysis of federal economist salaries and bonuses by gender.

Replicates and extends the original Stata analysis across all available years:
  - Salary and bonus distributions by gender (full and gender-assigned sample)
  - Breakdown by pay plan (GS, ES, ZP) and grade
  - Agency-level analysis (BLS, BEA, Census Bureau, IRS, ERS, and others)
  - Year-over-year gender gap trends (panel dimension added vs. original)

All tables are saved as CSVs to output/tables/.

Usage:
    python src/analyze.py             # all years, all tables
    python src/analyze.py --year 2024 # single year summary
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
TABLES_DIR    = Path(__file__).parent.parent / "output" / "tables"

# BEA (ZP pay plan) and Census (GS pay plan) can be separated within
# Dept of Commerce for all years. BLS is Dept of Labor for FY2016+.
# FY2015 used bureau-level names directly.
AGENCY_LABELS = {
    "bls_dum":              "BLS",
    "bea_dum":              "BEA",
    "census_dum":           "Census Bureau",
    "dept_labor_dum":       "Dept of Labor (incl. BLS)",
    "dept_treasury_dum":    "Dept of Treasury",
    "dept_agriculture_dum": "Dept of Agriculture (incl. ERS)",
    "dept_hhs_dum":         "Dept of HHS",
    "dept_energy_dum":      "Dept of Energy",
    "dept_commerce_dum":    "Dept of Commerce (other)",
}
OTHER_AGENCIES_2015 = [
    "INTERNAL REVENUE SERVICE",
    "ECONOMIC RESEARCH SERVICE",
    "DEPARTMENTAL OFFICES",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_panel() -> pd.DataFrame:
    path = PROCESSED_DIR / "economists_panel.csv"
    if not path.exists():
        raise FileNotFoundError(f"Panel not found: {path}. Run clean_merge.py first.")
    return pd.read_csv(path)


def gendered(df: pd.DataFrame) -> pd.DataFrame:
    """Restrict to records with valid gender and positive salary."""
    return df[df["gender"].isin(["male", "female"]) & (df["salary"] > 0)].copy()


def gender_summary(df: pd.DataFrame, var: str) -> pd.DataFrame:
    """Mean, median, std, and count for var, split by gender."""
    return (
        df.groupby("gender")[var]
        .agg(n="count", mean="mean", median="median", std="std", p25=lambda x: x.quantile(0.25), p75=lambda x: x.quantile(0.75))
        .round(1)
    )


def gap_pct(df: pd.DataFrame, var: str = "salary") -> pd.Series:
    """Raw and percentage gender gap in median var, by fiscal year."""
    med = df.groupby(["fiscal_year", "gender"])[var].median().unstack()
    gap = pd.DataFrame({
        "median_male":   med.get("male"),
        "median_female": med.get("female"),
    })
    gap["gap_raw"] = gap["median_male"] - gap["median_female"]
    gap["gap_pct"] = (gap["gap_raw"] / gap["median_male"] * 100).round(1)
    return gap


# ---------------------------------------------------------------------------
# Individual analyses
# ---------------------------------------------------------------------------

def salary_by_gender_year(df: pd.DataFrame) -> pd.DataFrame:
    """Median salary by gender and fiscal year (trend table)."""
    g = gendered(df)
    return gap_pct(g, "salary")


def bonus_by_gender_year(df: pd.DataFrame) -> pd.DataFrame:
    """Bonus incidence and conditional median by gender and year."""
    g = gendered(df)
    rows = []
    for year, grp in g.groupby("fiscal_year"):
        for gender, sub in grp.groupby("gender"):
            rows.append({
                "fiscal_year": year,
                "gender": gender,
                "n": len(sub),
                "pct_with_bonus": (sub["bonus"] > 0).mean() * 100,
                "median_bonus_conditional": sub.loc[sub["bonus"] > 0, "bonus"].median(),
                "mean_bonus_conditional":   sub.loc[sub["bonus"] > 0, "bonus"].mean(),
            })
    return pd.DataFrame(rows).round(1)


def salary_by_payplan(df: pd.DataFrame, year: int = None) -> pd.DataFrame:
    """Salary summary by pay plan and gender."""
    g = gendered(df)
    if year:
        g = g[g["fiscal_year"] == year]

    def plan_label(row):
        if row["gs_dum"] == 1: return "GS"
        if row["es_dum"] == 1: return "ES"
        return "Other"

    g = g.copy()
    g["pay_plan_group"] = g.apply(plan_label, axis=1)
    return (
        g.groupby(["pay_plan_group", "gender"])["salary"]
        .agg(n="count", median="median", mean="mean")
        .round(0)
    )


def salary_by_grade(df: pd.DataFrame, year: int = None) -> pd.DataFrame:
    """Median salary by GS grade and gender (GS pay plan only)."""
    g = gendered(df)
    if year:
        g = g[g["fiscal_year"] == year]
    gs = g[g["gs_dum"] == 1].copy()
    gs["grade"] = pd.to_numeric(gs["grade"], errors="coerce")
    return (
        gs.groupby(["grade", "gender"])["salary"]
        .agg(n="count", median="median")
        .round(0)
        .dropna()
    )


def _label_agencies(g: pd.DataFrame) -> pd.DataFrame:
    """Add agency_group column. BEA/BLS/Census flags work across all years."""
    g = g.copy()
    g["agency_group"] = "Other"

    for dum_col, label in AGENCY_LABELS.items():
        if dum_col in g.columns:
            g.loc[g[dum_col] == 1, "agency_group"] = label

    # FY2015 only: catch IRS, ERS, Departmental Offices by name
    agency_upper = g["agency"].str.strip().str.upper()
    for name in OTHER_AGENCIES_2015:
        g.loc[(g["fiscal_year"] == 2015) & (agency_upper == name), "agency_group"] = name.title()

    return g


def salary_by_agency(df: pd.DataFrame, year: int = None) -> pd.DataFrame:
    """Salary summary by agency/department and gender."""
    g = gendered(df)
    if year:
        g = g[g["fiscal_year"] == year]
    g = _label_agencies(g)
    return (
        g.groupby(["agency_group", "gender"])["salary"]
        .agg(n="count", median="median", mean="mean")
        .round(0)
    )


def gender_composition(df: pd.DataFrame) -> pd.DataFrame:
    """Share of female economists by agency/department and year."""
    g = gendered(df)
    g = _label_agencies(g)
    g_all = g.copy()
    g_all["agency_group"] = "All"
    g_combined = pd.concat([g, g_all], ignore_index=True)

    total = g_combined.groupby(["fiscal_year", "agency_group"]).size()
    female = g_combined[g_combined["gender"] == "female"].groupby(["fiscal_year", "agency_group"]).size()
    share = (female / total * 100).round(1).unstack("agency_group")

    # Keep only columns present in most years to avoid a very sparse table
    keep = share.columns[share.notna().mean() >= 0.3]
    return share[keep]


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_all(year: int = None) -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    df = load_panel()
    label = f"FY{year}" if year else "all_years"

    # 1. Salary trend
    trends = salary_by_gender_year(df)
    trends.to_csv(TABLES_DIR / "salary_gap_by_year.csv")
    print("=== Median Salary Gender Gap by Year ===")
    print(trends.to_string(), "\n")

    # 2. Salary by pay plan
    pay = salary_by_payplan(df, year=year)
    pay.to_csv(TABLES_DIR / f"salary_by_payplan_{label}.csv")
    print(f"=== Salary by Pay Plan ({label}) ===")
    print(pay.to_string(), "\n")

    # 3. Salary by GS grade
    grade = salary_by_grade(df, year=year)
    grade.to_csv(TABLES_DIR / f"salary_by_grade_{label}.csv")
    print(f"=== Salary by GS Grade ({label}) ===")
    print(grade.to_string(), "\n")

    # 4. Salary by agency
    agency = salary_by_agency(df, year=year)
    agency.to_csv(TABLES_DIR / f"salary_by_agency_{label}.csv")
    print(f"=== Salary by Agency ({label}) ===")
    print(agency.to_string(), "\n")

    # 5. Bonus trends
    bonus = bonus_by_gender_year(df)
    bonus.to_csv(TABLES_DIR / "bonus_by_gender_year.csv", index=False)
    print("=== Bonus Incidence and Conditional Median by Gender/Year ===")
    print(bonus.to_string(), "\n")

    # 6. Gender composition over time
    comp = gender_composition(df)
    comp.to_csv(TABLES_DIR / "female_share_by_agency_year.csv")
    print("=== Female Share (%) by Agency and Year ===")
    print(comp.to_string(), "\n")

    print(f"All tables saved to {TABLES_DIR}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, help="Focus analysis on a single year")
    args = parser.parse_args()
    run_all(year=args.year)
