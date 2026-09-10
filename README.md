# economist_pay

Analysis of compensation and career outcomes for economists in the federal government, with a focus on gender differences.

## Data sources

### 1. FedsDataCenter.com — federal salary data (FY2015–2024)
Individual-level salary and bonus records for all federal employees with occupation "Economist", sourced from OPM data released via FOIA. Covers agencies that report to OPM. Fetched programmatically from the FedsDataCenter JSON API.

Columns: `name, grade, pay_plan, salary, bonus, agency, location, occupation, year`

### 2. PhD placement data *(forthcoming)*
Placement outcomes for newly minted PhD economists. Expected columns: `name, year, department, field, placement, category`. Place CSV in `data/raw/phd_placements/`.

### 3. OPM FedScope — 2025 update and long-run history
FedsDataCenter stops at FY2024. To ask whether the number and pay of federal economists changed into 2025, the project uses OPM's FedScope "classic" raw datasets (occupational series 0110 / 0119):

- **`src/fetch_fedscope.py`** — the preliminary **March 2025** employment snapshot with **September 2024** bundled for comparison, plus April 2024–March 2025 accessions/separations.
- **`src/fetch_fedscope_history.py`** — September employment cubes back to **1998** and separation/accession files back to **FY2015**, for long-run context (~550 MB of downloads; the economist extracts are ~11 MB and committed).

This source has **no gender or race** — OPM removed those fields as of March 2025 (EOs 14151/14168/14173) — so the 2025 update is aggregate-only; the gender analysis above covers years ≤2024. It is also a different universe from FedsDataCenter (EHRI month-end status vs. annual FOIA extract), the March 2025 snapshot is preliminary and still counts administrative-leave / deferred-resignation staff as employed, and small agency×grade cells are suppressed. Pre-2006 headcounts include ~550 Department of State positions later reclassified out of series 0110. Full method and caveats: `docs/2025_update_plan.md`; findings memo: `docs/2025_update.md`.

### Legacy data (see `data/raw/fedsdatacenter/`)
- `Federal-Employee-Salaries_FY2015.xlsx` — original FY2015 download from FedsDataCenter
- `FederalPay.xlsx` — partial FederalPay.org time series (manual collection, 2004+)
- `Census_BLS_BEA_Economists.xlsx` — targeted Census/BLS/BEA economist data with PhD dates

## Directory structure

```
economist_pay/
├── data/
│   ├── raw/
│   │   ├── fedsdatacenter/    # Raw CSVs from API, one per fiscal year
│   │   ├── fedscope/          # OPM FedScope economist extracts (2025)
│   │   │   └── history/       # ...and back to 1998 (employment) / FY2015 (flows)
│   │   └── phd_placements/   # PhD placement data (place CSV here)
│   └── processed/             # Cleaned panel data, gender cache, fedscope_* tables
├── src/
│   ├── utils.py               # Shared helpers (name parsing, numeric cleaning)
│   ├── fetch_salary_data.py   # Download all years from FedsDataCenter API
│   ├── assign_gender.py       # Build gender lookup using gender_guesser
│   ├── clean_merge.py         # Parse names, merge gender, create panel
│   ├── analyze.py             # Descriptive stats by gender/agency/pay plan
│   ├── fetch_fedscope.py      # Download OPM FedScope, extract economist rows (2025)
│   ├── clean_fedscope.py      # Build Sept 2024 / March 2025 economist tables
│   ├── analyze_2025.py        # 2024->2025 headcount, pay, agency, grade, flows
│   ├── fetch_fedscope_history.py  # FedScope employment cubes to 1998, flows to FY2015
│   ├── analyze_history.py     # Long-run economist headcount, pay, separations
│   ├── make_figures.py        # All slide-deck figures
│   └── phd_placements.py      # PhD placement analysis module
├── notebooks/                 # Jupyter notebooks for exploration
├── output/
│   ├── tables/                # CSV output tables
│   └── figures/               # Plots
├── legacy/
│   └── stata/                 # Original Stata .do files (Julia Manzella, 2018)
├── docs/
│   ├── Notes.txt              # Original project notes
│   ├── 2025_update_plan.md    # Plan + data landscape for the FedScope extension
│   └── 2025_update.md         # Findings memo: has federal economist pay/headcount changed?
├── main.py                    # Full pipeline runner (--fedscope, --history)
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
```

## Running the pipeline

```bash
# Full pipeline: fetch → gender → merge → analyze
python main.py

# Skip download if raw files already exist
python main.py --skip-fetch

# Single year or custom range
python main.py --start 2020 --end 2024

# PhD placement analysis (after placing data in data/raw/phd_placements/)
python src/phd_placements.py

# 2025 update (OPM FedScope): fetch → clean → analyze the 2024→2025 change
python main.py --fedscope

# ...with long-run context (employment to 1998, separations to FY2015; ~550 MB)
python main.py --fedscope --history

# regenerate all figures (or just the 2025 group)
python src/make_figures.py
python src/make_figures.py --only fedscope2025
```

Individual steps can also be run directly:

```bash
python src/fetch_salary_data.py --year 2024    # fetch one year (FedsDataCenter)
python src/assign_gender.py                     # build/rebuild gender cache
python src/clean_merge.py                       # merge all years
python src/analyze.py --year 2024              # analyze one year

python src/fetch_fedscope.py                    # download + extract FedScope economists (2025)
python src/clean_fedscope.py                    # build the fedscope_* processed tables
python src/analyze_2025.py                      # 2024→2025 comparison tables

python src/fetch_fedscope_history.py            # employment cubes to 1998, flows to FY2015
python src/fetch_fedscope_history.py --flows-only    # just the separation/accession files
python src/analyze_history.py                   # long-run headcount, pay, separation-reason tables
```

### 2025 update outputs

Tables in `output/tables/` (all `fedscope_`-prefixed):

| file | contents |
|---|---|
| `fedscope_headline_2024_2025.csv` | headcount, mean pay (nominal + real), length of service |
| `fedscope_pay_change_decomp.csv` | GS mean-pay change split into raise / steps / grade-mix |
| `fedscope_pay_distribution_2025.csv` | March 2025 pay percentiles |
| `fedscope_by_agency_change.csv` · `fedscope_cell_coverage_2025.csv` | per-agency change, with coverage flags |
| `fedscope_by_grade_change.csv` · `fedscope_profile_2025.csv` | grade mix; March 2025 profile by pay plan / appointment / age / education |
| `fedscope_flows_{monthly,quarterly,by_reason}_2025.csv` · `fedscope_flows_profile_2025.csv` | hires vs. departures, and why people left |
| `fedscope_definition_sensitivity.csv` | headline under 0110 / 0110+0119 / PhD-only |
| `fedscope_economists_since_1998.csv` | 27-year headcount, real pay, PhD share, seniority *(`--history`)* |
| `fedscope_separations_by_fy_reason.csv` · `fedscope_flows_q1_2015_2025.csv` · `fedscope_separation_rate_by_fy.csv` | separations by fiscal year / reason, and a Jan–Mar cross-year comparison *(`--history`)* |

Figures in `output/figures/` (`make_figures.py --only fedscope2025`):

| file | shows |
|---|---|
| `fed_economists_2025.pdf` | headcount + real pay, FedScope only (2013–2025), no source break |
| `econ_pay_distribution_2025.pdf` | March 2025 pay distribution |
| `econ_agency_change_2025.pdf` | headcount change by agency, Sep 2024 → Mar 2025 |
| `econ_grade_mix_2025.pdf` | GS grade mix, before vs. after |
| `econ_flows_2025.pdf` · `econ_separation_reasons_2025.pdf` | monthly hires/departures; departures by reason and quarter |
| `econ_headcount_since_1998.pdf` | 27-year headcount and real-pay series *(`--history`)* |
| `econ_separations_history.pdf` · `econ_q1_history.pdf` | separations by fiscal year/reason; first-quarter flows 2015–2025 *(`--history`)* |

## Gender assignment

Gender is assigned using [`gender_guesser`](https://pypi.org/project/gender-guesser/), an offline library covering ~40,000 names. First names are parsed from OPM's `LAST,FIRST MIDDLE` format. When the first token is a single initial, the pipeline falls back to the second or third name token. The library returns six categories; `male`/`mostly_male` → male, `female`/`mostly_female` → female, `andy`/`unknown` → unassigned. Results are cached in `data/processed/gender_cache.csv`.

## Original work

The original Stata analysis was conducted by Julia Manzella and Dani (June–July 2018). Legacy code is preserved in `legacy/stata/`.
