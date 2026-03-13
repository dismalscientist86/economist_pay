"""
Assign gender to economist first names using gender_guesser.

gender_guesser is a fast, offline library (~40k names, no API required).
It returns one of six categories:
    male, mostly_male, female, mostly_female, andy (androgynous), unknown

We treat male+mostly_male as male and female+mostly_female as female.
andy and unknown are left unassigned (gender = "").

Results are cached to data/processed/gender_cache.csv so this step only
runs once across all years.

Usage:
    python src/assign_gender.py   # build cache from all raw CSVs
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import parse_first_name

import pandas as pd
import gender_guesser.detector as gender_detector

RAW_DIR = Path(__file__).parent.parent / "data" / "raw" / "fedsdatacenter"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
GENDER_CACHE = PROCESSED_DIR / "gender_cache.csv"

# Map gender_guesser output to binary male/female (or "" if ambiguous)
GENDER_MAP = {
    "male":         "male",
    "mostly_male":  "male",
    "female":       "female",
    "mostly_female": "female",
    "andy":         "",
    "unknown":      "",
}


def assign_gender_to_names(first_names: list[str]) -> pd.DataFrame:
    """
    Assign gender to a list of first names using gender_guesser.

    Returns a DataFrame with columns:
        first_name, gender_raw, gender
    where gender_raw is the full gender_guesser label and gender is the
    simplified male/female/"" value.
    """
    d = gender_detector.Detector(case_sensitive=False)
    rows = []
    for name in first_names:
        raw = d.get_gender(name) if name else "unknown"
        rows.append({
            "first_name": name,
            "gender_raw": raw,
            "gender": GENDER_MAP.get(raw, ""),
        })
    return pd.DataFrame(rows)


def build_gender_cache(overwrite: bool = False) -> pd.DataFrame:
    """
    Collect all unique first names across all raw CSVs, assign gender,
    and save to the cache file.
    """
    if GENDER_CACHE.exists() and not overwrite:
        print(f"Gender cache already exists ({GENDER_CACHE.name}). Use --overwrite to rebuild.")
        return pd.read_csv(GENDER_CACHE)

    csv_files = sorted(RAW_DIR.glob("economists_FY*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No raw CSV files found in {RAW_DIR}. Run fetch_salary_data.py first.")

    print(f"Collecting names from {len(csv_files)} year(s) of data...")
    all_first_names: set[str] = set()
    for f in csv_files:
        df = pd.read_csv(f, usecols=["name"])
        names = df["name"].apply(parse_first_name).dropna()
        names = names[names != ""]
        all_first_names.update(names.unique())

    print(f"  {len(all_first_names)} unique first names found")

    sorted_names = sorted(all_first_names)
    gender_df = assign_gender_to_names(sorted_names)

    assigned = (gender_df["gender"] != "").sum()
    print(f"  {assigned} names assigned ({assigned/len(gender_df):.1%}), "
          f"{len(gender_df)-assigned} unassigned (andy/unknown)")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    gender_df.to_csv(GENDER_CACHE, index=False)
    print(f"  Cache saved to {GENDER_CACHE.name}")
    return gender_df


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    build_gender_cache(overwrite=args.overwrite)
