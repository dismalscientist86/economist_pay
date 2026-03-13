"""
Clean and merge salary data with gender assignments.

For each raw year CSV:
  - Parses salary and bonus to numeric
  - Extracts first names and merges gender from the cache
  - Creates agency and pay-plan indicator columns

Outputs:
  - data/processed/economists_FY{year}_clean.csv  (one per year)
  - data/processed/economists_panel.csv            (all years stacked)

Usage:
    python src/clean_merge.py
    python src/clean_merge.py --year 2024
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import parse_first_name, clean_numeric

import pandas as pd

RAW_DIR = Path(__file__).parent.parent / "data" / "raw" / "fedsdatacenter"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
GENDER_CACHE = PROCESSED_DIR / "gender_cache.csv"

# Agencies of interest → indicator column name
AGENCY_FLAGS = {
    "BUREAU OF THE CENSUS":         "census_dum",
    "BUREAU OF LABOR STATISTICS":   "bls_dum",
    "BUREAU OF ECONOMIC ANALYSIS":  "bea_dum",
}

# BEA uses ZP pay plan; IRS and ERS are also tracked
PAYPLAN_FLAGS = {
    "GS": "gs_dum",
    "ES": "es_dum",
}


def process_year(year: int, gender_cache: pd.DataFrame) -> pd.DataFrame:
    src = RAW_DIR / f"economists_FY{year}.csv"
    if not src.exists():
        raise FileNotFoundError(f"Raw file not found: {src}. Run fetch_salary_data.py first.")

    df = pd.read_csv(src)
    df["fiscal_year"] = year

    # Numeric salary and bonus
    df["salary"] = df["salary"].apply(clean_numeric)
    df["bonus"]  = df["bonus"].apply(clean_numeric)

    # Name parsing
    df["first_name"] = df["name"].apply(parse_first_name)

    # Merge gender (left join: unmatched names keep gender = NaN → "")
    df = df.merge(
        gender_cache[["first_name", "gender", "gender_raw"]],
        on="first_name",
        how="left",
    )
    df["gender"] = df["gender"].fillna("")

    # Binary male indicator (1=male, 0=female, NaN=unassigned)
    df["male"] = df["gender"].map({"male": 1, "female": 0})

    # Agency indicator columns
    agency_upper = df["agency"].str.strip().str.upper()
    for agency_str, col in AGENCY_FLAGS.items():
        df[col] = (agency_upper == agency_str).astype(int)

    # Pay plan indicator columns
    for plan, col in PAYPLAN_FLAGS.items():
        df[col] = (df["pay_plan"].str.strip().str.upper() == plan).astype(int)

    return df


def merge_all_years(start: int = 2015, end: int = 2024) -> pd.DataFrame:
    if not GENDER_CACHE.exists():
        raise FileNotFoundError(
            f"Gender cache not found: {GENDER_CACHE}. Run assign_gender.py first."
        )

    gender_cache = pd.read_csv(GENDER_CACHE)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    all_dfs = []
    for year in range(start, end + 1):
        src = RAW_DIR / f"economists_FY{year}.csv"
        if not src.exists():
            print(f"  FY{year}: raw file not found, skipping")
            continue

        df = process_year(year, gender_cache)
        out = PROCESSED_DIR / f"economists_FY{year}_clean.csv"
        df.to_csv(out, index=False)

        n_gendered = df["gender"].isin(["male", "female"]).sum()
        print(f"  FY{year}: {len(df)} records, {n_gendered} with gender assigned "
              f"({n_gendered/len(df):.1%})")
        all_dfs.append(df)

    panel = pd.concat(all_dfs, ignore_index=True)
    panel_path = PROCESSED_DIR / "economists_panel.csv"
    panel.to_csv(panel_path, index=False)
    print(f"\nPanel saved: {len(panel)} records across {panel['fiscal_year'].nunique()} years "
          f"→ {panel_path.name}")
    return panel


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, help="Process a single year only")
    parser.add_argument("--start", type=int, default=2015)
    parser.add_argument("--end",   type=int, default=2024)
    args = parser.parse_args()

    if args.year:
        gender_cache = pd.read_csv(GENDER_CACHE)
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        df = process_year(args.year, gender_cache)
        out = PROCESSED_DIR / f"economists_FY{args.year}_clean.csv"
        df.to_csv(out, index=False)
        print(f"Saved {len(df)} records → {out.name}")
    else:
        merge_all_years(start=args.start, end=args.end)
