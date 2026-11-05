# TPCH Query Analysis

`generate.py` combines TPCH queries, notes, benchmark CSVs, optional execution logs, and runtime charts from Eiger/GaMax to generate query analysis reports. The CSVs provide the steps, timings, and algorithm implementations; logs add IR and physical-plan details when available.

For joins, the table and execution graph show left and right input row counts (for example, `100⋈300`, abbreviated with `K`, `M`, or `B` for larger counts) instead of a misleading selectivity. Other selectivity values remain output rows divided by the input rows.

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
- `Runtime breakdown comparison.md` — a single table of runtime breakdown charts for all queries and chart sources.

Run `python generate.py` to generate reports for all standard chart sources in `charts/`, generate the combined runtime breakdown table, and refresh chart crops. Standard chart filenames (`<device> SF<number> breakdown.<image>`) create reports. Charts ending in `breakdown comparison.<image>` are cropped for comparison but do not create their own reports.