# 2025 update — analysis plan

**Question.** Has the number and pay of economists in the federal government changed in the
last year?

**Status.** Plan approved 2026-09-09. Not yet implemented. Decisions locked:

- **Aggregate-only for 2025.** No gender dimension for the new data (see "Data landscape"
  below). The existing gender analysis (`src/analyze.py`, `economists_panel.csv`) is left
  untouched and remains the record through FY2024.
- **Comparison window: September 2024 → March 2025**, single source (FedScope). No
  cross-source splicing for level comparisons.
- **Economist = occupational series 0110.** Series 0119 ("Economics Assistant") reported
  separately as a sensitivity check, not folded into the headline.

---

## Data landscape

| Source | Latest period | Granularity | Gender | Salary field | Usable here |
|---|---|---|---|---|---|
| FedsDataCenter.com API (`src/fetch_salary_data.py`) | **FY2024** | individual + name | inferred from first name | exact base + bonus | No 2025 data — dropdown and API stop at 2024 |
| **FedScope classic — raw datasets** (opm.gov/data/datasets) | **March 2025** (preliminary, posted 2025-07-01) | de-identified, one row per employee, 3 files | **removed** | `SALARY` = annualized adjusted basic pay | Yes — `.zip` downloads succeed from this environment |
| **FedScope classic — summary cross-tabs** | March 2025 **and** Sept 2024 (bundled) | pre-aggregated (occ, agency, grade, pay plan, location, age, education, appointment type) | **removed** | `AVGSAL` only | Yes |
| OPM Federal Workforce Data API (data.opm.gov/api/v1/files) | ~July 2026, monthly | de-identified record-level (parquet) | **removed** | exact | Blocked — Akamai returns 503 to this environment |

**Why no gender.** Per Executive Orders 14151, 14168, and 14173, OPM removed sex, race,
and related demographic elements from FedScope and the new Federal Workforce Data platform
beginning with the March 2025 release. There is currently no public source for
gender-disaggregated 2025 federal workforce data.

**Why single-source.** The FedScope universe (≈4,998 economists in Sept 2024) does not match
the FedsDataCenter FY2024 file (4,718 economist records): different construction (EHRI
month-end status snapshot vs. annual FOIA extract), deduplication, and coverage. Splicing
the two would confound real change with a definitional break. The FedScope March 2025
release deliberately ships the Sept 2024 snapshot alongside for a clean comparison, so we
use that.

### Preliminary headline (from the summary cross-tab, series 0110)

| | Sept 2024 | March 2025 | Change |
|---|---|---|---|
| Economists (headcount) | 4,998 | 4,888 | −110 (−2.2%) |
| Avg adjusted basic pay | $146,952 | $151,094 | +$4,142 (+2.8%) |
| Avg length of service | 12.4 yr | 12.6 yr | +0.2 yr |

From the record-level March 2025 file: median adjusted basic pay $148,716, mean $152,416
(the mean runs above OPM's $151,094 because the ~4.5% redacted/DoD tail is excluded).

Flows (economist series 0110, April 2024 – March 2025): **317 accessions, 356 separations**
— and **137 of those separations fell in January–March 2025** alone (roughly a doubling of
the prior quarterly pace), so the early-2025 departures are already visible in the flow
data even though the March 2025 headcount snapshot doesn't fully reflect them.

---

## Known limitations (to state prominently in every output)

1. **6 months, not 12.** Sept 2024 → March 2025 is a half-year window. It is not a
   like-for-like "last year" comparison; it is the cleanest single-source comparison
   currently available.
2. **March 2025 is preliminary.** OPM flags it as subject to revision while agencies
   validate submissions.
3. **Understates the decline.** OPM states the March 2025 snapshot "does not reflect
   expected Federal workforce reshaping activities" — employees on administrative leave
   pending resignation, retirement, or release are still counted as current. The
   deferred-resignation and RIF effects of early 2025 are largely not yet visible.
4. **No gender.** The 2025 update cannot speak to gender differences.
5. **Universe differs from the historical panel.** FedScope numbers are not directly
   comparable in levels to the FedsDataCenter FY2015–2024 series; trend charts must label
   the source break.
6. **Suppression and masking.** Duty stations in MD, VA, and WV are recoded to DC. In the
   record-level March 2025 file, fully-redacted rows (mostly DoD) can't be identified as
   economists — the record-level extract is ~4,670 vs OPM's summary total of 4,888 (~4.5%
   lost). In the agency × pay-plan × grade summary, cells of ≤10 are omitted entirely, so
   only ~3,730–3,780 of ~4,900 economists (~76%) appear in that breakdown on **both** dates;
   the suppressed tail is concentrated in smaller agencies.
7. **No record-level September 2024.** OPM only publishes September 2024 as pre-aggregated
   summaries (it's bundled into the March 2025 release). So the September 2024 side gives an
   exact total and mean pay, and grade-level means for the larger cells — but no salary
   distribution, no percentiles, and no person-level cross-tabs. Full record-level September
   2024 needs the data.opm.gov monthly API (see "Deferred").
8. **Coverage gaps.** Some Department of Defense / Department of War components had late or
   missing submissions in 2025–2026 releases.

---

## Work plan

### Phase 1 — ingest ✅ done (2026-09-09)

**`src/fetch_fedscope.py`** — downloads six OPM zips to `data/raw/fedscope/_downloads/`
(git-ignored, ~1 GB unzipped) and extracts just the economist rows:
- Employment record-level files 1–3 (pipe-delimited, 31 cols) → filter `OCC ∈ {0110, 0119}`
  → `employment_202503_economists.csv` (5,001 rows: 4,670 series-0110 + 331 assistants).
- Employment summary cross-tabs → `summary/` (the "by Occupation" and "by Pay Plan and
  Grade" tables verbatim; the 40k-row Agency × PayPlan × Grade × Series table filtered to
  200 economist rows).
- Accessions and Separations record-level (Apr 2024 – Mar 2025) → filter to economists →
  `accessions_…` / `separations_…_economists.csv` (385 / 414 rows).
- Writes `data/raw/fedscope/SOURCES.md` (URLs, retrieval date, caveats).
- `--overwrite` re-fetches; `--no-keep-downloads` drops the cache.

**`src/clean_fedscope.py`** — four analysis-ready tables in `data/processed/`:
- `fedscope_economists_202503.csv` — one row per identifiable economist, March 2025;
  standardized columns (`snapshot, series, agency, agency_group, pay_plan, grade,
  grade_num, salary, state, age_band, education, los, appointment_type, is_permanent,
  supervisory, is_supervisor, work_schedule, stem`); `SALARY == REDACTED` → NaN (12 rows);
  `agency_group` via sub-element codes (DLLS→BLS, CM53→BEA, CM63→Census, AG18→ERS).
- `fedscope_economist_totals.csv` — Sept 2024 & March 2025 headcount, mean pay, mean LOS
  (from the "by Occupation" summary; exact, complete).
- `fedscope_economist_cells.csv` — agency × pay-plan × grade panel, both snapshots (the
  ~76%-coverage breakdown; small cells suppressed).
- `fedscope_economist_flows.csv` — economist accessions + separations, monthly, stacked
  with a `direction` column.

No `gender`, `name`, or `bonus` — not in this source.

### Phase 2 — analysis (`src/analyze_2025.py`, new)

All tables written to `output/tables/`, all figures to `output/figures/`, mirroring the
existing `run_all()` pattern.

1. **Headcount change.** Total economists Sept 2024 vs March 2025; percent change; the
   FedScope point plotted against the FY2015–2024 FedsDataCenter trend with an explicit
   source-break annotation.
2. **Pay change.** Mean pay both dates (exact); median and full distribution for March 2025
   from the record-level file; Sept 2024 distribution approximated from grade-cell means
   (no record-level Sept 2024). Nominal and real (deflated by CPI-U and, separately, ECI).
   Decompose the nominal mean change into:
   - the January 2025 GS pay-schedule adjustment (≈2.0% average: 1.7% base + 0.3% locality),
   - grade/pay-plan mix shift (reweight March 2025 grades at Sept 2024 cell means),
   - within-grade residual movement (uses the ~76%-coverage cells; flag the suppressed tail).
3. **By agency.** Headcount and average pay change per department/bureau; which gained and
   lost economists; a waterfall from Sept 2024 to March 2025 totals. Concentration among
   the big employers (Labor/BLS, Treasury, Agriculture/ERS, Commerce/BEA/Census, CEA, CFPB,
   FTC, SEC, FRS, EPA).
4. **By grade and pay plan.** GS-12/13/14/15 vs SES/ES vs AD and other systems; whether the
   surviving workforce is more or less senior (grade distribution shift, share at GS-14+).
5. **By appointment type.** Permanent vs term/temporary vs other; probationary-adjacent
   exposure (term + low length-of-service).
6. **By tenure, age, education, location, supervisory status.** Short tables for each;
   flag where suppression bites.
7. **Flows.** Pull the FedScope **Accessions** and **Separations** cubes for series 0110
   (available via the same classic-datasets page) to measure hires and departures directly
   over the window, rather than inferring them from the net change. Report gross in, gross
   out, and separation reason mix where available.

### Phase 3 — context and robustness

- Re-run headline headcount/pay with the `0110 + 0119` definition; report both.
- Reconcile the economist definition and universe against Foster et al. (2020, 2023) in
  `papers/` and note any differences.
- Restate all seven limitations in the memo; add a "refresh checklist" for when the final
  March 2025 and the September 2025 quarterly snapshots are published.

### Phase 4 — outputs

**Tables** (`output/tables/`)
- `economist_headcount_2024_2025.csv`
- `economist_pay_change_decomp.csv`
- `economist_pay_distribution_2024_2025.csv`
- `economist_by_agency_change.csv`
- `economist_by_grade_change.csv`
- `economist_by_appointment_change.csv`
- `economist_flows_2025.csv`

**Figures** (`output/figures/`)
- `headcount_trend_with_2025.pdf` — long series + FedScope point, source break marked
- `pay_distribution_2024_vs_2025.pdf`
- `agency_headcount_waterfall.pdf`
- `grade_mix_2024_vs_2025.pdf`

**Narrative**
- `docs/2025_update.md` — findings memo (headline, method, all caveats).
- New section in `slides/slides.tex` after "Comparison to Prior Work".

### Phase 5 — integration

- `main.py` gains a `--fedscope` path that runs fetch → clean → analyze_2025 without
  touching the FedsDataCenter/gender pipeline.
- `README.md`: document the source switch, the 2025 gender-data removal, and the
  FedScope universe caveat. Add `data/raw/fedscope/` and `fedscope_economists_*` to the
  directory map.
- `requirements.txt`: no new hard dependencies expected (pandas + requests suffice;
  `pyarrow` only if the FWD parquet route is later added).

---

## Deferred / optional

- **FWD monthly data (data.opm.gov).** Would enable a true Sept 2024 → Sept 2025 (or later)
  comparison and a monthly trajectory through the 2025 reshaping. Currently blocked from
  this environment; revisit if run from a different network or once the block clears.
- **ACS / CPS federal-economist gender split.** A survey-based, different-universe proxy if
  a gender dimension for 2025 becomes a priority. Not in current scope.
