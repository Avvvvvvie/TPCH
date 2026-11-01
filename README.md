# TPCH Query Analysis

`generate.py` combines TPCH queries, notes, execution logs, benchmark CSVs, and runtime charts from Eiger/GaMax to generate query analysis reports. It discovers device and scale factor combinations from chart filenames in `charts/`, then creates chart crops and reports for each combination.

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

Run `python generate.py` to generate reports for all matching chart sources in `charts/`. Pillow is required for chart cropping.
