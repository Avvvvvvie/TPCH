# TPCH Query Analysis

`generate.py` combines TPCH queries, notes, execution logs, benchmark CSVs, and runtime charts from Eiger/GaMax to generate query analysis reports.

For joins, reported selectivity is output rows divided by left-input rows; it is not a true match rate.

## Folders

- `queries/` SQL for Q1–Q22.
- `logs/` query execution logs for each scale factor.
- `csv/` benchmark step timings and run summaries.
- `charts/` original runtime breakdown images.
- `notes/` optional notes included in matching query reports.
- `assets/runtime-breakdowns/` generated per-query chart crops and legends.

## Generated reports

- `T4 SF1 Query analysis.md`
- `T4 SF10 Query analysis.md`

Run `python generate.py` to generate reports for all standard chart sources in `charts/` and refresh chart crops. Standard chart filenames (`<device> SF<number> breakdown.<image>`) create reports. Charts ending in `breakdown comparison.<image>` are cropped for comparison but do not create their own reports.