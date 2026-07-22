#!/usr/bin/env python3
"""
Render the contribution heatmap as an animated SVG.
Uses a diagonal reveal animation that plays once.
"""

import json
from datetime import datetime
from pathlib import Path

# GitHub-style color palette (5 levels)
PALETTE = [
    "#161b22",  # Level 0 - no contributions
    "#0e4429",  # Level 1
    "#006d32",  # Level 2
    "#26a641",  # Level 3
    "#39d353",  # Level 4
]

# Styling
BG_COLOR = "#0d1117"
TEXT_COLOR = "#8b949e"
CELL_SIZE = 11
CELL_GAP = 3
CELL_RADIUS = 2
WEEKS = 53
DAYS_PER_WEEK = 7

# Animation
REVEAL_DURATION = 1.5  # total animation time


def load_contributions() -> dict:
    """Load contribution data from JSON."""
    script_dir = Path(__file__).parent.parent
    data_path = script_dir / "data" / "contributions.json"

    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_calendar_grid(days: list) -> list[list[dict]]:
    """Organize days into a week x day grid."""
    # Create a dict for quick lookup
    day_map = {d["date"]: d for d in days}

    # Get the date range (last 53 weeks)
    if not days:
        return []

    # Sort and get the last year of data
    sorted_days = sorted(days, key=lambda x: x["date"])
    end_date = datetime.strptime(sorted_days[-1]["date"], "%Y-%m-%d")

    # Build grid: 53 weeks x 7 days
    grid = []

    # Start from the beginning of the first week
    start_date = end_date - __import__("datetime").timedelta(days=WEEKS * 7 - 1)
    # Adjust to start of week (Sunday)
    start_date = start_date - __import__("datetime").timedelta(days=start_date.weekday() + 1)

    current = start_date
    for week in range(WEEKS):
        week_data = []
        for day in range(DAYS_PER_WEEK):
            date_str = current.strftime("%Y-%m-%d")
            if date_str in day_map:
                week_data.append(day_map[date_str])
            else:
                week_data.append({"date": date_str, "count": 0, "level": 0})
            current += __import__("datetime").timedelta(days=1)
        grid.append(week_data)

    return grid


def generate_heatmap_svg(data: dict, output_path: str):
    """Generate the animated heatmap SVG."""
    days = data.get("days", [])
    stats = data.get("stats", {})

    grid = build_calendar_grid(days)

    # Calculate dimensions
    grid_width = WEEKS * (CELL_SIZE + CELL_GAP)
    grid_height = DAYS_PER_WEEK * (CELL_SIZE + CELL_GAP)

    padding = 40
    legend_height = 30
    stats_height = 25

    width = grid_width + padding * 2
    height = grid_height + padding * 2 + legend_height + stats_height

    svg_parts = [
        f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <style>
    .heatmap-text {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      font-size: 11px;
      fill: {TEXT_COLOR};
    }}
    .stats-text {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      font-size: 12px;
      fill: {TEXT_COLOR};
    }}
    @keyframes slideIn {{
      from {{
        opacity: 0;
        transform: translateY(-5px);
      }}
      to {{
        opacity: 1;
        transform: translateY(0);
      }}
    }}
  </style>

  <rect width="100%" height="100%" fill="{BG_COLOR}"/>

  <!-- Contribution grid -->
  <g transform="translate({padding}, {padding})">'''
    ]

    # Draw cells
    for week_idx, week in enumerate(grid):
        for day_idx, day in enumerate(week):
            x = week_idx * (CELL_SIZE + CELL_GAP)
            y = day_idx * (CELL_SIZE + CELL_GAP)

            level = min(day.get("level", 0), len(PALETTE) - 1)
            color = PALETTE[level]

            # Calculate animation delay based on diagonal position
            diagonal = week_idx + day_idx
            delay = diagonal * (REVEAL_DURATION / (WEEKS + DAYS_PER_WEEK))

            svg_parts.append(f'''
    <rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}"
          rx="{CELL_RADIUS}" fill="{color}"
          style="opacity: 0; animation: slideIn 0.1s ease-out {delay:.3f}s forwards;">
      <title>{day.get('date', '')}: {day.get('count', 0)} contributions</title>
    </rect>''')

    # Day labels
    day_labels = ["", "Mon", "", "Wed", "", "Fri", ""]
    for i, label in enumerate(day_labels):
        if label:
            y = i * (CELL_SIZE + CELL_GAP) + CELL_SIZE - 2
            svg_parts.append(f'''
    <text x="-25" y="{y}" class="heatmap-text">{label}</text>''')

    svg_parts.append(f'''
  </g>

  <!-- Legend -->
  <g transform="translate({width - 150}, {height - legend_height - stats_height + 5})">
    <text x="0" y="10" class="heatmap-text">Less</text>''')

    for i, color in enumerate(PALETTE):
        x = 30 + i * (CELL_SIZE + 2)
        svg_parts.append(f'''
    <rect x="{x}" y="0" width="{CELL_SIZE}" height="{CELL_SIZE}" rx="{CELL_RADIUS}" fill="{color}"/>''')

    svg_parts.append(f'''
    <text x="{30 + len(PALETTE) * (CELL_SIZE + 2) + 5}" y="10" class="heatmap-text">More</text>
  </g>

  <!-- Stats footer -->
  <text x="{padding}" y="{height - 10}" class="stats-text">
    {stats.get('total', 0):,} contributions in the last year
  </text>

</svg>''')

    svg_content = "".join(svg_parts)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"Generated heatmap: {output_path}")


def main():
    script_dir = Path(__file__).parent.parent
    output_path = script_dir / "contrib-heatmap.svg"

    data = load_contributions()
    generate_heatmap_svg(data, str(output_path))


if __name__ == "__main__":
    main()
