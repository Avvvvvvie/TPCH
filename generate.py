from __future__ import annotations

import csv
import html
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

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
PLAN_LIST_ARGUMENT_RE = re.compile(r"\b([A-Za-z]+)=\[([^\]]*)\]")
PLAN_COLUMN_REFERENCE_RE = re.compile(r"#(\d+)")
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
    r"(?P<device>.+) SF(?P<scale_factor>\d+) breakdown"
    r"(?P<comparison> comparison)?\.(?:jpe?g|png)$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ChartSource:
    device: str
    scale_factor: int
    path: Path
    comparison: bool

    def query_image_path(self, root: Path, query_number: int) -> Path:
        suffix = "_comparison" if self.comparison else ""
        return (
            root
            / "assets"
            / "runtime-breakdowns"
            / f"{self.device}_SF{self.scale_factor}_Q{query_number}{suffix}.jpg"
        )


def discover_chart_sources(root: Path) -> list[ChartSource]:
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
            ChartSource(
                device=match.group("device"),
                scale_factor=int(match.group("scale_factor")),
                path=chart_path,
                comparison=bool(match.group("comparison")),
            )
        )
    if not chart_sources:
        raise FileNotFoundError(
            f"No '<device> SF<number> breakdown[ comparison]' chart sources "
            f"found in {charts_dir}"
        )
    return sorted(
        chart_sources,
        key=lambda source: (
            source.scale_factor,
            source.device.casefold(),
            source.comparison,
        ),
    )


def generate_runtime_breakdown_assets(
    root: Path, source: ChartSource
) -> None:
    asset_dir = root / "assets" / "runtime-breakdowns"
    asset_dir.mkdir(parents=True, exist_ok=True)
    suffix = "_comparison" if source.comparison else ""

    with Image.open(source.path) as source_image:
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
                asset_dir
                / f"{source.device}_SF{source.scale_factor}_Q{query_number}{suffix}.jpg",
                quality=95,
            )

        if source.comparison:
            return

        legend_band_top = round(height * 0.89)
        legend_band = image.crop((0, legend_band_top, width, height))
        difference = ImageChops.difference(
            legend_band, Image.new("RGB", legend_band.size, "white")
        ).convert("L")
        bbox = difference.point(lambda value: 255 if value > 30 else 0).getbbox()
        if bbox is None:
            raise ValueError(f"No operator legend found in {source.path}")

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
            asset_dir / f"{source.device}_SF{source.scale_factor}_legend.jpg",
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
                "arguments": arguments,
            }
        )
    return plan


def parse_plan_list_arguments(arguments: str) -> dict[str, list[str]]:
    return {
        name: [value.strip() for value in values.split(",") if value.strip()]
        for name, values in PLAN_LIST_ARGUMENT_RE.findall(arguments)
    }


def resolve_column_index(index: str, columns: list[str]) -> str:
    if index.isdigit() and int(index) < len(columns):
        return columns[int(index)]
    return f"input column {index}"


def resolve_column_references(expression: str, columns: list[str]) -> str:
    def replace_reference(match: re.Match[str]) -> str:
        return resolve_column_index(match.group(1), columns)

    return PLAN_COLUMN_REFERENCE_RE.sub(replace_reference, expression)


def remove_column_prefix(column: str) -> str:
    return re.sub(r"^[A-Za-z]{1,2}_", "", column)


def split_top_level_arguments(value: str) -> list[str]:
    arguments = []
    start = 0
    depth = 0
    quote_character: str | None = None

    for index, character in enumerate(value):
        if quote_character is not None:
            if character == quote_character:
                quote_character = None
        elif character in {"'", '"'}:
            quote_character = character
        elif character in "([":
            depth += 1
        elif character in ")]":
            depth -= 1
        elif character == "," and depth == 0:
            arguments.append(value[start:index].strip())
            start = index + 1

    arguments.append(value[start:].strip())
    return arguments


def parse_ir_project_outputs(ir_text: str) -> list[list[tuple[str, str]]]:
    projects = []
    for line in ir_text.splitlines():
        match = re.match(r"^\s*Project\((.*)\)\s*$", line)
        if match is None:
            continue
        outputs = []
        for expression in split_top_level_arguments(match.group(1)):
            alias, separator, value = expression.partition("=")
            if separator:
                outputs.append((alias.strip(), value.strip()))
            else:
                outputs.append((expression, expression))
        projects.append(outputs)
    return projects


def split_top_level_sections(value: str, delimiter: str) -> list[str]:
    sections = []
    start = 0
    depth = 0
    quote_character: str | None = None

    for index, character in enumerate(value):
        if quote_character is not None:
            if character == quote_character:
                quote_character = None
        elif character in {"'", '"'}:
            quote_character = character
        elif character in "([{":
            depth += 1
        elif character in ")]}":
            depth -= 1
        elif character == delimiter and depth == 0:
            sections.append(value[start:index].strip())
            start = index + 1

    sections.append(value[start:].strip())
    return sections


def simplify_ir_for_display(ir_text: str) -> str:
    simplified_lines = []
    project_pattern = re.compile(r"^(\s*Project\()(.*)(\)\s*)$")
    aggregate_pattern = re.compile(r"^(\s*Aggregate\()(.*)(\)\s*)$")
    for line in ir_text.splitlines():
        aggregate_match = aggregate_pattern.match(line)
        if aggregate_match is not None:
            keys: list[str] = []
            aggregates: list[str] = []
            recognized = False
            for section in split_top_level_sections(aggregate_match.group(2), ";"):
                key_match = re.fullmatch(r"keys=\[(.*)\]", section)
                aggregate_match_inner = re.fullmatch(r"aggs=\[(.*)\]", section)
                if key_match is not None:
                    recognized = True
                    keys = split_top_level_arguments(key_match.group(1))
                elif aggregate_match_inner is not None:
                    recognized = True
                    aggregates = [
                        re.sub(r"\s+AS\s+[\w#]+$", "", expression)
                        for expression in split_top_level_arguments(
                            aggregate_match_inner.group(1)
                        )
                    ]
            if not recognized:
                simplified_lines.append(line)
                continue
            details = ", ".join(keys)
            aggregate_details = ", ".join(aggregates)
            if details and aggregate_details:
                details += "; "
            details += aggregate_details
            simplified_lines.append(
                f"{aggregate_match.group(1)}{details}{aggregate_match.group(3)}"
            )
            continue

        match = project_pattern.match(line)
        if match is None:
            simplified_lines.append(line)
            continue

        expressions = []
        for expression in split_top_level_arguments(match.group(2)):
            alias, separator, value = expression.partition("=")
            if separator and alias.strip() == value.strip():
                expressions.append(alias.strip())
            else:
                expressions.append(expression)
        simplified_lines.append(
            f"{match.group(1)}{', '.join(expressions)}{match.group(3)}"
        )
    return "\n".join(simplified_lines)


def match_project_outputs(
    project_outputs: list[list[tuple[str, str]]],
    input_columns: list[str],
    input_origins: list[set[str]],
    used_projects: set[int],
    expected_count: int,
) -> tuple[int, list[str], list[set[str]]] | None:
    candidates = [
        (index, outputs)
        for index, outputs in enumerate(reversed(project_outputs))
        if index not in used_projects and len(outputs) == expected_count
    ]
    if not candidates:
        return None

    available_names = set(input_columns)
    for origins in input_origins:
        available_names.update(origins)

    def expression_origins(expression: str) -> set[str]:
        identifiers = set(re.findall(r"\b[A-Za-z_]\w*\b", expression))
        return identifiers & available_names

    def score(outputs: list[tuple[str, str]]) -> int:
        matches = 0
        for _, expression in outputs:
            matches += len(expression_origins(expression))
        return matches

    project_index, outputs = max(
        candidates,
        key=lambda candidate: score(candidate[1]),
    )
    if score(outputs) == 0 and input_columns and len(candidates) > 1:
        return None
    return (
        project_index,
        [alias for alias, _ in outputs],
        [expression_origins(expression) for _, expression in outputs],
    )


def get_plan_column_details(
    plan: list[dict[str, object]],
    steps: list[dict[str, int | str]],
    ir_text: str,
    omit_unresolved_count_all: bool = False,
) -> dict[int, str]:
    step_by_id = {int(step["id"]): step for step in steps}
    project_outputs = parse_ir_project_outputs(ir_text)
    physical_count_all_count = sum(
        1
        for item in plan
        if item["operation"] in {"GroupBy", "ScalarAgg"}
        for expression in parse_plan_list_arguments(str(item["arguments"])).get(
            "aggs", []
        )
        if re.fullmatch(r"\?\s*\(\s*#-1\s*\)", expression)
    )
    ir_count_all_count = len(
        re.findall(r"\bcount_all\s*\(\s*\*\s*\)", ir_text)
    )
    count_all_is_confirmed = (
        physical_count_all_count > 0
        and physical_count_all_count == ir_count_all_count
    )
    used_projects: set[int] = set()
    output_columns: dict[int, list[str]] = {}
    output_origins: dict[int, list[set[str]]] = {}
    details_by_id: dict[int, str] = {}

    for item in plan:
        step_id = int(item["id"])
        operation = str(item["operation"])
        arguments = str(item["arguments"])
        inputs = [int(input_id) for input_id in item["inputs"]]
        list_arguments = parse_plan_list_arguments(arguments)
        input_columns = [output_columns[input_id] for input_id in inputs]
        input_origins = [output_origins[input_id] for input_id in inputs]
        details: list[str] = []

        if operation == "SourceTable":
            columns = list_arguments.get("cols", [])
            output_columns[step_id] = columns
            output_origins[step_id] = [{column} for column in columns]
            if columns:
                details.append(", ".join(columns))
        elif operation == "Filter":
            source_columns = input_columns[0] if input_columns else []
            source_origins = input_origins[0] if input_origins else []
            selected = list_arguments.get("out")
            output_columns[step_id] = (
                [resolve_column_index(index, source_columns) for index in selected]
                if selected is not None
                else source_columns.copy()
            )
            output_origins[step_id] = (
                [
                    source_origins[int(index)]
                    if index.isdigit() and int(index) < len(source_origins)
                    else set()
                    for index in selected
                ]
                if selected is not None
                else [origins.copy() for origins in source_origins]
            )
        elif operation == "Reorder":
            source_columns = input_columns[0] if input_columns else []
            source_origins = input_origins[0] if input_origins else []
            ordinals = list_arguments.get("ordinals", [])
            output_columns[step_id] = [
                resolve_column_index(index, source_columns) for index in ordinals
            ]
            output_origins[step_id] = [
                source_origins[int(index)].copy()
                if index.isdigit() and int(index) < len(source_origins)
                else set()
                for index in ordinals
            ]
        elif operation in {"EqJoin", "SemiJoin", "AntiJoin", "CrossJoin"}:
            left_columns = input_columns[0] if input_columns else []
            right_columns = input_columns[1] if len(input_columns) > 1 else []
            left_origins = input_origins[0] if input_origins else []
            right_origins = input_origins[1] if len(input_origins) > 1 else []
            left_keys = list_arguments.get("lkeys", [])
            right_keys = list_arguments.get("rkeys", [])
            resolved_left_keys = [
                resolve_column_index(index, left_columns) for index in left_keys
            ]
            resolved_right_keys = [
                resolve_column_index(index, right_columns) for index in right_keys
            ]
            if resolved_left_keys or resolved_right_keys:
                normalized_left_keys = [
                    remove_column_prefix(key)
                    for key in resolved_left_keys
                ]
                normalized_right_keys = [
                    remove_column_prefix(key)
                    for key in resolved_right_keys
                ]
                if operation == "EqJoin" and (
                    normalized_left_keys == normalized_right_keys
                ):
                    details.append(", ".join(normalized_left_keys))
                else:
                    details.append(
                        "; ".join(
                            part
                            for part in (
                                ", ".join(resolved_left_keys),
                                ", ".join(resolved_right_keys),
                            )
                            if part
                        )
                    )
            if operation in {"SemiJoin", "AntiJoin"}:
                output_columns[step_id] = left_columns.copy()
                output_origins[step_id] = [
                    origins.copy() for origins in left_origins
                ]
            elif operation == "CrossJoin":
                output_columns[step_id] = left_columns + right_columns
                output_origins[step_id] = [
                    origins.copy() for origins in left_origins + right_origins
                ]
            else:
                left_key_indices = {
                    int(index) for index in left_keys if index.isdigit()
                }
                removed_right_keys = {
                    int(index) for index in right_keys if index.isdigit()
                }
                output_columns[step_id] = (
                    [
                        resolve_column_index(index, left_columns)
                        for index in left_keys
                    ]
                    + [
                        column
                        for index, column in enumerate(left_columns)
                        if index not in left_key_indices
                    ]
                    + [
                        column
                        for index, column in enumerate(right_columns)
                        if index not in removed_right_keys
                    ]
                )
                output_origins[step_id] = (
                    [
                        left_origins[int(left_index)].union(
                            right_origins[int(right_index)]
                        )
                        for left_index, right_index in zip(left_keys, right_keys)
                        if left_index.isdigit()
                        and int(left_index) < len(left_origins)
                        and right_index.isdigit()
                        and int(right_index) < len(right_origins)
                    ]
                    + [
                        origins.copy()
                        for index, origins in enumerate(left_origins)
                        if index not in left_key_indices
                    ]
                    + [
                        origins.copy()
                        for index, origins in enumerate(right_origins)
                        if index not in removed_right_keys
                    ]
                )
        elif operation == "Concat":
            output_columns[step_id] = [
                column for columns in input_columns for column in columns
            ]
            output_origins[step_id] = [
                origins.copy()
                for columns in input_origins
                for origins in columns
            ]
        elif operation == "Project":
            item_count = re.search(r"#items=(\d+)", arguments)
            count = int(item_count.group(1)) if item_count else int(step_by_id[step_id]["cols"])
            matched_project = match_project_outputs(
                project_outputs,
                input_columns[0] if input_columns else [],
                input_origins[0] if input_origins else [],
                used_projects,
                count,
            )
            if matched_project is not None:
                project_index, columns, origins = matched_project
                used_projects.add(project_index)
                output_columns[step_id] = columns
                output_origins[step_id] = origins
                details.append(", ".join(columns))
            else:
                output_columns[step_id] = [
                    f"project output {index}" for index in range(count)
                ]
                output_origins[step_id] = [set() for _ in range(count)]
            if item_count and matched_project is None:
                details.append("names unavailable")
        elif operation in {"GroupBy", "ScalarAgg"}:
            source_columns = input_columns[0] if input_columns else []
            source_origins = input_origins[0] if input_origins else []
            n_keys_match = re.search(r"\bn_keys=(\d+)", arguments)
            key_count = int(n_keys_match.group(1)) if n_keys_match else 0
            key_columns = source_columns[:key_count]
            aggregate_expressions = list_arguments.get("aggs", [])
            aggregate_columns = source_columns[key_count:]
            resolved_aggregates = []
            aggregate_origins = []
            for expression in aggregate_expressions:
                is_unresolved_count_all = bool(
                    re.fullmatch(r"\?\s*\(\s*#-1\s*\)", expression)
                )
                references = {
                    int(index)
                    for index in PLAN_COLUMN_REFERENCE_RE.findall(expression)
                    if int(index) < len(aggregate_columns)
                }
                resolved_aggregates.append(
                    "count_all(*)"
                    if is_unresolved_count_all and count_all_is_confirmed
                    else PLAN_COLUMN_REFERENCE_RE.sub(
                        lambda match: (
                            aggregate_columns[int(match.group(1))]
                            if int(match.group(1)) < len(aggregate_columns)
                            else match.group(0)
                        ),
                        expression,
                    )
                )
                aggregate_origins.append(
                    set().union(
                        *(
                            source_origins[key_count + index]
                            for index in references
                        )
                    )
                    if references
                    else set()
                )
            output_columns[step_id] = key_columns + [
                expression for expression in resolved_aggregates
            ]
            output_origins[step_id] = [
                origins.copy() for origins in source_origins[:key_count]
            ] + aggregate_origins
            if key_count:
                details.append(", ".join(key_columns))
            display_aggregates = [
                aggregate
                for aggregate in resolved_aggregates
                if not (
                    omit_unresolved_count_all
                    and not count_all_is_confirmed
                    and re.fullmatch(r"\?\s*\(\s*#-1\s*\)", aggregate)
                )
            ]
            if display_aggregates:
                details.append(", ".join(display_aggregates))
        else:
            output_columns[step_id] = (
                input_columns[0].copy() if input_columns else []
            )
            output_origins[step_id] = (
                [origins.copy() for origins in input_origins[0]]
                if input_origins
                else []
            )
            for name, values in list_arguments.items():
                if name == "keys":
                    columns = input_columns[0] if input_columns else []
                    resolved = [
                        resolve_column_references(value, columns) for value in values
                    ]
                else:
                    resolved = values
                if operation != "TopK":
                    details.append(", ".join(resolved))

        expected_columns = int(step_by_id[step_id]["cols"])
        if len(output_columns[step_id]) != expected_columns:
            output_columns[step_id] = [
                f"output column {index}" for index in range(expected_columns)
            ]
            output_origins[step_id] = [set() for _ in range(expected_columns)]
        details_by_id[step_id] = "; ".join(details)

    return details_by_id


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


def format_row_count(row_count: int) -> str:
    units = ((1_000, "K"), (1_000_000, "M"), (1_000_000_000, "B"))
    for index in range(len(units) - 1, -1, -1):
        threshold, suffix = units[index]
        if row_count >= threshold:
            scaled = row_count / threshold
            if scaled >= 999.95 and index < len(units) - 1:
                threshold, suffix = units[index + 1]
                scaled = row_count / threshold
            return f"{scaled:.1f}".rstrip("0").rstrip(".") + suffix
    return str(row_count)


def get_step_annotation(
    step: dict[str, int | str],
    plan_item: dict[str, object],
    step_by_id: dict[int, dict[str, int | str]],
) -> str:
    operation = str(step["operation"])
    inputs = plan_item["inputs"]
    step_rows = int(step["rows"])

    if "Join" in operation or operation == "CrossJoin":
        if len(inputs) >= 2:
            left_rows = int(step_by_id[int(inputs[0])]["rows"])
            right_rows = int(step_by_id[int(inputs[1])]["rows"])
            return f"{format_row_count(left_rows)}⋈{format_row_count(right_rows)}"
    elif operation in {"Filter", "GroupBy", "TopK"} and inputs:
        previous_rows = int(step_by_id[int(inputs[0])]["rows"])
        if previous_rows:
            return format_selectivity(step_rows / previous_rows)
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


def get_baseline_benchmark_rows(
    query_number: int,
    summary: dict[str, str],
    benchmark_rows: list[dict[str, str]],
) -> tuple[tuple[str, ...], dict[int, dict[str, str]]]:
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
    return baseline_configuration, baseline_rows


def get_step_benchmark_data(
    query_number: int,
    steps: list[dict[str, int | str]],
    summary: dict[str, str],
    benchmark_rows: list[dict[str, str]],
) -> dict[int, tuple[str, str, str, str]]:
    """Match baseline by total runtime and apply summary overrides per best step."""
    baseline_configuration, baseline_rows = get_baseline_benchmark_rows(
        query_number, summary, benchmark_rows
    )

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


def make_csv_step_table(
    query_number: int,
    summary: dict[str, str],
    benchmark_rows: list[dict[str, str]],
) -> str:
    baseline_rows = get_baseline_benchmark_rows(
        query_number, summary, benchmark_rows
    )[1]
    steps = [
        {"id": step_id, "operation": row["step_kind"]}
        for step_id, row in sorted(baseline_rows.items())
    ]
    benchmark_data = get_step_benchmark_data(
        query_number, steps, summary, benchmark_rows
    )
    has_best_time = any(
        values[0] != values[1] for values in benchmark_data.values()
    )
    has_best_implementation = any(
        values[2] != values[3] for values in benchmark_data.values()
    )

    columns = ["Step", "Step kind", "Baseline (ms)"]
    if has_best_time:
        columns.append("Best (ms)")
    columns.append("Baseline implementation")
    if has_best_implementation:
        columns.append("Best implementation")
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    steps_by_id = {int(step["id"]): step for step in steps}
    for step_id in range(max(steps_by_id) + 1):
        step = steps_by_id.get(step_id)
        if step is None:
            values = [str(step_id), "SourceTable"]
            values.extend("" for _ in columns[2:])
            lines.append("| " + " | ".join(values) + " |")
            continue

        operation = str(step["operation"])
        baseline_time, best_time, baseline_implementation, best_implementation = (
            benchmark_data[step_id]
        )
        values = [
            str(step_id),
            operation,
            format_runtime(baseline_time) if baseline_time else "",
        ]
        if has_best_time:
            values.append(format_runtime(best_time) if best_time else "")
        values.append(baseline_implementation)
        if has_best_implementation:
            values.append(best_implementation)
        lines.append("| " + " | ".join(values) + " |")

    baseline_total = sum(
        float(values[0]) for values in benchmark_data.values() if values[0]
    )
    best_total = sum(
        float(values[1]) for values in benchmark_data.values() if values[1]
    )
    total_values = ["", "Total", format_runtime(str(baseline_total))]
    if has_best_time:
        total_values.append(format_runtime(str(best_total)))
    total_values.append("")
    if has_best_implementation:
        total_values.append("")
    lines.append("| " + " | ".join(total_values) + " |")
    return "\n".join(lines)


def make_step_table(
    log_text: str,
    query_number: int,
    summary: dict[str, str],
    benchmark_rows: list[dict[str, str]],
) -> str:
    steps, plan = get_execution_data(log_text)
    plan_by_id = {int(item["id"]): item for item in plan}
    step_by_id = {int(step["id"]): step for step in steps}
    post_rules_ir = read_section(
        log_text, "-- IR (post-rules) --", "-- ExecPlan --"
    )
    column_details_by_id = get_plan_column_details(plan, steps, post_rules_ir)
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

        annotation = get_step_annotation(step, plan_item, step_by_id)
        key_details = column_details_by_id[step_id]
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
                annotation,
                key_details,
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
        "Selectivity / Join inputs",
        "Baseline (ms)",
    ]
    if has_best_time:
        columns.append("Best (ms)")
    columns.append("Baseline implementation")
    if has_best_implementation:
        columns.append("Best implementation")
    columns.append("Physical plan keys / columns")

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
                annotation,
                baseline_time,
            ]
            + ([best_time] if has_best_time else [])
            + [baseline_implementation]
            + ([best_implementation] if has_best_implementation else [])
            + [key_details]
        ) + " |"
        for (
            step_id,
            operation,
            rows,
            cols,
            tables,
            annotation,
            key_details,
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
    total_values.append("")
    lines.append("| " + " | ".join(total_values) + " |")
    return "\n".join(lines)


def make_ir_graph(ir_text: str) -> str:
    ir_text = simplify_ir_for_display(ir_text)
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
    post_rules_ir = read_section(
        log_text, "-- IR (post-rules) --", "-- ExecPlan --"
    )
    column_details_by_id = get_plan_column_details(
        plan, steps, post_rules_ir, omit_unresolved_count_all=True
    )
    lines = ["```mermaid", "flowchart TD"]

    for step in steps:
        step_id = int(step["id"])
        operation = str(step["operation"])
        plan_item = plan_by_id[step_id]
        source = plan_item["source"]
        label = f"{step_id} · {operation}"
        annotation = get_step_annotation(step, plan_item, step_by_id)
        key_details = column_details_by_id[step_id]
        if annotation:
            label += f" · {annotation}"
        if isinstance(source, str):
            label += f"<br/>{source}"
        if key_details and operation != "Project":
            label += f"<br/>{key_details}"
        label += f"<br/>{int(step['rows']):,} × {int(step['cols'])}"
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


def make_runtime_breakdown_table(images: list[tuple[str, str]]) -> str:
    labels = [label.replace("|", r"\|") for label, _ in images]
    headers = "| " + " | ".join(labels) + " |"
    separator = "| " + " | ".join("---" for _ in images) + " |"
    image_cells = []
    for (label, image_path) in images:
        image_cells.append(make_runtime_breakdown_image(label, image_path))
    return "\n".join((headers, separator, "| " + " | ".join(image_cells) + " |"))


def make_runtime_breakdown_image(label: str, image_path: str) -> str:
    safe_label = label.replace("|", r"\|")
    image_reference = quote(image_path, safe="/._-")
    return f'<img src="{image_reference}" alt="{safe_label}" width="200">'


def make_runtime_breakdown_comparison_table(
    root: Path,
    output_path: Path,
    chart_sources: list[ChartSource],
    order: list[str],
) -> str:
    source_paths = {str(source.path): source for source in chart_sources}
    ordered_sources = order_runtime_breakdowns(
        [
            (f"{source.device} SF{source.scale_factor}", str(source.path))
            for source in chart_sources
        ],
        order,
    )
    columns = []
    for label, source_path in ordered_sources:
        source = source_paths[source_path]
        if any(
            source.query_image_path(root, query_number).is_file()
            for query_number in range(1, 23)
        ):
            columns.append((source, label))
    if not columns:
        return ""

    labels = [label.replace("|", r"\|") for _, label in columns]
    lines = [
        "| Query | " + " | ".join(labels) + " |",
        "| --- | " + " | ".join("---" for _ in columns) + " |",
    ]
    for query_number in range(1, 23):
        image_cells = []
        for source, label in columns:
            image_path = source.query_image_path(root, query_number)
            if image_path.is_file():
                image_reference = image_path.relative_to(output_path.parent).as_posix()
                image_cells.append(make_runtime_breakdown_image(label, image_reference))
            else:
                image_cells.append("")
        lines.append(
            f"| Q{query_number} | " + " | ".join(image_cells) + " |"
        )
    return "\n".join(lines)


def read_runtime_breakdown_order(root: Path) -> list[str]:
    order_path = root / "order.json"
    if not order_path.is_file():
        return []

    order = json.loads(order_path.read_text(encoding="utf-8-sig"))
    if not isinstance(order, list) or any(not isinstance(item, str) for item in order):
        raise ValueError(f"{order_path.name} must contain a JSON array of labels")
    if len(order) != len(set(order)):
        raise ValueError(f"{order_path.name} contains duplicate labels")
    return order


def order_runtime_breakdowns(
    images: list[tuple[str, str]], order: list[str]
) -> list[tuple[str, str]]:
    order_index = {label: index for index, label in enumerate(order)}
    ordered_images = sorted(
        enumerate(images),
        key=lambda item: (
            order_index.get(item[1][0], len(order)),
            item[0],
        ),
    )
    return [image for _, image in ordered_images]


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
        f"- This query joins {len(table_reads)} tables."
    ] if len(table_reads) >= 5 else []
    lines.extend(
        f"- {table.capitalize()} is read multiple times."
        for table, count in table_reads.items()
        if count > 1
    )
    lines.extend(notes)
    return "\n\n".join(lines)


def render_query(
    query_number: int,
    query_sql: str,
    log_text: str,
    notes: list[str] | None = None,
    runtime_breakdowns: list[tuple[str, str]] | None = None,
    benchmark_summary: dict[str, str] | None = None,
    benchmark_rows: list[dict[str, str]] | None = None,
) -> str:
    if benchmark_summary is None or benchmark_rows is None:
        raise ValueError(f"Benchmark data is required to render Q{query_number}")
    query_title, query_description, sql_body = parse_query_header(
        query_number, query_sql
    )
    active_tables = ",".join(get_active_tables(sql_body))
    diagram = SCHEMA_DIAGRAM.format(active_tables=active_tables)
    report_sections = [
        f"# Q{query_number} {query_title}",
    ]
    if query_description:
        report_sections.extend(("", query_description))
    report_sections.extend(("", "```sql", sql_body, "```", diagram))
    if log_text.strip():
        post_rules_ir = read_section(
            log_text, "-- IR (post-rules) --", "-- ExecPlan --"
        )
        post_rules_ir = simplify_ir_for_display(post_rules_ir)
        report_sections.extend(
            (
                "",
                "```sql",
                post_rules_ir,
                "```",
                "",
                make_ir_graph(post_rules_ir),
                "",
                make_step_table(
                    log_text, query_number, benchmark_summary, benchmark_rows
                ),
                "",
                make_execution_graph(log_text),
            )
        )
        note_text = make_notes(parse_plan(log_text), notes or [])
    else:
        report_sections.extend(
            (
                "",
                make_csv_step_table(
                    query_number, benchmark_summary, benchmark_rows
                ),
            )
        )
        note_text = "\n\n".join(notes or [])
    if note_text:
        report_sections.extend(("", "## Notes", "", note_text))
    if runtime_breakdowns:
        report_sections.extend(
            (
                "",
                "## Runtime breakdown comparison",
                "",
                make_runtime_breakdown_table(runtime_breakdowns),
            )
        )
    return "\n".join(report_sections)


def generate_report(
    root: Path,
    device: str,
    scale_factor: int,
    output_path: Path,
    chart_sources: list[ChartSource] | None = None,
) -> Path | None:
    if chart_sources is None:
        chart_sources = discover_chart_sources(root)
    benchmark_rows_by_query, summaries_by_query = read_benchmark_sources(
        root, device, scale_factor
    )
    runtime_breakdown_order = read_runtime_breakdown_order(root)
    query_reports = []
    for query_number in sorted(benchmark_rows_by_query):
        if not 1 <= query_number <= 22:
            continue
        log_path = root / "logs" / f"{device} Q{query_number} SF{scale_factor}.txt"
        log_text = (
            log_path.read_text(encoding="utf-8-sig")
            if log_path.is_file()
            else ""
        )

        query_path = root / "queries" / f"Q{query_number}.sql"
        query_sql = query_path.read_text(encoding="utf-8-sig")
        query_notes = read_notes(root, device, scale_factor, query_number)
        if query_number not in summaries_by_query:
            raise ValueError(f"Summary is missing Q{query_number}")
        runtime_breakdowns = []
        for chart_source in chart_sources:
            chart_path = chart_source.query_image_path(root, query_number)
            if not chart_path.is_file():
                continue
            chart_label = f"{chart_source.device} SF{chart_source.scale_factor}"
            image_reference = chart_path.relative_to(output_path.parent).as_posix()
            runtime_breakdowns.append((chart_label, image_reference))
        runtime_breakdowns = order_runtime_breakdowns(
            runtime_breakdowns, runtime_breakdown_order
        )
        query_reports.append(
            render_query(
                query_number,
                query_sql,
                log_text,
                query_notes,
                runtime_breakdowns,
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


def generate_runtime_breakdown_comparison(
    root: Path, chart_sources: list[ChartSource]
) -> Path:
    output_path = root / "Runtime breakdown comparison.md"
    table = make_runtime_breakdown_comparison_table(
        root,
        output_path,
        chart_sources,
        read_runtime_breakdown_order(root),
    )
    if not table:
        raise ValueError("No runtime breakdown query images are available")
    legend_source = next(
        (source for source in chart_sources if not source.comparison),
        None,
    )
    if legend_source is not None:
        legend_path = (
            root
            / "assets"
            / "runtime-breakdowns"
            / f"{legend_source.device}_SF{legend_source.scale_factor}_legend.jpg"
        )
        if legend_path.is_file():
            legend_reference = legend_path.relative_to(output_path.parent).as_posix()
            table += (
                "\n\n## Runtime breakdown legend\n\n"
                f"![Runtime breakdown legend|200x0]({legend_reference})"
            )
    output_path.write_text(
        "# Runtime breakdown comparison\n\n" + table + "\n",
        encoding="utf-8",
    )
    return output_path


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    chart_sources = discover_chart_sources(project_root)
    for chart_source in chart_sources:
        generate_runtime_breakdown_assets(project_root, chart_source)

    comparison_path = generate_runtime_breakdown_comparison(
        project_root, chart_sources
    )
    print(f"Generated {comparison_path}")

    for chart_source in chart_sources:
        if chart_source.comparison:
            continue
        report_path = (
            project_root
            / f"{chart_source.device} SF{chart_source.scale_factor} Query analysis.md"
        )
        generated_path = generate_report(
            project_root,
            chart_source.device,
            chart_source.scale_factor,
            report_path,
            chart_sources,
        )
        if generated_path is not None:
            print(f"Generated {generated_path}")