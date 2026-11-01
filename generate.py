from __future__ import annotations

import csv
import html
import math
import re
from pathlib import Path

from PIL import Image, ImageChops

TABLES = (
    "region",
    "nation",
    "supplier",
    "customer",
    "part",
    "partsupp",
    "orders",
    "lineitem",
)

SCHEMA_DIAGRAM = """```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class {active_tables} active
```"""

STEP_RE = re.compile(
    r"^\[step (\d+): ([^\]]+)\] -> (\d+) rows x (\d+) cols$", re.MULTILINE
)
PLAN_RE = re.compile(r"^v(\d+) = (\w+)\((.*)\)$", re.MULTILINE)
BENCHMARK_CONFIG_COLUMNS = (
    "filter",
    "project",
    "sort",
    "group_by",
    "distinct",
    "eq_join",
)
DEFAULT_VALUE = {
    "filter": "nofuse",
    "project": "nofuse",
    "sort": "no_skf",
    "group_by": "hash",
    "distinct": "hash",
    "eq_join": "hash_gfur",
}
STEP_KIND_CONFIG = {
    "Filter": "filter",
    "Project": "project",
    "Sort": "sort",
    "GroupBy": "group_by",
    "Distinct": "distinct",
    "EqJoin": "eq_join",
}
STEP_KIND_CONFIG_REVERSE = {
    config_column: step_kind for step_kind, config_column in STEP_KIND_CONFIG.items()
}
SUMMARY_OVERRIDE_RE = re.compile(r"Step\s+(\d+):\s*([^;]+)")
CHART_SOURCE_RE = re.compile(
    r"(?P<device>.+) SF(?P<scale_factor>\d+) breakdown\.(?:jpe?g|png)$",
    re.IGNORECASE,
)


def discover_chart_sources(root: Path) -> list[tuple[str, int, Path]]:
    charts_dir = root / "charts"
    if not charts_dir.is_dir():
        raise FileNotFoundError(f"Chart source folder does not exist: {charts_dir}")

    chart_sources = []
    for chart_path in sorted(charts_dir.iterdir()):
        if not chart_path.is_file():
            continue
        match = CHART_SOURCE_RE.fullmatch(chart_path.name)
        if match is None:
            continue
        chart_sources.append(
            (
                match.group("device"),
                int(match.group("scale_factor")),
                chart_path,
            )
        )
    if not chart_sources:
        raise FileNotFoundError(
            f"No '<device> SF<number> breakdown' chart sources found in {charts_dir}"
        )
    return chart_sources


def generate_runtime_breakdown_assets(
    root: Path, device: str, scale_factor: int, source_path: Path
) -> None:
    asset_dir = root / "assets" / "runtime-breakdowns"
    asset_dir.mkdir(parents=True, exist_ok=True)

    with Image.open(source_path) as source_image:
        image = source_image.convert("RGB")
        width, height = image.size
        first_column_width = round(width * 0.10468)
        column_boundaries = [0, first_column_width]
        column_width = (width - first_column_width) / 10
        column_boundaries.extend(
            round(first_column_width + column_width * column)
            for column in range(1, 10)
        )
        column_boundaries.append(width)

        row_boundaries = (0, round(height * 0.438), round(height * 0.887))
        for query_number in range(1, 23):
            column = (query_number - 1) % 11
            row = (query_number - 1) // 11
            crop = image.crop(
                (
                    column_boundaries[column],
                    row_boundaries[row],
                    column_boundaries[column + 1],
                    row_boundaries[row + 1],
                )
            )
            crop.save(
                asset_dir / f"{device}_SF{scale_factor}_Q{query_number}.jpg",
                quality=95,
            )

        legend_band_top = round(height * 0.89)
        legend_band = image.crop((0, legend_band_top, width, height))
        difference = ImageChops.difference(
            legend_band, Image.new("RGB", legend_band.size, "white")
        ).convert("L")
        bbox = difference.point(lambda value: 255 if value > 30 else 0).getbbox()
        if bbox is None:
            raise ValueError(f"No operator legend found in {source_path}")

        left, top, right, bottom = bbox
        padding = 8
        legend = legend_band.crop(
            (
                max(0, left - padding),
                max(0, top - padding),
                min(width, right + padding),
                min(legend_band.height, bottom + padding),
            )
        )
        legend.save(
            asset_dir / f"{device}_SF{scale_factor}_legend.jpg",
            quality=95,
        )


def read_section(log_text: str, start: str, end: str) -> str:
    start_index = log_text.find(start)
    if start_index == -1:
        raise ValueError(f"Log is missing section {start!r}")
    start_index += len(start)
    end_index = log_text.find(end, start_index)
    if end_index == -1:
        raise ValueError(f"Log is missing section marker {end!r}")
    return log_text[start_index:end_index].strip()


def get_active_tables(query_sql: str) -> list[str]:
    return [
        table.upper()
        for table in TABLES
        if re.search(rf"\b{re.escape(table)}\b", query_sql, re.IGNORECASE)
    ]


def parse_query_header(
    query_number: int, query_sql: str
) -> tuple[str, str, str]:
    lines = query_sql.lstrip("\ufeff").splitlines()
    header_comments = []
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if not line.startswith("--"):
            break
        header_comments.append(line[2:].strip())
        index += 1

    title = header_comments[0] if header_comments else f"Q{query_number}"
    description = "\n".join(
        comment for comment in header_comments[1:] if comment
    )
    sql_body = "\n".join(lines[index:]).strip()
    return title, description, sql_body


def parse_plan(log_text: str) -> list[dict[str, object]]:
    plan = []
    for match in PLAN_RE.finditer(log_text):
        variable_id, operation, arguments = match.groups()
        input_text = arguments.split(";", maxsplit=1)[0]
        inputs = [int(value) for value in re.findall(r"\bv(\d+)\b", input_text)]
        source_match = re.match(r'\s*"([^"]+)"', arguments)
        plan.append(
            {
                "id": int(variable_id),
                "operation": operation,
                "inputs": inputs,
                "source": source_match.group(1) if source_match else None,
            }
        )
    return plan


def format_selectivity(ratio: float) -> str:
    percentage = ratio * 100
    if percentage == 0:
        return "0%"
    if percentage >= 1:
        formatted = f"{percentage:.3g}"
    else:
        decimal_places = max(0, 2 - math.floor(math.log10(percentage)))
        formatted = f"{percentage:.{decimal_places}f}".rstrip("0").rstrip(".")
    return f"{formatted}%"


def get_execution_data(
    log_text: str,
) -> tuple[list[dict[str, int | str]], list[dict[str, object]]]:
    steps = [
        {
            "id": int(step_id),
            "operation": operation,
            "rows": int(rows),
            "cols": int(cols),
        }
        for step_id, operation, rows, cols in STEP_RE.findall(log_text)
    ]
    plan = parse_plan(log_text)
    if not steps:
        raise ValueError("Log does not contain any execution steps")
    if len(steps) != len(plan):
        raise ValueError(
            f"Found {len(steps)} execution steps but {len(plan)} plan operations"
        )

    plan_by_id = {int(item["id"]): item for item in plan}
    step_by_id = {step["id"]: step for step in steps}
    if set(plan_by_id) != set(step_by_id):
        raise ValueError("Execution step ids do not match execution plan ids")
    return steps, plan


def get_step_selectivity(
    step: dict[str, int | str],
    plan_item: dict[str, object],
    step_by_id: dict[int, dict[str, int | str]],
) -> str:
    operation = str(step["operation"])
    inputs = plan_item["inputs"]
    step_rows = int(step["rows"])

    if operation in {"Filter", "GroupBy", "TopK"} and inputs:
        previous_rows = int(step_by_id[int(inputs[0])]["rows"])
        if previous_rows:
            return format_selectivity(step_rows / previous_rows)
    elif ("Join" in operation or operation == "CrossJoin") and len(inputs) >= 2:
        left_rows = int(step_by_id[int(inputs[0])]["rows"])
        if left_rows:
            return format_selectivity(step_rows / left_rows)
    return ""


def read_benchmark_sources(
    root: Path, device: str, scale_factor: int
) -> tuple[dict[int, list[dict[str, str]]], dict[int, dict[str, str]]]:
    csv_dir = root / "csv"
    bench_path = csv_dir / f"{device} SF{scale_factor} bench_steps.csv"
    summary_path = csv_dir / f"{device} SF{scale_factor} summary.csv"

    with bench_path.open(encoding="utf-8-sig", newline="") as bench_file:
        bench_reader = csv.DictReader(bench_file)
        required_bench_columns = {
            "query",
            "step_index",
            "step_kind",
            "mean_ms",
            *BENCHMARK_CONFIG_COLUMNS,
        }
        missing_columns = required_bench_columns - set(bench_reader.fieldnames or ())
        if missing_columns:
            raise ValueError(
                f"{bench_path.name} is missing columns: {', '.join(sorted(missing_columns))}"
            )
        benchmark_rows: dict[int, list[dict[str, str]]] = {}
        for row in bench_reader:
            query_number = int(row["query"])
            benchmark_rows.setdefault(query_number, []).append(row)

    with summary_path.open(encoding="utf-8-sig", newline="") as summary_file:
        summary_reader = csv.DictReader(summary_file)
        required_summary_columns = {
            "query",
            "baseline-cfg",
            "best-cfg",
            *BENCHMARK_CONFIG_COLUMNS,
        }
        missing_columns = required_summary_columns - set(summary_reader.fieldnames or ())
        if missing_columns:
            raise ValueError(
                f"{summary_path.name} is missing columns: {', '.join(sorted(missing_columns))}"
            )
        summary_rows: dict[int, dict[str, str]] = {}
        for row in summary_reader:
            query_number = int(row["query"])
            if query_number in summary_rows:
                raise ValueError(
                    f"{summary_path.name} contains duplicate Q{query_number} rows"
                )
            summary_rows[query_number] = row

    return benchmark_rows, summary_rows


def get_step_benchmark_data(
    query_number: int,
    steps: list[dict[str, int | str]],
    summary: dict[str, str],
    benchmark_rows: list[dict[str, str]],
) -> dict[int, tuple[str, str, str, str]]:
    """Match baseline by total runtime and apply summary overrides per best step."""
    rows_by_config: dict[tuple[str, ...], list[dict[str, str]]] = {}
    for row in benchmark_rows:
        if int(row["query"]) != query_number:
            continue
        configuration = tuple(row[column] for column in BENCHMARK_CONFIG_COLUMNS)
        rows_by_config.setdefault(configuration, []).append(row)
    if not rows_by_config:
        raise ValueError(f"No benchmark rows found for Q{query_number}")

    try:
        baseline_runtime = float(summary["baseline-cfg"])
        float(summary["best-cfg"])
    except ValueError as error:
        raise ValueError(
            f"Q{query_number} summary contains an invalid runtime"
        ) from error

    configuration_totals = {
        configuration: sum(float(row["mean_ms"]) for row in rows)
        for configuration, rows in rows_by_config.items()
    }
    baseline_configuration = min(
        configuration_totals,
        key=lambda configuration: abs(
            configuration_totals[configuration] - baseline_runtime
        ),
    )
    baseline_rows: dict[int, dict[str, str]] = {}
    for row in rows_by_config[baseline_configuration]:
        step_index = int(row["step_index"])
        if step_index in baseline_rows:
            raise ValueError(
                f"Q{query_number} baseline benchmark has duplicate step {step_index}"
            )
        baseline_rows[step_index] = row

    step_by_id = {int(step["id"]): step for step in steps}
    best_overrides: dict[tuple[str, int], str] = {}
    for column in BENCHMARK_CONFIG_COLUMNS:
        for step_text, implementation in SUMMARY_OVERRIDE_RE.findall(
            summary[column]
        ):
            step_index = int(step_text)
            override_key = (column, step_index)
            if override_key in best_overrides:
                raise ValueError(
                    f"Q{query_number} summary repeats {column} step {step_index}"
                )
            if step_index not in step_by_id:
                raise ValueError(
                    f"Q{query_number} summary references missing step {step_index}"
                )
            if str(step_by_id[step_index]["operation"]) != STEP_KIND_CONFIG_REVERSE[column]:
                raise ValueError(
                    f"Q{query_number} summary assigns {column} to incompatible "
                    f"step {step_index} ({step_by_id[step_index]['operation']})"
                )
            best_overrides[override_key] = implementation.strip()

    benchmark_data: dict[int, tuple[str, str, str, str]] = {}
    for step in steps:
        step_index = int(step["id"])
        baseline_row = baseline_rows.get(step_index)
        step_kind = str(step["operation"])
        config_column = STEP_KIND_CONFIG.get(step_kind)
        if baseline_row is None:
            benchmark_data[step_index] = ("", "", "", "")
            continue

        if config_column is None:
            benchmark_data[step_index] = (
                baseline_row["mean_ms"],
                baseline_row["mean_ms"],
                "",
                "",
            )
            continue

        baseline_implementation = baseline_row[config_column]
        best_implementation = best_overrides.get(
            (config_column, step_index), baseline_implementation
        )
        benchmark_implementation = (
            "default" if best_implementation == "nofuse" else best_implementation
        )

        if benchmark_implementation == baseline_configuration[
            BENCHMARK_CONFIG_COLUMNS.index(config_column)
        ]:
            best_row = baseline_row
        else:
            candidates = [
                row
                for row in benchmark_rows
                if int(row["query"]) == query_number
                and int(row["step_index"]) == step_index
                and row["step_kind"] == step_kind
                and row[config_column] == benchmark_implementation
            ]
            if not candidates:
                raise ValueError(
                    f"Q{query_number} step {step_index} has no benchmark timing "
                    f"for {best_implementation}"
                )
            candidates.sort(
                key=lambda row: sum(
                    row[column] != baseline_configuration[index]
                    for index, column in enumerate(BENCHMARK_CONFIG_COLUMNS)
                    if column != config_column
                )
            )
            nearest_distance = sum(
                candidates[0][column] != baseline_configuration[index]
                for index, column in enumerate(BENCHMARK_CONFIG_COLUMNS)
                if column != config_column
            )
            tied_candidates = [
                row
                for row in candidates
                if sum(
                    row[column] != baseline_configuration[index]
                    for index, column in enumerate(BENCHMARK_CONFIG_COLUMNS)
                    if column != config_column
                )
                == nearest_distance
            ]
            if len(tied_candidates) > 1:
                raise ValueError(
                    f"Q{query_number} step {step_index} has ambiguous benchmark "
                    f"timings for {best_implementation}"
                )
            best_row = candidates[0]

        benchmark_data[step_index] = (
            baseline_row["mean_ms"],
            best_row["mean_ms"],
            DEFAULT_VALUE.get(config_column, baseline_implementation)
            if baseline_implementation == "default"
            else baseline_implementation,
            DEFAULT_VALUE.get(config_column, best_row[config_column])
            if best_row[config_column] == "default"
            else best_row[config_column],
        )

    return benchmark_data


def format_runtime(value: str) -> str:
    return f"{float(value):.6g}"


def make_step_table(
    log_text: str,
    query_number: int,
    summary: dict[str, str],
    benchmark_rows: list[dict[str, str]],
) -> str:
    steps, plan = get_execution_data(log_text)
    plan_by_id = {int(item["id"]): item for item in plan}
    step_by_id = {int(step["id"]): step for step in steps}
    benchmark_data = get_step_benchmark_data(
        query_number, steps, summary, benchmark_rows
    )

    lineage: dict[int, str] = {}
    table_rows = []
    for step in steps:
        step_id = int(step["id"])
        operation = str(step["operation"])
        plan_item = plan_by_id[step_id]
        inputs = plan_item["inputs"]
        source = plan_item["source"]

        if operation == "SourceTable":
            if not isinstance(source, str):
                raise ValueError(f"SourceTable step {step_id} has no table name")
            lineage[step_id] = source
            tables = source
        elif "Join" in operation or operation == "CrossJoin":
            if len(inputs) < 2:
                raise ValueError(f"Join step {step_id} does not have two inputs")
            left = lineage[int(inputs[0])]
            right = lineage[int(inputs[1])]
            left = f"({left})" if "⋈" in left else left
            right = f"({right})" if "⋈" in right else right
            lineage[step_id] = f"{left}⋈{right}"
            join_count = 0
            table_parts = []
            for part in lineage[step_id].split("⋈"):
                if table_parts:
                    join_count += 1
                    table_parts.append(" ⋈ " if join_count % 5 == 0 else "⋈")
                table_parts.append(part)
            tables = "".join(table_parts)
        else:
            lineage[step_id] = lineage[int(inputs[0])] if inputs else ""
            tables = "<" if operation in {"Filter", "GroupBy", "TopK"} else ""

        selectivity = get_step_selectivity(step, plan_item, step_by_id)
        baseline_time, best_time, baseline_implementation, best_implementation = (
            benchmark_data[step_id]
        )

        table_rows.append(
            (
                step_id,
                operation,
                int(step["rows"]),
                int(step["cols"]),
                tables,
                selectivity,
                format_runtime(baseline_time) if baseline_time else "",
                format_runtime(best_time) if best_time else "",
                baseline_implementation,
                best_implementation,
            )
        )

    has_best_time = any(
        values[0] != values[1] for values in benchmark_data.values()
    )
    has_best_implementation = any(
        values[2] != values[3] for values in benchmark_data.values()
    )
    columns = [
        "Step",
        "Operation",
        "Rows",
        "Cols",
        "Tables",
        "Selectivity",
        "Baseline (ms)",
    ]
    if has_best_time:
        columns.append("Best (ms)")
    columns.append("Baseline implementation")
    if has_best_implementation:
        columns.append("Best implementation")

    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    lines.extend(
        "| " + " | ".join(
            [
                str(step_id),
                operation,
                str(rows),
                str(cols),
                tables,
                selectivity,
                baseline_time,
            ]
            + ([best_time] if has_best_time else [])
            + [baseline_implementation]
            + ([best_implementation] if has_best_implementation else [])
        ) + " |"
        for (
            step_id,
            operation,
            rows,
            cols,
            tables,
            selectivity,
            baseline_time,
            best_time,
            baseline_implementation,
            best_implementation,
        ) in table_rows
    )
    baseline_total = sum(
        float(values[0]) for values in benchmark_data.values() if values[0]
    )
    best_total = sum(
        float(values[1]) for values in benchmark_data.values() if values[1]
    )
    total_values = [
        "",
        "Total",
        "",
        "",
        "",
        "",
        format_runtime(str(baseline_total)),
    ]
    if has_best_time:
        total_values.append(format_runtime(str(best_total)))
    total_values.append("")
    if has_best_implementation:
        total_values.append("")
    lines.append("| " + " | ".join(total_values) + " |")
    return "\n".join(lines)


def make_ir_graph(ir_text: str) -> str:
    nodes: list[tuple[int, str, str, int | None]] = []
    parent_stack: list[tuple[int, int]] = []
    operation_pattern = re.compile(r"^(\s*)([A-Za-z]+)(.*)$")

    for line in ir_text.splitlines():
        if not line.strip():
            continue
        match = operation_pattern.match(line)
        if match is None:
            raise ValueError(f"Unrecognized post-rules IR line: {line!r}")

        indentation, operation, arguments = match.groups()
        depth = len(indentation.expandtabs(2))
        while parent_stack and parent_stack[-1][0] >= depth:
            parent_stack.pop()
        parent_id = parent_stack[-1][1] if parent_stack else None
        node_id = len(nodes)
        nodes.append((node_id, operation, arguments.strip(), parent_id))
        parent_stack.append((depth, node_id))

    if not nodes:
        raise ValueError("Post-rules IR does not contain any operators")

    lines = ["```mermaid", "flowchart TD"]
    classes: dict[str, list[str]] = {
        "source": [],
        "filter": [],
        "join": [],
        "aggregate": [],
        "transform": [],
        "ordering": [],
    }

    for node_id, operation, arguments, parent_id in nodes:
        details = arguments
        if details.startswith("(") and details.endswith(")"):
            details = details[1:-1]
        elif details.startswith("[") and details.endswith("]"):
            details = details[1:-1]

        if operation == "Scan":
            scan_match = re.match(r"([^ ]+) \[(.*)\]", details)
            if scan_match:
                details = f"{scan_match.group(1)} · {scan_match.group(2)}"
        if len(details) > 110:
            details = f"{details[:107]}..."

        label = html.escape(details, quote=False).replace('"', "#quot;")
        label = f"{operation}<br/>{label}" if label else operation
        lines.append(f'    ir_{node_id}["{label}"]')
        if parent_id is not None:
            lines.append(f"    ir_{parent_id} --> ir_{node_id}")

        if operation == "Scan":
            category = "source"
        elif operation == "Filter":
            category = "filter"
        elif "Join" in operation:
            category = "join"
        elif operation in {"Aggregate", "Distinct"}:
            category = "aggregate"
        elif operation in {"Sort", "Limit"}:
            category = "ordering"
        else:
            category = "transform"
        classes[category].append(f"ir_{node_id}")

    lines.extend(
        (
            "    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a",
            "    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f",
            "    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95",
            "    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d",
            "    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937",
            "    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d",
        )
    )
    for category, category_nodes in classes.items():
        if category_nodes:
            lines.append(f"    class {','.join(category_nodes)} {category}")
    lines.extend(("```", ""))
    return "\n".join(lines)


def make_execution_graph(log_text: str) -> str:
    steps, plan = get_execution_data(log_text)
    step_by_id = {int(step["id"]): step for step in steps}
    plan_by_id = {int(item["id"]): item for item in plan}
    lines = ["```mermaid", "flowchart TD"]

    for step in steps:
        step_id = int(step["id"])
        operation = str(step["operation"])
        plan_item = plan_by_id[step_id]
        source = plan_item["source"]
        label = f"{step_id} · {operation}"
        selectivity = get_step_selectivity(step, plan_item, step_by_id)
        if selectivity:
            label += f" · {selectivity}"
        if isinstance(source, str):
            label += f"<br/>{source}"
        label += f"<br/>{int(step['rows']):,} rows × {int(step['cols'])} cols"
        label = label.replace('"', "#quot;")
        lines.append(f'    step_{step_id}["{label}"]')

        inputs = plan_item["inputs"]
        for input_id in inputs:
            input_id = int(input_id)
            if input_id not in step_by_id:
                raise ValueError(
                    f"Plan step {step_id} references missing input v{input_id}"
                )
            lines.append(f"    step_{input_id} --> step_{step_id}")

    lines.extend(
        (
            "    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a",
            "    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f",
            "    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95",
            "    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d",
            "    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937",
            "    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d",
        )
    )
    classes = {
        "source": [],
        "filter": [],
        "join": [],
        "aggregate": [],
        "transform": [],
        "ordering": [],
    }
    for step in steps:
        step_id = int(step["id"])
        operation = str(step["operation"])
        if operation == "SourceTable":
            category = "source"
        elif operation == "Filter":
            category = "filter"
        elif "Join" in operation or operation == "CrossJoin":
            category = "join"
        elif operation in {"GroupBy", "ScalarAgg"}:
            category = "aggregate"
        elif operation in {"Sort", "TopK", "Limit"}:
            category = "ordering"
        else:
            category = "transform"
        classes[category].append(f"step_{step_id}")

    for category, nodes in classes.items():
        if nodes:
            lines.append(f"    class {','.join(nodes)} {category}")
    lines.extend(("```", ""))
    return "\n".join(lines)


def read_notes(
    root: Path, device: str, scale_factor: int, query_number: int
) -> list[str]:
    """Load notes named with optional device, Q<number>, and SF<number> scopes."""
    notes_dir = root / "notes"
    if not notes_dir.is_dir():
        return []

    device_scope = re.sub(r"[\s._-]+", "", device).casefold()
    query_pattern = re.compile(r"(?<![A-Za-z0-9])Q(\d+)(?![A-Za-z0-9])", re.I)
    scale_factor_pattern = re.compile(
        r"(?<![A-Za-z0-9])SF(\d+)(?![A-Za-z0-9])", re.I
    )
    notes = []
    for note_path in sorted(notes_dir.iterdir()):
        if not note_path.is_file() or note_path.suffix.lower() not in {".md", ".txt"}:
            continue

        stem = note_path.stem
        query_scopes = [int(value) for value in query_pattern.findall(stem)]
        scale_factor_scopes = [
            int(value) for value in scale_factor_pattern.findall(stem)
        ]
        if query_scopes and query_number not in query_scopes:
            continue
        if scale_factor_scopes and scale_factor not in scale_factor_scopes:
            continue

        device_name = query_pattern.sub(" ", stem)
        device_name = scale_factor_pattern.sub(" ", device_name)
        device_name = re.sub(r"[\s._-]+", "", device_name).casefold()
        if device_name and device_name != device_scope:
            continue
        if not (query_scopes or scale_factor_scopes or device_name):
            continue

        note = note_path.read_text(encoding="utf-8-sig").strip()
        if note:
            notes.append(note)
    return notes


def make_notes(plan: list[dict[str, object]], notes: list[str]) -> str:
    table_reads: dict[str, int] = {}
    for item in plan:
        source = item["source"]
        if item["operation"] == "SourceTable" and isinstance(source, str):
            table_reads[source] = table_reads.get(source, 0) + 1

    lines = [
        f"- {table} is read multiple times."
        for table, count in table_reads.items()
        if count > 1
    ]
    lines.extend(notes)
    return "\n\n".join(lines)


def render_query(
    query_number: int,
    query_sql: str,
    log_text: str,
    notes: list[str] | None = None,
    runtime_breakdown: str | None = None,
    benchmark_summary: dict[str, str] | None = None,
    benchmark_rows: list[dict[str, str]] | None = None,
) -> str:
    if benchmark_summary is None or benchmark_rows is None:
        raise ValueError(f"Benchmark data is required to render Q{query_number}")
    query_title, query_description, sql_body = parse_query_header(
        query_number, query_sql
    )
    post_rules_ir = read_section(
        log_text, "-- IR (post-rules) --", "-- ExecPlan --"
    )
    active_tables = ",".join(get_active_tables(sql_body))
    diagram = SCHEMA_DIAGRAM.format(active_tables=active_tables)
    report_sections = [
        f"# Q{query_number} {query_title}",
    ]
    if query_description:
        report_sections.extend(("", query_description))
    report_sections.extend(
        (
            "",
        "```sql",
        sql_body,
        "```",
        diagram,
        "",
        "```sql",
        post_rules_ir,
        "```",
        "",
        make_ir_graph(post_rules_ir),
        "",
        make_step_table(log_text, query_number, benchmark_summary, benchmark_rows),
        "",
        make_execution_graph(log_text),
        )
    )
    note_text = make_notes(parse_plan(log_text), notes or [])
    if note_text:
        report_sections.extend(("", "## Notes", "", note_text))
    if runtime_breakdown is not None:
        report_sections.extend(
            (
                "",
                "## Runtime breakdown",
                "",
                f"![Q{query_number} runtime breakdown|200x0]({runtime_breakdown})",
            )
        )
    return "\n".join(report_sections)


def generate_report(
    root: Path, device: str, scale_factor: int, output_path: Path
) -> Path | None:
    benchmark_rows_by_query, summaries_by_query = read_benchmark_sources(
        root, device, scale_factor
    )
    query_reports = []
    for query_number in range(1, 23):
        log_path = root / "logs" / f"{device} Q{query_number} SF{scale_factor}.txt"
        log_text = log_path.read_text(encoding="utf-8-sig")
        if not log_text.strip():
            continue

        query_path = root / "queries" / f"Q{query_number}.sql"
        query_sql = query_path.read_text(encoding="utf-8-sig")
        query_notes = read_notes(root, device, scale_factor, query_number)
        if query_number not in summaries_by_query:
            raise ValueError(f"Summary is missing Q{query_number}")
        chart_path = (
            root
            / "assets"
            / "runtime-breakdowns"
            / f"{device}_SF{scale_factor}_Q{query_number}.jpg"
        )
        runtime_breakdown = (
            chart_path.relative_to(output_path.parent).as_posix()
            if chart_path.is_file()
            else None
        )
        query_reports.append(
            render_query(
                query_number,
                query_sql,
                log_text,
                query_notes,
                runtime_breakdown,
                summaries_by_query[query_number],
                benchmark_rows_by_query.get(query_number, []),
            )
        )

    if not query_reports:
        return None

    report_text = "\n\n".join(query_reports)
    legend_path = (
        root
        / "assets"
        / "runtime-breakdowns"
        / f"{device}_SF{scale_factor}_legend.jpg"
    )
    if legend_path.is_file():
        legend_reference = legend_path.relative_to(output_path.parent).as_posix()
        report_text += (
            "\n\n## Runtime breakdown legend\n\n"
            f"![Runtime breakdown legend|200x0]({legend_reference})"
        )
    output_path.write_text(report_text + "\n", encoding="utf-8")
    return output_path


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    for device, scale_factor, chart_path in discover_chart_sources(project_root):
        generate_runtime_breakdown_assets(
            project_root, device, scale_factor, chart_path
        )
        report_path = (
            project_root / f"{device} SF{scale_factor} Query analysis.md"
        )
        generated_path = generate_report(
            project_root, device, scale_factor, report_path
        )
        if generated_path is not None:
            print(f"Generated {generated_path}")