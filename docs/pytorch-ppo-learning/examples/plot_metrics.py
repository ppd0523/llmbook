"""PPO 학습 CSV를 외부 plotting 패키지 없이 SVG로 그린다."""

from __future__ import annotations

import argparse
import csv
import html
import math
from pathlib import Path


PANELS = (
    ("return20", "최근 20 episode return"),
    ("eval_mean", "분리 평가 return"),
    ("entropy", "정책 entropy"),
    ("approx_kl", "Approximate KL"),
    ("clip_fraction", "Clip fraction"),
    ("explained_variance", "Explained variance"),
)
COLORS = ("#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c")


def read_run(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        required = {"steps", *(key for key, _ in PANELS)}
        missing = required.difference(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path}: 필요한 열이 없습니다: {sorted(missing)}")
        rows = []
        for raw in reader:
            row = {key: float(raw[key]) for key in required}
            if math.isfinite(row["steps"]):
                rows.append(row)
    if not rows:
        raise ValueError(f"{path}: 그릴 수 있는 행이 없습니다.")
    return rows


def finite_range(values: list[float]) -> tuple[float, float]:
    finite = [value for value in values if math.isfinite(value)]
    if not finite:
        return 0.0, 1.0
    low, high = min(finite), max(finite)
    if low == high:
        padding = max(abs(low) * 0.1, 1e-3)
        return low - padding, high + padding
    padding = (high - low) * 0.08
    return low - padding, high + padding


def polyline_points(
    rows: list[dict[str, float]],
    key: str,
    left: float,
    top: float,
    width: float,
    height: float,
    x_max: float,
    y_min: float,
    y_max: float,
) -> str:
    points = []
    for row in rows:
        value = row[key]
        if not math.isfinite(value):
            continue
        x = left + width * row["steps"] / max(x_max, 1.0)
        y = top + height * (y_max - value) / max(y_max - y_min, 1e-12)
        points.append(f"{x:.1f},{y:.1f}")
    return " ".join(points)


def render_svg(runs: list[tuple[Path, list[dict[str, float]]]]) -> str:
    canvas_width, canvas_height = 1100, 1050
    panel_width, panel_height = 450, 230
    x_positions, y_positions = (85, 625), (100, 405, 710)
    x_max = max(row["steps"] for _, rows in runs for row in rows)
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_width}" height="{canvas_height}" viewBox="0 0 {canvas_width} {canvas_height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="550" y="38" text-anchor="middle" font-family="sans-serif" font-size="24" font-weight="700">PPO 학습 지표</text>',
    ]

    for panel_index, (key, title) in enumerate(PANELS):
        left = x_positions[panel_index % 2]
        top = y_positions[panel_index // 2]
        values = [row[key] for _, rows in runs for row in rows]
        y_min, y_max = finite_range(values)
        elements.extend(
            [
                f'<rect x="{left}" y="{top}" width="{panel_width}" height="{panel_height}" fill="#f8fafc" stroke="#cbd5e1"/>',
                f'<text x="{left + panel_width / 2}" y="{top - 14}" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="600">{html.escape(title)}</text>',
                f'<text x="{left - 8}" y="{top + 5}" text-anchor="end" font-family="sans-serif" font-size="12">{y_max:.3g}</text>',
                f'<text x="{left - 8}" y="{top + panel_height}" text-anchor="end" font-family="sans-serif" font-size="12">{y_min:.3g}</text>',
                f'<text x="{left}" y="{top + panel_height + 20}" font-family="sans-serif" font-size="12">0</text>',
                f'<text x="{left + panel_width}" y="{top + panel_height + 20}" text-anchor="end" font-family="sans-serif" font-size="12">{x_max:.0f} steps</text>',
            ]
        )
        for run_index, (_, rows) in enumerate(runs):
            points = polyline_points(
                rows, key, left, top, panel_width, panel_height, x_max, y_min, y_max
            )
            if points:
                elements.append(
                    f'<polyline points="{points}" fill="none" stroke="{COLORS[run_index % len(COLORS)]}" stroke-width="2"/>'
                )

    legend_y = 1015
    for run_index, (path, _) in enumerate(runs):
        legend_x = 85 + run_index * 200
        label = html.escape(path.stem)
        color = COLORS[run_index % len(COLORS)]
        elements.append(
            f'<line x1="{legend_x}" y1="{legend_y}" x2="{legend_x + 24}" y2="{legend_y}" stroke="{color}" stroke-width="3"/>'
        )
        elements.append(
            f'<text x="{legend_x + 32}" y="{legend_y + 5}" font-family="sans-serif" font-size="13">{label}</text>'
        )
    elements.append("</svg>")
    return "\n".join(elements)


def main() -> None:
    parser = argparse.ArgumentParser(description="PPO metrics CSV를 SVG로 그립니다.")
    parser.add_argument("csv_files", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, default=Path("ppo_metrics.svg"))
    args = parser.parse_args()

    runs = [(path, read_run(path)) for path in args.csv_files]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_svg(runs), encoding="utf-8")
    print(f"saved: {args.output.resolve()}")


if __name__ == "__main__":
    main()
