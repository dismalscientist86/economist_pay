"""
Fetch federal economist salary data from the FedsDataCenter.com JSON API.

The site uses a DataTables server-side processing endpoint that returns
paginated JSON. This script paginates through all records for each fiscal
year and saves one CSV per year to data/raw/fedsdatacenter/.

Usage:
    python src/fetch_salary_data.py               # fetch all years (2015-2024)
    python src/fetch_salary_data.py --year 2024   # single year
    python src/fetch_salary_data.py --start 2020 --end 2024
"""

import argparse
import time
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://www.fedsdatacenter.com/federal-pay-rates/output.php"
RAW_DIR = Path(__file__).parent.parent / "data" / "raw" / "fedsdatacenter"

# Column order matches the aaData array returned by the API
COLUMNS = ["name", "grade", "pay_plan", "salary", "bonus", "agency", "location", "occupation", "year"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (research data collection; contact via GitHub)",
    "Referer": "https://www.fedsdatacenter.com/federal-pay-rates/",
}


def fetch_year(year: int, page_size: int = 100, delay: float = 0.5) -> pd.DataFrame:
    """
    Fetch all economist records for a given fiscal year.

    Paginates through the DataTables JSON endpoint until all records
    are retrieved. Uses a short delay between requests to be polite.
    """
    params = {
        "n": "", "l": "", "a": "",
        "o": "economist",
        "y": str(year),
        "iDisplayStart": 0,
        "iDisplayLength": page_size,
        "sEcho": 1,
    }

    resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    total = int(data["iTotalDisplayRecords"])
    print(f"  FY{year}: {total} records found")

    records = list(data["aaData"])

    for start in range(page_size, total, page_size):
        params["iDisplayStart"] = start
        params["sEcho"] += 1
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        records.extend(resp.json()["aaData"])
        time.sleep(delay)

    df = pd.DataFrame(records, columns=COLUMNS)
    assert len(df) == total, f"Expected {total} records, got {len(df)}"
    return df


def fetch_all_years(start: int = 2015, end: int = 2024, overwrite: bool = False) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for year in range(start, end + 1):
        out_path = RAW_DIR / f"economists_FY{year}.csv"
        if out_path.exists() and not overwrite:
            print(f"  FY{year}: already exists, skipping (use --overwrite to re-fetch)")
            continue

        print(f"Fetching FY{year}...")
        df = fetch_year(year)
        df.to_csv(out_path, index=False)
        print(f"  FY{year}: saved {len(df)} records to {out_path.name}")
        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch federal economist salary data")
    parser.add_argument("--year", type=int, help="Fetch a single fiscal year")
    parser.add_argument("--start", type=int, default=2015)
    parser.add_argument("--end", type=int, default=2024)
    parser.add_argument("--overwrite", action="store_true", help="Re-fetch existing files")
    args = parser.parse_args()

    if args.year:
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        df = fetch_year(args.year)
        out = RAW_DIR / f"economists_FY{args.year}.csv"
        df.to_csv(out, index=False)
        print(f"Saved {len(df)} records → {out}")
    else:
        fetch_all_years(start=args.start, end=args.end, overwrite=args.overwrite)
