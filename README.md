# economist_pay

Analysis of compensation and career outcomes for economists in the federal government, with a focus on gender differences.

## Data sources

### 1. FedsDataCenter.com — federal salary data (FY2015–2024)
Individual-level salary and bonus records for all federal employees with occupation "Economist", sourced from OPM data released via FOIA. Covers agencies that report to OPM. Fetched programmatically from the FedsDataCenter JSON API.

Columns: `name, grade, pay_plan, salary, bonus, agency, location, occupation, year`

### 2. PhD placement data *(forthcoming)*
Placement outcomes for newly minted PhD economists. Expected columns: `name, year, department, field, placement, category`. Place CSV in `data/raw/phd_placements/`.

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
│   │   └── phd_placements/   # PhD placement data (place CSV here)
│   └── processed/             # Cleaned panel data and gender cache
├── src/
│   ├── utils.py               # Shared helpers (name parsing, numeric cleaning)
│   ├── fetch_salary_data.py   # Download all years from FedsDataCenter API
│   ├── assign_gender.py       # Build gender lookup using gender_guesser
│   ├── clean_merge.py         # Parse names, merge gender, create panel
│   ├── analyze.py             # Descriptive stats by gender/agency/pay plan
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
```

Individual steps can also be run directly:

```bash
python src/fetch_salary_data.py --year 2024   # fetch one year
python src/assign_gender.py                    # build/rebuild gender cache
python src/clean_merge.py                      # merge all years
python src/analyze.py --year 2024             # analyze one year
```

## Gender assignment

Gender is assigned using [`gender_guesser`](https://pypi.org/project/gender-guesser/), an offline library covering ~40,000 names. First names are parsed from OPM's `LAST,FIRST MIDDLE` format. When the first token is a single initial, the pipeline falls back to the second or third name token. The library returns six categories; `male`/`mostly_male` → male, `female`/`mostly_female` → female, `andy`/`unknown` → unassigned. Results are cached in `data/processed/gender_cache.csv`.

## Original work

The original Stata analysis was conducted by Julia Manzella and Dani (June–July 2018). Legacy code is preserved in `legacy/stata/`.
