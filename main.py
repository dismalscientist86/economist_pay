"""
Main pipeline runner for the economist_pay project.

Runs the full salary data pipeline in sequence:
  1. fetch_salary_data  - download FY2015-2024 from FedsDataCenter API
  2. assign_gender      - build gender lookup from all unique first names
  3. clean_merge        - parse names, merge gender, create indicators, build panel
  4. analyze            - generate descriptive stat tables

For PhD placement analysis, run: python src/phd_placements.py

Usage:
    python main.py                        # full pipeline
    python main.py --skip-fetch           # skip download (use existing raw files)
    python main.py --start 2020 --end 2024
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from fetch_salary_data import fetch_all_years
from assign_gender import build_gender_cache
from clean_merge import merge_all_years
from analyze import run_all

RAW_DIR = Path(__file__).parent / "data" / "raw" / "fedsdatacenter"


def main():
    parser = argparse.ArgumentParser(description="Federal economist pay analysis pipeline")
    parser.add_argument("--skip-fetch",   action="store_true", help="Skip data download step")
    parser.add_argument("--skip-gender",  action="store_true", help="Skip gender assignment step")
    parser.add_argument("--skip-merge",   action="store_true", help="Skip clean/merge step")
    parser.add_argument("--skip-analyze", action="store_true", help="Skip analysis step")
    parser.add_argument("--start", type=int, default=2015, help="First fiscal year to include")
    parser.add_argument("--end",   type=int, default=2024, help="Last fiscal year to include")
    parser.add_argument("--overwrite", action="store_true", help="Re-fetch/re-process existing files")
    args = parser.parse_args()

    if not args.skip_fetch:
        print("=" * 60)
        print("Step 1: Fetching salary data from FedsDataCenter...")
        print("=" * 60)
        fetch_all_years(start=args.start, end=args.end, overwrite=args.overwrite)

    if not args.skip_gender:
        print("\n" + "=" * 60)
        print("Step 2: Building gender cache...")
        print("=" * 60)
        build_gender_cache(overwrite=args.overwrite)

    if not args.skip_merge:
        print("\n" + "=" * 60)
        print("Step 3: Cleaning and merging data...")
        print("=" * 60)
        merge_all_years(start=args.start, end=args.end)

    if not args.skip_analyze:
        print("\n" + "=" * 60)
        print("Step 4: Running analysis...")
        print("=" * 60)
        run_all()

    print("\nDone.")


if __name__ == "__main__":
    main()
