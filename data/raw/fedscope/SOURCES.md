# FedScope source files

Retrieved 2026-09-09 from <https://www.opm.gov/data/datasets/>.

OPM FedScope "classic" raw datasets. This is the **preliminary** March 2025
employment snapshot (posted 2025-07-01) with the September 2024 snapshot
bundled for comparison, plus the April 2024-March 2025 accessions/separations.

| dataset | OPM Files path | local zip |
| --- | --- | --- |
| employment_file_1 | `756/a1acc4f3-0c10-45e3-ac1f-0ee7f5769e1d.zip` | `_downloads/march_2025_employment_1.zip` |
| employment_file_2 | `758/18693acd-e0d7-4cb5-b15b-bd455a3a432c.zip` | `_downloads/march_2025_employment_2.zip` |
| employment_file_3 | `759/3c93cbe4-ae79-4881-8562-5892df28744d.zip` | `_downloads/march_2025_employment_3.zip` |
| employment_summary | `753/bc88ce69-1bbe-406f-9441-3c5153014616.zip` | `_downloads/march_2025_employment_summary.zip` |
| accessions | `761/6124a377-5e92-43e7-ade2-3be674580bc7.zip` | `_downloads/accessions_202404_to_202503.zip` |
| separations | `763/1e0ad2cd-40ee-4646-9daa-58b762bcddfb.zip` | `_downloads/separations_202404_to_202503.zip` |

## Caveats (carry into every output)

- **No gender / race.** Removed from FedScope as of March 2025 (EO 14151/14168/14173).
- **Preliminary.** March 2025 is subject to revision.
- **Understates the decline.** Employees on administrative leave pending
  resignation/retirement are still counted as current in March 2025.
- **Redaction.** Fully-redacted rows (mostly DoD) cannot be identified as
  economists in the record-level files, so `employment_202503_economists.csv`
  (~4,670 rows) is smaller than OPM's summary economist total (~4,888).
- **Location masking.** MD/VA/WV duty stations recoded to DC.
- **Small-cell suppression.** Summary cells <= 10 shown as `10_OR_LESS`.
- **Universe break.** Not directly comparable in levels to the FedsDataCenter
  FY2015-2024 series (EHRI month-end status vs. annual FOIA extract).

`_downloads/` is git-ignored. Re-create everything with `python src/fetch_fedscope.py`.
