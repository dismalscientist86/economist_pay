"""
Generate all figures for the Beamer slide deck.
Outputs PDF figures to output/figures/.

Usage:
    python src/make_figures.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

TABLES  = Path(__file__).parent.parent / "output" / "tables"
FIGURES = Path(__file__).parent.parent / "output" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

# ── Colour palette ──────────────────────────────────────────────────────────
BLUE   = "#2166AC"
RED    = "#D6604D"
GRAY   = "#888888"
LGRAY  = "#DDDDDD"
PAPER  = "#4DAC26"   # green for paper comparison series

plt.rcParams.update({
    "font.family":      "serif",
    "font.size":        12,
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "axes.linewidth":   0.8,
    "grid.alpha":       0.35,
    "grid.linestyle":   "--",
    "figure.dpi":       150,
})

def save(name):
    plt.tight_layout()
    plt.savefig(FIGURES / f"{name}.pdf", bbox_inches="tight")
    plt.close()
    print(f"  Saved {name}.pdf")


# ── 1. Median salary by gender, 2015-2024 ───────────────────────────────────
def fig_salary_trends():
    df = pd.read_csv(TABLES / "salary_gap_by_year.csv", index_col=0)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Left: median salary levels
    ax = axes[0]
    ax.plot(df.index, df["median_male"]   / 1000, color=BLUE, marker="o", label="Men")
    ax.plot(df.index, df["median_female"] / 1000, color=RED,  marker="s", label="Women")
    ax.set_xlabel("Fiscal Year")
    ax.set_ylabel("Median Salary ($ thousands)")
    ax.set_title("Median Salary by Gender")
    ax.legend(frameon=False)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("$%g"))
    ax.set_xticks(df.index)
    ax.set_xticklabels(df.index, rotation=45)
    ax.grid(axis="y")

    # Right: gap %
    ax = axes[1]
    ax.bar(df.index, df["gap_pct"], color=[BLUE if g > 0 else RED for g in df["gap_pct"]], width=0.6)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Fiscal Year")
    ax.set_ylabel("Men's Advantage (%)")
    ax.set_title("Median Salary Gap (Men − Women) / Men")
    ax.set_xticks(df.index)
    ax.set_xticklabels(df.index, rotation=45)
    ax.grid(axis="y")
    for yr, gap in zip(df.index, df["gap_pct"]):
        ax.text(yr, gap + 0.08, f"{gap:.1f}%", ha="center", va="bottom", fontsize=9)

    save("salary_trends")


# ── 2. Female share of federal economists by key agency, 2016-2024 ──────────
def fig_female_share_agency():
    df = pd.read_csv(TABLES / "female_share_by_agency_year.csv", index_col=0)
    df = df[df.index >= 2016]   # pre-2016 only has "All" and BLS/BEA/Census bureau-level

    # Select columns present throughout
    cols   = {
        "All":                              ("All", "black",  "-",  2.0),
        "Dept of Labor (incl. BLS)":        ("BLS (via Dept of Labor)", BLUE,   "-",  1.4),
        "BEA":                              ("BEA",          RED,   "--", 1.4),
        "Census Bureau":                    ("Census",       PAPER, "-.", 1.4),
        "Dept of Treasury":                 ("Treasury",     GRAY,  ":",  1.4),
        "Dept of Agriculture (incl. ERS)":  ("Agriculture",  "#8073AC", "-", 1.4),
    }

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for col, (label, color, ls, lw) in cols.items():
        if col in df.columns:
            ax.plot(df.index, df[col], color=color, linestyle=ls,
                    linewidth=lw, marker="o", markersize=4, label=label)

    ax.set_xlabel("Fiscal Year")
    ax.set_ylabel("Female Share (%)")
    ax.set_title("Female Share of Federal Economists by Agency")
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.set_xticks(df.index)
    ax.set_xticklabels(df.index, rotation=45)
    ax.set_ylim(20, 55)
    ax.grid(axis="y")
    save("female_share_agency")


# ── 3. Salary by GS grade and gender (most recent year) ─────────────────────
def fig_grade_salary():
    df = pd.read_csv(TABLES / "salary_by_grade_all_years.csv")
    df = df.rename(columns={"Unnamed: 0": "grade", "Unnamed: 1": "gender"})
    # Reshape: grade, gender, median
    df = df.dropna(subset=["grade"])
    df["grade"] = pd.to_numeric(df["grade"], errors="coerce")
    df = df[df["grade"].between(7, 15)]

    male   = df[df["gender"] == "male"].set_index("grade")["median"]
    female = df[df["gender"] == "female"].set_index("grade")["median"]
    grades = sorted(set(male.index) & set(female.index))

    x = np.arange(len(grades))
    w = 0.35

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x - w/2, [male[g]   / 1000 for g in grades], w, color=BLUE, label="Men",   alpha=0.9)
    ax.bar(x + w/2, [female[g] / 1000 for g in grades], w, color=RED,  label="Women", alpha=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels([f"GS-{int(g)}" for g in grades])
    ax.set_xlabel("GS Grade")
    ax.set_ylabel("Median Salary ($ thousands)")
    ax.set_title("Median Salary by GS Grade and Gender (FY2015-2024 pooled)")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("$%g"))
    ax.legend(frameon=False)
    ax.grid(axis="y")
    save("grade_salary")


# ── 4. Salary gap by agency (all years) ──────────────────────────────────────
def fig_agency_gap():
    df = pd.read_csv(TABLES / "salary_by_agency_all_years.csv")
    df.columns = ["agency", "gender", "n", "median", "mean"]
    df = df.dropna(subset=["agency", "gender"])

    pivot = df.pivot_table(index="agency", columns="gender", values="median")
    pivot = pivot.dropna()
    pivot["gap_pct"] = (pivot["male"] - pivot["female"]) / pivot["male"] * 100

    # Drop "Dept of Commerce (other)" — too few and mixed
    pivot = pivot[~pivot.index.str.startswith("Dept of Commerce")]

    # Shorten labels
    label_map = {
        "BEA":                              "BEA",
        "BLS":                              "BLS",
        "Census Bureau":                    "Census Bureau",
        "Departmental Offices":             "Dept. Offices",
        "Dept of Agriculture (incl. ERS)":  "Agriculture (incl. ERS)",
        "Dept of Energy":                   "Energy",
        "Dept of HHS":                      "HHS",
        "Dept of Labor (incl. BLS)":        "Labor (incl. BLS)",
        "Dept of Treasury":                 "Treasury",
        "Economic Research Service":        "ERS (FY2015)",
        "Internal Revenue Service":         "IRS (FY2015)",
        "Other":                            "Other",
    }
    pivot.index = [label_map.get(i, i) for i in pivot.index]
    pivot = pivot.sort_values("gap_pct")

    colors = [RED if g < 0 else BLUE for g in pivot["gap_pct"]]

    fig, ax = plt.subplots(figsize=(8, 5.5))
    bars = ax.barh(pivot.index, pivot["gap_pct"], color=colors, alpha=0.85)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Men's Salary Advantage (%)\n(negative = women earn more)")
    ax.set_title("Median Salary Gap by Agency (FY2015-2024 pooled)")
    ax.grid(axis="x")
    for bar, val in zip(bars, pivot["gap_pct"]):
        xpos = val + 0.1 if val >= 0 else val - 0.1
        ha   = "left"  if val >= 0 else "right"
        ax.text(xpos, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", ha=ha, fontsize=9)
    save("agency_gap")


# ── 5. Placement sector shares: our data vs. Early Career Paths paper ────────
def fig_placement_comparison():
    # Paper values from Table 1 (all programs)
    sectors = ["Academia", "Government", "Finance /\ncentral banks", "Consulting /\nprivate sector"]

    our_0107  = [58.1, 5.3, 9.1, 21.4]
    our_1417  = [63.0, 3.6, 7.3, 22.2]
    paper_0107 = [60.0, 5.0, 9.0, 22.0]
    paper_1417 = [54.0, 11.0, 9.0, 26.0]

    x  = np.arange(len(sectors))
    w  = 0.2

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - 1.5*w, our_0107,   w, color=BLUE,  alpha=0.85, label="EconPhDPlacements, 2001-07")
    ax.bar(x - 0.5*w, our_1417,   w, color=BLUE,  alpha=0.50, label="EconPhDPlacements, 2014-17")
    ax.bar(x + 0.5*w, paper_0107, w, color=PAPER, alpha=0.85, label="Foster et al. (2023, JEP), 2001-07")
    ax.bar(x + 1.5*w, paper_1417, w, color=PAPER, alpha=0.50, label="Foster et al. (2023, JEP), 2014-17")

    ax.set_xticks(x)
    ax.set_xticklabels(sectors)
    ax.set_ylabel("Share of Placements (%)")
    ax.set_title("Initial Placement Shares: EconPhDPlacements vs. Foster et al. (2023, JEP)")
    ax.legend(frameon=False, fontsize=9)
    ax.grid(axis="y")

    note = ("Note: 'International orgs' (4-6% in EconPhDPlacements) not captured in paper (LEHD = US only).\n"
            "Paper: Foster, McEntarfer & Sandler (2023, JEP). Govt in paper = NAICS 92 only.")
    ax.text(0.01, -0.18, note, transform=ax.transAxes, fontsize=7.5,
            color=GRAY, va="top")
    save("placement_comparison")


# ── 6. Placement sector shares over time (our data) ──────────────────────────
def fig_placement_trends():
    df = pd.read_csv(TABLES / "placements_by_category_year.csv")
    df = df[df["year"] >= 2001]

    # Compute share within year
    totals = df.groupby("year")["n"].sum()
    df["share"] = df.apply(lambda r: r["n"] / totals[r["year"]] * 100, axis=1)

    cat_map = {
        "tenure_track":      "Tenure-track",
        "other_academic":    "Other academic",
        "private_sector":    "Private sector",
        "central_banks":     "Central banks",
        "government":        "Government",
        "think_tanks":       "Think tanks",
        "international_orgs":"International orgs",
    }
    colors_map = {
        "Tenure-track":      BLUE,
        "Other academic":    "#6BAED6",
        "Private sector":    RED,
        "Central banks":     "#FD8D3C",
        "Government":        PAPER,
        "Think tanks":       "#74C476",
        "International orgs":"#8073AC",
    }

    pivot = df.pivot_table(index="year", columns="category", values="share", aggfunc="sum").fillna(0)
    pivot.columns = [cat_map.get(c, c) for c in pivot.columns]

    # Smooth with 3-year rolling average for readability
    pivot_smooth = pivot.rolling(3, center=True, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(9, 5))
    for col in ["Tenure-track", "Other academic", "Private sector",
                "Central banks", "Government", "Think tanks", "International orgs"]:
        if col in pivot_smooth.columns:
            ax.plot(pivot_smooth.index, pivot_smooth[col],
                    color=colors_map[col], linewidth=1.8, label=col)

    ax.set_xlabel("Placement Year")
    ax.set_ylabel("Share of Placements (%, 3-yr moving avg.)")
    ax.set_title("PhD Economist Placement Shares Over Time")
    ax.legend(frameon=False, fontsize=8.5, loc="upper right", ncol=2)
    ax.set_xlim(2001, 2025)
    ax.grid(axis="y")
    save("placement_trends")


# ── 7. Female share by sector: our data vs. Diversity & Equity paper ─────────
def fig_female_sector_comparison():
    sectors   = ["Academia", "Industry", "Government\n(broad)"]
    ours_all  = [30.6, 30.4, 29.4]
    ours_0117 = [29.6, 31.2, 29.9]
    ours_1417 = [27.3, 28.2, 31.9]
    paper     = [32.8, 35.9, 38.5]

    x  = np.arange(len(sectors))
    w  = 0.18

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x - 1.5*w, ours_0117, w, color=BLUE,  alpha=0.85, label="EconPhDPlacements, 2001-17")
    ax.bar(x - 0.5*w, ours_1417, w, color=BLUE,  alpha=0.50, label="EconPhDPlacements, 2014-17")
    ax.bar(x + 0.5*w, ours_all,  w, color=BLUE,  alpha=0.30, label="EconPhDPlacements, all years")
    ax.bar(x + 1.5*w, paper,     w, color=PAPER, alpha=0.85, label="Foster et al. (2023, JERP), 2017")

    ax.set_xticks(x)
    ax.set_xticklabels(sectors)
    ax.set_ylabel("Female Share (%)")
    ax.set_title("Female Share by Sector: EconPhDPlacements vs. Foster et al. (2023, JERP)")
    ax.axhline(34.6, color=PAPER, linestyle="--", linewidth=1.2, label="Paper overall (34.6%)")
    ax.legend(frameon=False, fontsize=8.5)
    ax.set_ylim(0, 50)
    ax.grid(axis="y")

    note = ("Note: Gender assigned via gender_guesser (50.5% of placements). Unassigned names\n"
            "skew international (likely male-heavy), so our female shares are likely understated.\n"
            "Paper uses self-reported SED gender (100% coverage). D&E = Diversity & Equity in\n"
            "Labor Market Outcomes for Economists (Foster, McEntarfer & Sandler, 2023, JERP).")
    ax.text(0.01, -0.28, note, transform=ax.transAxes, fontsize=7.5, color=GRAY, va="top")
    save("female_sector_comparison")


# ── 8. Federal salary gap vs. OPM paper comparison ───────────────────────────
def fig_salary_comparison_paper():
    """
    Side-by-side: our raw median gap vs. Foster et al. 2020 (OPM data) raw log gap.
    Both compare all federal economists; paper covers 2000-2015.
    """
    df = pd.read_csv(TABLES / "salary_gap_by_year.csv", index_col=0)

    # Paper's OPM result: raw log gap for white females = -1.41%;
    # with controls = -0.53%.  Shown as horizontal reference bands.
    fig, ax = plt.subplots(figsize=(8, 4.5))

    ax.plot(df.index, df["gap_pct"], color=BLUE, marker="o", linewidth=2,
            label="FedsDataCenter (median gap)")

    ax.axhspan(0, 1.41, alpha=0.12, color=PAPER,
               label="Foster et al. 2020 (OPM): raw gap for white women (1.4%)")
    ax.axhspan(0, 0.53, alpha=0.22, color=PAPER,
               label="Foster et al. 2020 (OPM): gap with agency+year controls (0.5%)")

    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Fiscal Year")
    ax.set_ylabel("Men's Salary Advantage (%)")
    ax.set_title("Federal Economist Gender Salary Gap: FedsDataCenter vs. Prior Work")
    ax.legend(frameon=False, fontsize=8.5, loc="upper right")
    ax.set_xticks(df.index)
    ax.set_xticklabels(df.index, rotation=45)
    ax.set_ylim(-1, 6)
    ax.grid(axis="y")

    note = ("Our gap: raw median comparison (no controls). Paper gap: log earnings regression.\n"
            "Paper: Foster, Manzella, McEntarfer & Sandler (2020, AEA P&P), OPM data 2000-2015.")
    ax.text(0.01, -0.18, note, transform=ax.transAxes, fontsize=7.5, color=GRAY, va="top")
    save("salary_comparison_paper")


# ── Run all ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating figures...")
    fig_salary_trends()
    fig_female_share_agency()
    fig_grade_salary()
    fig_agency_gap()
    fig_placement_comparison()
    fig_placement_trends()
    fig_female_sector_comparison()
    fig_salary_comparison_paper()
    print(f"Done. All figures saved to {FIGURES}/")
