"""
Historical FedScope for long-run context on the 2024 -> 2025 change:
economist (occupational series 0110 / 0119) flows back to FY2015 and
employment snapshots back to September 1998.

Two data eras, both filtered to economist rows here:
  - Pre-2025 "cube" files (SEPDATA / ACCDATA / FACTDATA): comma-delimited,
    coded values with DT translation tables. Codes are kept as-is; the code
    -> label maps live in analyze_history.py.
  - The 2023-Q1/Q2 and later pipe-delimited files with text labels (same
    layout as fetch_fedscope.py).

The April 2024 - March 2025 flows and the March 2025 employment snapshot come
from fetch_fedscope.py; this module fills in everything before them.

Outputs (data/raw/fedscope/history/, git-tracked, all small):
  separations_FY2015_2019_economists.csv   coded, Oct 2014 - Sep 2019
  separations_FY2020_2023_economists.csv   coded, Oct 2019 - Sep 2023
  separations_202310_202403_economists.csv text,  Oct 2023 - Mar 2024
  accessions_*                             same three windows
  employment_YYYYMM_economists.csv         coded FACTDATA, Sep 1998 - Sep 2024

Usage:
    python src/fetch_fedscope_history.py                  # flows + employment
    python src/fetch_fedscope_history.py --flows-only
    python src/fetch_fedscope_history.py --employment-only
    python src/fetch_fedscope_history.py --overwrite
"""

import argparse
from pathlib import Path

import requests

from fetch_fedscope import (BASE, DOWNLOAD_DIR, FEDSCOPE_DIR, HEADERS,
                            filter_records_from_zip)

HISTORY_DIR = FEDSCOPE_DIR / "history"

# key -> (OPM Files path, local zip name, kind, era)
FLOW_HISTORY = {
    "sep_fy2015_2019":   ("611/004f4b85-fe4f-4e7d-bd7b-2d23033570cb.zip",
                          "separations_FY2015-2019.zip", "separations", "coded"),
    "sep_fy2020_2023":   ("652/21d85c40-bd35-4f20-9359-281a31af39b1.zip",
                          "separations_FY2020-2024.zip", "separations", "coded"),
    "sep_202310_202403": ("773/28054cf5-0127-4039-b7ee-a49774eb3c1e.zip",
                          "separations_202310_to_202403.zip", "separations", "text"),
    "acc_fy2015_2019":   ("610/fd567924-edea-478f-bc5a-24e19efd7243.zip",
                          "accessions_FY2015-2019.zip", "accessions", "coded"),
    "acc_fy2020_2023":   ("649/8caf0a70-9c09-4eb2-844f-71a4f21addfa.zip",
                          "accessions_FY2020-2024.zip", "accessions", "coded"),
    "acc_202310_202403": ("774/48233fa0-36c6-4397-ab63-1468daf49a8b.zip",
                          "accessions_202310_to_202403.zip", "accessions", "text"),
}

# September employment cubes, YYYYMM -> OPM Files path (March 2025 is done by
# fetch_fedscope.py). FACTDATA layout is stable across all of these.
EMPLOYMENT_HISTORY = {
    199809: "77/25455df4-0c25-49f3-a460-147b3aa596c8.zip",
    199909: "74/70967261-28e6-4598-ad8a-69f0f6b04532.zip",
    200009: "71/f74f444b-b84b-4a75-b7d5-83726b80a320.zip",
    200109: "68/22fb81c4-51bb-4309-a9e5-de7fc891d299.zip",
    200209: "65/a5e33b42-51aa-41f0-8d1c-0dcde6c6ff2a.zip",
    200309: "62/ecdd5c00-aeda-45ff-bd74-975714ee10a6.zip",
    200409: "59/b5c2a4f7-5ac5-44f7-bd3c-0f2cfb000e21.zip",
    200509: "56/f00a1a8f-d865-4214-8051-049f66d322be.zip",
    200609: "53/b9945224-54e1-45e3-9780-b6b36b845b4b.zip",
    200709: "50/7b7655fd-b4d0-4e15-9e97-33956b8aca09.zip",
    200809: "38/3653d805-eb0a-4e70-b96d-39b7c58347f0.zip",
    200909: "26/f0a8eef6-a0b5-4015-a2f4-6597f1ca3ae7.zip",
    201009: "172/c21d50d7-9b48-432c-a03e-96d5fb93f5fa.zip",
    201109: "235/caac291b-001d-4568-a8be-96215c319fd4.zip",
    201209: "253/2b43e513-cbfa-4eb5-ae9a-20e718ef1f4e.zip",
    201309: "331/499b1fa1-c354-4c96-b20c-fc18a82bacb8.zip",
    201409: "381/30a3741c-a24d-4f97-9a0e-e45f2ee13773.zip",
    201509: "413/de1dd3f7-0c39-46ab-a1c6-848be284358b.zip",
    201609: "490/ae0351fd-58d1-47d5-b1aa-2ca3bf977d30.zip",
    201709: "522/e4af5225-d9fc-46fa-98f9-b360ed26840d.zip",
    201809: "549/4a840c61-0c6d-41ac-8ffc-a6419b6484e0.zip",
    201909: "600/52da12cd-055e-4e9b-af36-60b2ed9e7d98.zip",
    202009: "621/07f71358-8972-478e-a2cb-fd02f135b7af.zip",
    202109: "633/074d44a6-a8a2-4e35-9b2e-969f2cc8363f.zip",
    202209: "667/fab0e970-bb13-434e-b1df-e867705c7f4e.zip",
    202309: "691/41bdfdda-0ebe-4e19-81f8-5a98d55389b4.zip",
    202409: "721/550993be-94ba-476c-9d66-7f7e8871b07b.zip",
}


def _download(rel: str, local_name: str, overwrite: bool) -> Path:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    dest = DOWNLOAD_DIR / local_name
    if dest.exists() and not overwrite:
        print(f"  {local_name}: cached ({dest.stat().st_size / 1e6:.0f} MB)")
        return dest
    print(f"  downloading {local_name} ...")
    with requests.get(f"{BASE}/{rel}", headers=HEADERS, stream=True, timeout=180) as r:
        r.raise_for_status()
        with open(dest, "wb") as fh:
            for chunk in r.iter_content(chunk_size=1 << 20):
                fh.write(chunk)
    print(f"  {local_name}: {dest.stat().st_size / 1e6:.0f} MB")
    return dest


def fetch_flows(overwrite: bool = False) -> None:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    for key, (rel, zip_name, kind, era) in FLOW_HISTORY.items():
        window = key.split("_", 1)[1]
        out = HISTORY_DIR / f"{kind}_{window}_economists.csv"
        if out.exists() and not overwrite:
            print(f"  {out.name}: exists")
            continue
        zip_path = _download(rel, zip_name, overwrite)
        out.unlink(missing_ok=True)
        if era == "coded":
            suffix = "SEPDATA" if kind == "separations" else "ACCDATA"
            delim = ","
        else:
            suffix, delim = ".txt", "|"
        n = filter_records_from_zip(zip_path, suffix, out, delimiter=delim)
        print(f"  {out.name}: {n} economist rows ({era})")


def fetch_employment(overwrite: bool = False) -> None:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    for yyyymm, rel in EMPLOYMENT_HISTORY.items():
        out = HISTORY_DIR / f"employment_{yyyymm}_economists.csv"
        if out.exists() and not overwrite:
            print(f"  {out.name}: exists")
            continue
        zip_path = _download(rel, f"employment_{yyyymm}.zip", overwrite)
        out.unlink(missing_ok=True)
        n = filter_records_from_zip(zip_path, "FACTDATA", out, delimiter=",")
        print(f"  {out.name}: {n} economist rows")


def write_sources() -> None:
    from datetime import date
    lines = [
        "# Historical FedScope source files",
        "",
        f"Retrieved {date.today().isoformat()} from <https://www.opm.gov/data/datasets/>.",
        "Economist (series 0110 / 0119) rows only; full files are in `../_downloads/`",
        "(git-ignored). Re-create with `python src/fetch_fedscope_history.py`.",
        "",
        "| file | OPM Files path |",
        "| --- | --- |",
    ]
    for rel, zip_name, kind, era in FLOW_HISTORY.values():
        lines.append(f"| {zip_name} | `{rel}` |")
    for yyyymm, rel in EMPLOYMENT_HISTORY.items():
        lines.append(f"| employment_{yyyymm}.zip | `{rel}` |")
    lines += [
        "",
        "## Notes",
        "- Pre-2025 files (`SEPDATA`/`ACCDATA`/`FACTDATA`) are comma-delimited with",
        "  coded values; 2025-era files are pipe-delimited with text labels.",
        "- ~550 Department of State positions were reclassified out of series 0110",
        "  between Sep 2005 and Sep 2006, so pre-2006 headcounts run ~550 high.",
        "- Historical `SALARY` is nominal; `analyze_history.py` deflates with CPI-U.",
        "",
    ]
    (HISTORY_DIR / "SOURCES.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Fetch historical FedScope economist data")
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--flows-only", action="store_true")
    p.add_argument("--employment-only", action="store_true")
    args = p.parse_args()

    if not args.employment_only:
        print("Historical flows (FY2015 - Mar 2024):")
        fetch_flows(overwrite=args.overwrite)
    if not args.flows_only:
        print("\nHistorical employment snapshots (Sep 1998 - Sep 2024):")
        fetch_employment(overwrite=args.overwrite)
    write_sources()
    print("\nDone. Next: python src/analyze_history.py")
