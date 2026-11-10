"""
Crosswalk between the agency names in the Federal-Remote-Work telework CSVs and
FedScope's two-letter agency codes, plus a loader for those CSVs.

The CSVs live in the Federal-Remote-Work submodule:
  2024_rates_of_inperson_work_by_agency.csv   % hours in person, remote headcount
  2024_return_to_office_plans.csv             in-person-day mandates and dates

Agency names differ between the two files ("Department of Labor" vs "Labor
Department"; "NASA"; "USAID"), and FedScope splits DoD into four agencies
(Army, Navy, Air Force, other defense). Both are handled here.
"""

from pathlib import Path

import pandas as pd

REMOTE_DIR = Path(__file__).parent.parent / "Federal-Remote-Work"

# CSV agency name -> FedScope AGY code(s)
XWALK = {
    "Department of Agriculture": ["AG"], "Agriculture Department": ["AG"],
    "Department of Commerce": ["CM"], "Commerce Department": ["CM"],
    "Department of Defense": ["AR", "NV", "AF", "DD"], "Defense Department": ["AR", "NV", "AF", "DD"],
    "Department of Education": ["ED"], "Education Department": ["ED"],
    "Department of Energy": ["DN"], "Energy Department": ["DN"],
    "Department of Health and Human Services": ["HE"],
    "Department of Homeland Security": ["HS"],
    "Department of Housing and Urban Development": ["HU"],
    "Department of Justice": ["DJ"], "Justice Department": ["DJ"],
    "Department of Labor": ["DL"], "Labor Department": ["DL"],
    "Department of State": ["ST"], "State Department": ["ST"],
    "Department of the Interior": ["IN"], "Interior Department": ["IN"],
    "Department of the Treasury": ["TR"], "Treasury Department": ["TR"],
    "Department of Transportation": ["TD"], "Transportation Department": ["TD"],
    "Department of Veterans Affairs": ["VA"],
    "Environmental Protection Agency": ["EP"],
    "General Services Administration": ["GS"],
    "National Aeronautics and Space Administration": ["NN"], "NASA": ["NN"],
    "National Science Foundation": ["NF"],
    "Nuclear Regulatory Commission": ["NU"],
    "Office of Personnel Management": ["OM"],
    "Small Business Administration": ["SB"],
    "Social Security Administration": ["SZ"],
    "U.S. Agency for International Development": ["AM"], "USAID": ["AM"],
}

SHORT = {
    "Department of Agriculture": "USDA", "Department of Commerce": "Commerce",
    "Department of Defense": "DoD", "Department of Education": "Education",
    "Department of Energy": "Energy", "Department of Health and Human Services": "HHS",
    "Department of Homeland Security": "DHS",
    "Department of Housing and Urban Development": "HUD",
    "Department of Justice": "DOJ", "Department of Labor": "Labor",
    "Department of State": "State", "Department of the Interior": "Interior",
    "Department of the Treasury": "Treasury", "Department of Transportation": "DOT",
    "Department of Veterans Affairs": "VA", "Environmental Protection Agency": "EPA",
    "General Services Administration": "GSA",
    "National Aeronautics and Space Administration": "NASA",
    "National Science Foundation": "NSF", "Nuclear Regulatory Commission": "NRC",
    "Office of Personnel Management": "OPM", "Small Business Administration": "SBA",
    "Social Security Administration": "SSA",
    "U.S. Agency for International Development": "USAID",
}


def load_telework_exposure() -> pd.DataFrame:
    """One row per agency with 2024 in-person / remote exposure and an AGY list."""
    path = REMOTE_DIR / "2024_rates_of_inperson_work_by_agency.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing. Run: git submodule update --init")
    r = pd.read_csv(path, encoding="utf-8-sig")        # file has a BOM
    r = r[r["Agency"] != "All agencies combined"].copy()
    for c in ["Total hrs. in person", "Teleworkers' hrs. in person"]:
        r[c] = r[c].str.rstrip("%").astype(float)
    r = r.rename(columns={"Total hrs. in person": "inperson_pct",
                          "Teleworkers' hrs. in person": "tw_inperson_pct"})
    r["remote_share"] = r["Remote employees"] / r["Total employees"]
    r["tw_eligible_share"] = r["Telework-eligible employees"] / r["Total employees"]
    r["agy"] = r["Agency"].map(XWALK)
    r["short"] = r["Agency"].map(SHORT)
    return r.reset_index(drop=True)
