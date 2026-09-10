"""
Fetch FedScope employment, accessions, and separations data from OPM and
extract the economist (occupational series 0110 / 0119) records.

Background
----------
FedsDataCenter.com (see fetch_salary_data.py) stops at FY2024. For 2025 the
only public source is OPM's FedScope "classic" raw datasets:
    https://www.opm.gov/data/datasets/

This release is the *preliminary* March 2025 snapshot (posted 2025-07-01). It
carries the September 2024 snapshot alongside for a clean comparison. Note:

  - Gender / race were removed from FedScope as of March 2025 (EO 14151/14168/
    14173). This data has no gender dimension.
  - The March 2025 snapshot does NOT reflect the 2025 reshaping: employees on
    administrative leave pending resignation/retirement are still counted.
  - Some rows (mostly DoD) are fully REDACTED; those economists cannot be
    identified in the record-level files, so the record-level economist extract
    (~4,670) is smaller than OPM's summary total (~4,888).
  - MD/VA/WV duty stations are recoded to DC; summary cells <= 10 show as
    10_OR_LESS.

What this script produces (all under data/raw/fedscope/)
-------------------------------------------------------
  _downloads/                       raw .zip files as downloaded (git-ignored)
  SOURCES.md                        URLs, retrieval date, notes
  employment_202503_economists.csv  record-level economists, March 2025 snapshot
  accessions_202404_202503_economists.csv   record-level economist accessions
  separations_202404_202503_economists.csv  record-level economist separations
  summary/                          the small pre-aggregated cross-tabs
      Status Employment by Occupation_202503_and_202409.txt        (verbatim)
      Status Employment by Pay Plan and Grade_202503_and_202409.txt (verbatim)
      Employment by Agency PayPlan Grade Series_economists.csv     (filtered)
      FedScope Employment.pdf                                      (data dictionary)

Usage
-----
    python src/fetch_fedscope.py                # fetch + extract (skips existing)
    python src/fetch_fedscope.py --overwrite    # re-download and re-extract
    python src/fetch_fedscope.py --keep-downloads / --no-keep-downloads
"""

import argparse
import csv
import io
import shutil
import sys
import zipfile
from datetime import date
from pathlib import Path

import requests

FEDSCOPE_DIR = Path(__file__).parent.parent / "data" / "raw" / "fedscope"
DOWNLOAD_DIR = FEDSCOPE_DIR / "_downloads"
SUMMARY_DIR = FEDSCOPE_DIR / "summary"

BASE = "https://www.opm.gov/data/datasets/Files"
HEADERS = {"User-Agent": "Mozilla/5.0 (research data collection; contact via GitHub)"}

# Economist occupational series. 0110 is the headline; 0119 (Economics
# Assistant) is kept for the sensitivity check and dropped by clean_fedscope
# unless explicitly requested.
ECON_SERIES = {"0110", "0119"}

# csv.field_size_limit default is too small for these wide rows on some builds
csv.field_size_limit(10_000_000)

# --------------------------------------------------------------------------
# Dataset registry
# --------------------------------------------------------------------------
# Each entry: the OPM "Files/<id>/<uuid>.zip" path and the local zip name.
DATASETS = {
    "employment_file_1": ("756/a1acc4f3-0c10-45e3-ac1f-0ee7f5769e1d.zip", "march_2025_employment_1.zip"),
    "employment_file_2": ("758/18693acd-e0d7-4cb5-b15b-bd455a3a432c.zip", "march_2025_employment_2.zip"),
    "employment_file_3": ("759/3c93cbe4-ae79-4881-8562-5892df28744d.zip", "march_2025_employment_3.zip"),
    "employment_summary": ("753/bc88ce69-1bbe-406f-9441-3c5153014616.zip", "march_2025_employment_summary.zip"),
    "accessions": ("761/6124a377-5e92-43e7-ade2-3be674580bc7.zip", "accessions_202404_to_202503.zip"),
    "separations": ("763/1e0ad2cd-40ee-4646-9daa-58b762bcddfb.zip", "separations_202404_to_202503.zip"),
}

# Summary files copied verbatim (small, useful as reference / for other work).
# The accessions/separations record layout matches the employment one (plus the
# ACC/SEP action columns), so only the employment data dictionary is kept.
SUMMARY_VERBATIM = {
    "Status Employment by Occupation_202503_and_202409.txt",
    "Status Employment by Pay Plan and Grade_202503_and_202409.txt",
    "FedScope Employment.pdf",
}
# The Agency x PayPlan x Grade x Series summary is ~5 MB of all occupations;
# we keep only the economist rows.
SUMMARY_AGENCY_SERIES = "Status Employment by Agency_PayPlan_Grade_Series_202503_and_202409.txt"


# --------------------------------------------------------------------------
# Download
# --------------------------------------------------------------------------

def download(key: str, overwrite: bool = False) -> Path:
    rel, local_name = DATASETS[key]
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    dest = DOWNLOAD_DIR / local_name
    if dest.exists() and not overwrite:
        print(f"  {local_name}: already downloaded ({dest.stat().st_size / 1e6:.1f} MB)")
        return dest

    url = f"{BASE}/{rel}"
    print(f"  downloading {local_name} ...")
    with requests.get(url, headers=HEADERS, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=1 << 20):
                fh.write(chunk)
    print(f"  {local_name}: {dest.stat().st_size / 1e6:.1f} MB")
    return dest


# --------------------------------------------------------------------------
# Record-level economist filter
# --------------------------------------------------------------------------

def filter_records_from_zip(zip_path: Path, member_suffix: str, out_path: Path,
                            occ_field: str = "OCC", keep: set = ECON_SERIES) -> int:
    """
    Stream a large pipe-delimited member out of `zip_path`, keep only rows whose
    `occ_field` is in `keep`, and append them to `out_path` (CSV). Returns the
    number of rows written. Writes the header on first call (out_path absent).
    """
    with zipfile.ZipFile(zip_path) as zf:
        member = next(n for n in zf.namelist() if n.endswith(member_suffix))
        write_header = not out_path.exists()
        n = 0
        with zf.open(member) as raw:
            text = io.TextIOWrapper(raw, encoding="latin-1", newline="")
            reader = csv.reader(text, delimiter="|", quotechar='"')
            header = next(reader)
            try:
                occ_idx = header.index(occ_field)
            except ValueError:
                raise ValueError(f"{occ_field} not in {member} header: {header}")

            with open(out_path, "a", newline="", encoding="utf-8") as out_fh:
                writer = csv.writer(out_fh)
                if write_header:
                    writer.writerow(header)
                for row in reader:
                    if len(row) > occ_idx and row[occ_idx] in keep:
                        writer.writerow(row)
                        n += 1
    return n


def filter_summary_series(zip_path: Path, out_path: Path) -> int:
    """Keep only economist rows from the Agency x PayPlan x Grade x Series summary."""
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(SUMMARY_AGENCY_SERIES) as raw:
            text = io.TextIOWrapper(raw, encoding="latin-1", newline="")
            reader = csv.reader(text, delimiter="\t", quotechar='"')
            header = next(reader)
            occ_idx = header.index("OCC")
            n = 0
            with open(out_path, "w", newline="", encoding="utf-8") as out_fh:
                writer = csv.writer(out_fh)
                writer.writerow(header)
                for row in reader:
                    if len(row) > occ_idx and row[occ_idx] in {"110", "119", "0110", "0119"}:
                        writer.writerow(row)
                        n += 1
    return n


def extract_summary_verbatim(zip_path: Path) -> None:
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if name in SUMMARY_VERBATIM:
                with zf.open(name) as src, open(SUMMARY_DIR / name, "wb") as dst:
                    shutil.copyfileobj(src, dst)


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------

def build(overwrite: bool = False, keep_downloads: bool = True) -> None:
    FEDSCOPE_DIR.mkdir(parents=True, exist_ok=True)

    print("Step 1: download")
    paths = {k: download(k, overwrite=overwrite) for k in DATASETS}

    print("\nStep 2: extract economist records — employment (March 2025 snapshot)")
    emp_out = FEDSCOPE_DIR / "employment_202503_economists.csv"
    if emp_out.exists() and not overwrite:
        print(f"  {emp_out.name}: exists, skipping")
    else:
        emp_out.unlink(missing_ok=True)
        total = 0
        for key, suffix in (("employment_file_1", "_Employment_1.txt"),
                            ("employment_file_2", "_Employment_2.txt"),
                            ("employment_file_3", "_Employment_3.txt")):
            n = filter_records_from_zip(paths[key], suffix, emp_out)
            print(f"  {key}: {n} economist rows")
            total += n
        print(f"  -> {emp_out.name}: {total} rows")

    print("\nStep 3: extract economist records — accessions & separations (Apr 2024-Mar 2025)")
    for key, suffix, out_name in (
        ("accessions", "_Accessions.txt", "accessions_202404_202503_economists.csv"),
        ("separations", "_Separations.txt", "separations_202404_202503_economists.csv"),
    ):
        out_path = FEDSCOPE_DIR / out_name
        if out_path.exists() and not overwrite:
            print(f"  {out_name}: exists, skipping")
            continue
        out_path.unlink(missing_ok=True)
        n = filter_records_from_zip(paths[key], suffix, out_path)
        print(f"  {key}: {n} economist rows -> {out_name}")

    print("\nStep 4: summary cross-tabs")
    extract_summary_verbatim(paths["employment_summary"])
    n = filter_summary_series(paths["employment_summary"],
                              SUMMARY_DIR / "Employment by Agency PayPlan Grade Series_economists.csv")
    print(f"  economist rows in Agency x PayPlan x Grade x Series: {n}")
    print(f"  summary files -> {SUMMARY_DIR}/")

    write_sources_md()

    if not keep_downloads:
        print("\nStep 5: removing _downloads/ (--no-keep-downloads)")
        shutil.rmtree(DOWNLOAD_DIR, ignore_errors=True)

    print("\nDone.")


def write_sources_md() -> None:
    lines = [
        "# FedScope source files",
        "",
        f"Retrieved {date.today().isoformat()} from <https://www.opm.gov/data/datasets/>.",
        "",
        "OPM FedScope \"classic\" raw datasets. This is the **preliminary** March 2025",
        "employment snapshot (posted 2025-07-01) with the September 2024 snapshot",
        "bundled for comparison, plus the April 2024-March 2025 accessions/separations.",
        "",
        "| dataset | OPM Files path | local zip |",
        "| --- | --- | --- |",
    ]
    for key, (rel, local_name) in DATASETS.items():
        lines.append(f"| {key} | `{rel}` | `_downloads/{local_name}` |")
    lines += [
        "",
        "## Caveats (carry into every output)",
        "",
        "- **No gender / race.** Removed from FedScope as of March 2025 (EO 14151/14168/14173).",
        "- **Preliminary.** March 2025 is subject to revision.",
        "- **Understates the decline.** Employees on administrative leave pending",
        "  resignation/retirement are still counted as current in March 2025.",
        "- **Redaction.** Fully-redacted rows (mostly DoD) cannot be identified as",
        "  economists in the record-level files, so `employment_202503_economists.csv`",
        "  (~4,670 rows) is smaller than OPM's summary economist total (~4,888).",
        "- **Location masking.** MD/VA/WV duty stations recoded to DC.",
        "- **Small-cell suppression.** Summary cells <= 10 shown as `10_OR_LESS`.",
        "- **Universe break.** Not directly comparable in levels to the FedsDataCenter",
        "  FY2015-2024 series (EHRI month-end status vs. annual FOIA extract).",
        "",
        "`_downloads/` is git-ignored. Re-create everything with `python src/fetch_fedscope.py`.",
        "",
    ]
    (FEDSCOPE_DIR / "SOURCES.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch FedScope economist data (2024-2025)")
    parser.add_argument("--overwrite", action="store_true", help="Re-download and re-extract")
    parser.add_argument("--no-keep-downloads", dest="keep_downloads", action="store_false",
                        help="Delete the ~1 GB _downloads/ cache when finished")
    parser.set_defaults(keep_downloads=True)
    args = parser.parse_args()

    build(overwrite=args.overwrite, keep_downloads=args.keep_downloads)
