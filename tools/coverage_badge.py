"""Writes a coverage badge as an SVG, in the flat style of shields.io.

Reads the total from the JSON report of coverage.py (``pytest --cov
--cov-report=json``).  The tests workflow runs it and pushes the badge to the
``badges`` branch, which the README shows.

Run with:  uv run python tools/coverage_badge.py coverage.json coverage.svg
"""

import json
import sys

TEMPLATE = """\
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20" role="img" aria-label="coverage: {value}">
  <title>coverage: {value}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r"><rect width="{width}" height="20" rx="3" fill="#fff"/></clipPath>
  <g clip-path="url(#r)">
    <rect width="61" height="20" fill="#555"/>
    <rect x="61" width="{value_width}" height="20" fill="{color}"/>
    <rect width="{width}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="30.5" y="15" fill="#010101" fill-opacity=".3">coverage</text>
    <text x="30.5" y="14">coverage</text>
    <text x="{value_x}" y="15" fill="#010101" fill-opacity=".3">{value}</text>
    <text x="{value_x}" y="14">{value}</text>
  </g>
</svg>
"""


def color(percent: float) -> str:
    """The shields.io colors, from red below 60% to bright green from 95%"""
    for threshold, name in ((95, "#4c1"), (90, "#97ca00"), (80, "#a4a61d"),
                            (70, "#dfb317"), (60, "#fe7d37")):
        if percent >= threshold:
            return name
    return "#e05d44"


def badge(percent: float) -> str:
    value = f"{percent:.0f}%"
    value_width = 7 * len(value) + 10
    return TEMPLATE.format(
        value=value,
        color=color(percent),
        value_width=value_width,
        value_x=61 + value_width / 2,
        width=61 + value_width,
    )


def main() -> None:
    report, output = sys.argv[1], sys.argv[2]
    with open(report) as f:
        percent = json.load(f)["totals"]["percent_covered"]
    with open(output, "w") as f:
        f.write(badge(percent))
    print(f"coverage {percent:.1f}% -> {output}")


if __name__ == "__main__":
    main()
