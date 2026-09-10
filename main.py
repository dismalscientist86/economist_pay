"""
Main pipeline runner for the economist_pay project.

Runs the full salary data pipeline in sequence:
  1. fetch_salary_data  - download FY2015-2024 from FedsDataCenter API
  2. assign_gender      - build gender lookup from all unique first names
  3. clean_merge        - parse names, merge gender, create indicators, build panel
  4. analyze            - generate descriptive stat tables

For PhD placement analysis, run: python src/phd_placements.py

For the 2025 update (FedScope, no gender), run: python main.py --fedscope
  This is a separate pipeline — FedsDataCenter stops at FY2024, so 2025 uses
  OPM FedScope. See docs/2025_update_plan.md.

Usage:
    python main.py                        # full pipeline (FedsDataCenter, 2015-2024)
    python main.py --skip-fetch           # skip download (use existing raw files)
    python main.py --start 2020 --end 2024
    python main.py --fedscope             # 2025 update: fetch -> clean -> analyze
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


def run_fedscope_2025(overwrite: bool = False) -> None:
    """The 2025 update pipeline: FedScope fetch -> clean -> analyze."""
    from fetch_fedscope import build as fetch_fedscope
    from clean_fedscope import run_all as clean_fedscope
    from analyze_2025 import run_all as analyze_2025

    print("=" * 60)
    print("FedScope 2025 update: fetching (Sept 2024 + March 2025)...")
    print("=" * 60)
    fetch_fedscope(overwrite=overwrite)

    print("\n" + "=" * 60)
    print("Cleaning FedScope economist extracts...")
    print("=" * 60)
    clean_fedscope()

    print("\n" + "=" * 60)
    print("Analyzing 2024 -> 2025 change...")
    print("=" * 60)
    analyze_2025()

    print("\nDone. Figures: python src/make_figures.py --only fedscope2025")


def main():
    parser = argparse.ArgumentParser(description="Federal economist pay analysis pipeline")
    parser.add_argument("--fedscope", action="store_true",
                        help="Run the 2025 update pipeline (FedScope) instead of the FedsDataCenter one")
    parser.add_argument("--skip-fetch",   action="store_true", help="Skip data download step")
    parser.add_argument("--skip-gender",  action="store_true", help="Skip gender assignment step")
    parser.add_argument("--skip-merge",   action="store_true", help="Skip clean/merge step")
    parser.add_argument("--skip-analyze", action="store_true", help="Skip analysis step")
    parser.add_argument("--start", type=int, default=2015, help="First fiscal year to include")
    parser.add_argument("--end",   type=int, default=2024, help="Last fiscal year to include")
    parser.add_argument("--overwrite", action="store_true", help="Re-fetch/re-process existing files")
    args = parser.parse_args()

    if args.fedscope:
        run_fedscope_2025(overwrite=args.overwrite)
        return

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
