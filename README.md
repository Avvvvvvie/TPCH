# TPCH Query Analysis

`generate.py` combines TPCH queries, notes, benchmark CSVs, optional execution logs, and runtime charts from Eiger/GaMax to generate query analysis reports. The CSVs provide the steps, timings, and algorithm implementations; logs add IR and physical-plan details when available.


## Folders

- `queries/` SQL for Q1–Q22.
- `logs/` query execution logs for each scale factor.
- `csv/` benchmark step timings and run summaries.
- `charts/` original runtime breakdown images.
- `notes/` optional notes included in matching query reports.
- `assets/runtime-breakdowns/` generated per-query chart crops and legends.

## Reports

- `<device> <scale factor> Query analysis.md` shows details for each query.
- `Runtime breakdown comparison.md` shows all charts.
- `TPCH Schema.md` shows a schema overview.

Run `python generate.py` to generate reports for all standard chart sources in `charts/`, generate the combined runtime breakdown table, and refresh chart crops. Standard chart filenames (`<device> SF<number> breakdown.<image>`) create reports. Charts ending in `breakdown comparison.<image>` are cropped for comparison but do not create their own reports.