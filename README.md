# economist_pay

Analysis of compensation and career outcomes for economists in the federal government, with a focus on gender differences.

## Data sources

### 1. FedsDataCenter.com — federal salary data (FY2015–2024)
Individual-level salary and bonus records for all federal employees with occupation "Economist", sourced from OPM data released via FOIA. Covers agencies that report to OPM. Fetched programmatically from the FedsDataCenter JSON API.

Columns: `name, grade, pay_plan, salary, bonus, agency, location, occupation, year`

### 2. PhD placement data *(forthcoming)*
Placement outcomes for newly minted PhD economists. Expected columns: `name, year, department, field, placement, category`. Place CSV in `data/raw/phd_placements/`.

### 3. OPM FedScope — 2025 update
FedsDataCenter stops at FY2024. To ask whether the number and pay of federal economists changed into 2025, the project uses OPM's FedScope "classic" raw datasets: the preliminary **March 2025** employment snapshot with **September 2024** bundled for comparison, plus April 2024–March 2025 accessions/separations. `src/fetch_fedscope.py` downloads these and extracts the economist rows (occupational series 0110 / 0119).

This source has **no gender or race** — OPM removed those fields as of March 2025 (EOs 14151/14168/14173) — so the 2025 update is aggregate-only; the gender analysis above covers years ≤2024. It is also a different universe from FedsDataCenter (EHRI month-end status vs. annual FOIA extract), the March 2025 snapshot is preliminary and still counts administrative-leave / deferred-resignation staff as employed, and small agency×grade cells are suppressed. See `docs/2025_update_plan.md`.

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
│   │   ├── fedscope/          # OPM FedScope economist extracts (2025 update)
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
│   └── Notes.txt              # Original project notes
├── main.py                    # Full pipeline runner
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
python src/make_figures.py --only fedscope2025

# ...with long-run context (employment to 1998, separations to FY2015; ~550 MB)
python main.py --fedscope --history
```

Individual steps can also be run directly:

```bash
python src/fetch_salary_data.py --year 2024   # fetch one year
python src/assign_gender.py                    # build/rebuild gender cache
python src/clean_merge.py                      # merge all years
python src/analyze.py --year 2024             # analyze one year
python src/fetch_fedscope.py                   # download + extract FedScope economists
python src/clean_fedscope.py                   # build the fedscope_* processed tables
python src/analyze_2025.py                     # 2024→2025 comparison tables
```

## Gender assignment

Gender is assigned using [`gender_guesser`](https://pypi.org/project/gender-guesser/), an offline library covering ~40,000 names. First names are parsed from OPM's `LAST,FIRST MIDDLE` format. When the first token is a single initial, the pipeline falls back to the second or third name token. The library returns six categories; `male`/`mostly_male` → male, `female`/`mostly_female` → female, `andy`/`unknown` → unassigned. Results are cached in `data/processed/gender_cache.csv`.

## Original work

The original Stata analysis was conducted by Julia Manzella and Dani (June–July 2018). Legacy code is preserved in `legacy/stata/`.
