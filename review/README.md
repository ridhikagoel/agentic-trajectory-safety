# Systematic review artifact

This folder holds the protocol, search logs, screening decisions, coding sheets and scripts for the review reported in the paper. It sits alongside the paper's synthetic experiment.

- `PROTOCOL.md`: the research questions, sources, eligibility criteria and codebook, fixed before screening, plus a log of every change made during the review and why.
- `raw/`:
  - search query logs and raw API responses (NVD JSON, arXiv Atom)
  - one screening table per source; every record gets a decision and a reason
  - `s4_known_items.csv`, the recall check against cases from an earlier draft
- `coding/`: each coder's sheets, the blank sheets, the human spot-check sheet, and the agreement output.
- `scripts/`: search (`s1_*`, `s2_*`, `s3_*`), coding-sheet builders, `kappa.py`, and `summarize.py`. The last one computes every count reported in the paper and writes `RESULTS.md`.

## Left out on purpose (third-party copyright)

These were used during the review but are not redistributed here:

- the full text of news articles and vendor documents
- the AI Incident Database snapshot

To rebuild them:

- **AIID:** download `backup-20261012101643.tar.bz2` from https://incidentdatabase.ai/research/snapshots/ and extract `mongodump_full_snapshot/incidents.csv` into `raw/aiid_snapshot/` before running `scripts/s2_aiid_filter.py`.
- **Other sources:** each record in `coding/*.csv` lists its sources.

`raw/s2_aiid_records.csv` contains AIID incident titles and descriptions. These are © Responsible AI Collaborative, CC BY-SA 4.0.
