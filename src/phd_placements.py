"""
PhD economist placement analysis module.

Analyzes initial job placement outcomes for new PhD economists by gender,
field, department, and placement category.

Data source: data/raw/phd_placements/econ_phd_placements.csv
  8,824 records covering placement years 1991–2025 from 44 top PhD programs.

CSV columns (actual):
    name          - full name of PhD recipient
    year          - placement year
    department_id - short code for PhD-granting department (e.g. 'harvard', 'chicago')
    field         - subfield(s); may be multi-valued or empty
    placement     - placement institution/employer
    category      - placement type: tenure_track, other_academic, government,
                    central_banks, think_tanks, international_orgs,
                    private_sector, or "" (unknown)

Gender is assigned via the salary-data gender cache (gender_guesser).
If the cache doesn't exist yet, assign_gender.py must be run first,
OR the gender assignment step here can be skipped and re-run later.

Usage:
    python src/phd_placements.py
    python src/phd_placements.py --skip-gender   # if cache not yet built
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import parse_first_name_natural as parse_first_name

import pandas as pd

RAW_DIR       = Path(__file__).parent.parent / "data" / "raw" / "phd_placements"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
TABLES_DIR    = Path(__file__).parent.parent / "output" / "tables"
GENDER_CACHE  = PROCESSED_DIR / "gender_cache.csv"

CATEGORY_ORDER = [
    "tenure_track",
    "other_academic",
    "government",
    "central_banks",
    "think_tanks",
    "international_orgs",
    "private_sector",
    "",
]

ACADEMIC = {"tenure_track", "other_academic"}
GOVERNMENT_BROAD = {"government", "central_banks", "think_tanks", "international_orgs"}


def load_placements() -> pd.DataFrame:
    """Load PhD placement CSV from data/raw/phd_placements/."""
    files = sorted(RAW_DIR.glob("*.csv"))
    if not files:
        raise FileNotFoundError(
            f"No placement CSV found in {RAW_DIR}."
        )

    dfs = []
    for f in files:
        df = pd.read_csv(f, encoding="utf-8")
        df.columns = df.columns.str.lower().str.strip()
        # Rename department_id → department for consistency
        if "department_id" in df.columns and "department" not in df.columns:
            df = df.rename(columns={"department_id": "department"})
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["category"] = df["category"].fillna("").str.strip()
    return df


def assign_gender(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign gender from the salary-data gender cache.
    Falls back gracefully if cache doesn't exist.
    """
    if not GENDER_CACHE.exists():
        print("  Warning: gender cache not found. Run assign_gender.py after fetching salary data.")
        print("  Proceeding without gender assignment.")
        df["first_name"] = df["name"].apply(parse_first_name)
        df["gender"] = ""
        return df

    cache = pd.read_csv(GENDER_CACHE)
    df = df.copy()
    df["first_name"] = df["name"].apply(parse_first_name)
    df = df.merge(cache[["first_name", "gender"]], on="first_name", how="left")
    df["gender"] = df["gender"].fillna("")
    return df


# ---------------------------------------------------------------------------
# Analyses
# ---------------------------------------------------------------------------

def gender_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Overall gender composition of the dataset."""
    g = df[df["gender"].isin(["male", "female"])]
    total = g.groupby("year").size().rename("n_total")
    female = g[g["gender"] == "female"].groupby("year").size().rename("n_female")
    result = pd.concat([total, female], axis=1).fillna(0)
    result["female_share_pct"] = (result["n_female"] / result["n_total"] * 100).round(1)
    return result


def placements_by_category_gender(df: pd.DataFrame) -> pd.DataFrame:
    """Placement counts and female share by category."""
    g = df[df["gender"].isin(["male", "female"])]
    counts = g.groupby(["category", "gender"]).size().unstack(fill_value=0)

    # Ensure both columns present
    for col in ["male", "female"]:
        if col not in counts.columns:
            counts[col] = 0

    counts["total"] = counts["male"] + counts["female"]
    counts["female_pct"] = (counts["female"] / counts["total"] * 100).round(1)
    return counts.sort_values("total", ascending=False)


def placements_by_category_year(df: pd.DataFrame) -> pd.DataFrame:
    """Female share of each placement category by year (trend)."""
    g = df[df["gender"].isin(["male", "female"])]
    total  = g.groupby(["year", "category"]).size().rename("n")
    female = g[g["gender"] == "female"].groupby(["year", "category"]).size().rename("n_female")
    result = pd.concat([total, female], axis=1).fillna(0)
    result["female_pct"] = (result["n_female"] / result["n"] * 100).round(1)
    return result.reset_index()


def placements_by_department_gender(df: pd.DataFrame) -> pd.DataFrame:
    """Placement counts and female share by PhD-granting department."""
    g = df[df["gender"].isin(["male", "female"])]
    counts = g.groupby(["department", "gender"]).size().unstack(fill_value=0)
    for col in ["male", "female"]:
        if col not in counts.columns:
            counts[col] = 0
    counts["total"] = counts["male"] + counts["female"]
    counts["female_pct"] = (counts["female"] / counts["total"] * 100).round(1)
    return counts.sort_values("total", ascending=False)


def academia_vs_other(df: pd.DataFrame) -> pd.DataFrame:
    """
    Female share in academia (tenure_track + other_academic) vs.
    government-broad (government + central_banks + think_tanks + international_orgs)
    vs. private sector, by year.
    """
    g = df[df["gender"].isin(["male", "female"])].copy()
    g["sector"] = "other"
    g.loc[g["category"].isin(ACADEMIC), "sector"] = "academia"
    g.loc[g["category"].isin(GOVERNMENT_BROAD), "sector"] = "government_broad"
    g.loc[g["category"] == "private_sector", "sector"] = "private_sector"

    total  = g.groupby(["year", "sector"]).size().rename("n")
    female = g[g["gender"] == "female"].groupby(["year", "sector"]).size().rename("n_female")
    result = pd.concat([total, female], axis=1).fillna(0)
    result["female_pct"] = (result["n_female"] / result["n"] * 100).round(1)
    return result.reset_index()


def run_all(skip_gender: bool = False) -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df = load_placements()
    print(f"Loaded {len(df)} placement records ({df['year'].min():.0f}–{df['year'].max():.0f})")

    if skip_gender:
        df["first_name"] = df["name"].apply(parse_first_name)
        df["gender"] = ""
    else:
        df = assign_gender(df)
        n_assigned = df["gender"].isin(["male", "female"]).sum()
        print(f"Gender assigned: {n_assigned}/{len(df)} ({n_assigned/len(df):.1%})")

    # Save cleaned placements
    df.to_csv(PROCESSED_DIR / "phd_placements_clean.csv", index=False)

    # 1. Female share by year
    gs = gender_summary(df)
    gs.to_csv(TABLES_DIR / "placements_female_share_by_year.csv")
    print("\n=== Female Share of PhD Placements by Year ===")
    print(gs.tail(10).to_string(), "\n")

    # 2. By category
    cat = placements_by_category_gender(df)
    cat.to_csv(TABLES_DIR / "placements_by_category_gender.csv")
    print("=== Placements by Category and Gender ===")
    print(cat.to_string(), "\n")

    # 3. Category trends
    cat_yr = placements_by_category_year(df)
    cat_yr.to_csv(TABLES_DIR / "placements_by_category_year.csv", index=False)

    # 4. By department
    dept = placements_by_department_gender(df)
    dept.to_csv(TABLES_DIR / "placements_by_department_gender.csv")
    print("=== Placements by Department and Gender ===")
    print(dept.to_string(), "\n")

    # 5. Academia vs government vs private sector
    sectors = academia_vs_other(df)
    sectors.to_csv(TABLES_DIR / "placements_by_sector_year.csv", index=False)
    print("=== Female Share by Sector (most recent 5 years) ===")
    recent = sectors[sectors["year"] >= sectors["year"].max() - 4]
    print(recent.to_string(index=False), "\n")

    print(f"All tables saved to {TABLES_DIR}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-gender", action="store_true",
                        help="Skip gender assignment (useful before salary data is fetched)")
    args = parser.parse_args()
    run_all(skip_gender=args.skip_gender)
