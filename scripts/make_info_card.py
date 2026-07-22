#!/usr/bin/env python3
"""
Generate macOS terminal-style neofetch info card SVG.
Based on avivashishta's design.
"""

from pathlib import Path
import requests

# User info - customize these!
USERNAME = "zerofour04"
GITHUB_USERNAME = "Zerofour04"


def fetch_github_stats() -> dict:
    """Fetch stars and followers from GitHub API."""
    try:
        # Get user info (followers)
        user_resp = requests.get(f"https://api.github.com/users/{GITHUB_USERNAME}")
        user_data = user_resp.json()
        followers = user_data.get("followers", 0)

        # Get total stars across all repos
        repos_resp = requests.get(f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100")
        repos = repos_resp.json()
        total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)

        return {"stars": total_stars, "followers": followers}
    except Exception as e:
        print(f"Warning: Could not fetch GitHub stats: {e}")
        return {"stars": 0, "followers": 0}
INFO = {
    "Now": "Fullstack Developer",
    "Loc": "Munich, Germany",
    "Focus": "Building digital experiences",
}

STACK = {
    "Frontend": "React, Vue, TypeScript, Tailwind",
    "Backend": "Node.js, PHP, Java, Python",
    "Cloud": "AWS, Docker, Vercel, Cloudflare",
    "DB": "PostgreSQL, MongoDB, Supabase",
}

HIGHLIGHTS_TEMPLATE = [
    "{stars} GitHub Stars",
    "{followers} Followers",
    "Goaßmaß-driven development",
    "Tegernsee Hell > Augustiner",
]

# Colors
GREEN = "#3fb950"
CYAN = "#22d3ee"
ORANGE = "#ffa657"
BLUE = "#58a6ff"
TEXT = "#c9d1d9"
DIM = "#7d8590"
BG_TOP = "#111722"
BG_BOTTOM = "#0d1117"
BORDER = "#30363d"
RED = "#ff5f56"
YELLOW = "#ffbd2e"
TRAFFIC_GREEN = "#27c93f"

# Layout
WIDTH = 490
PADDING = 20
TITLE_BAR = 30
LINE_HEIGHT = 20.5
LABEL_X = 112

FONT = 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace'


def escape_xml(text: str) -> str:
    """Escape special XML characters."""
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;"))


def generate_info_card(output_path: str):
    # Fetch dynamic GitHub stats
    stats = fetch_github_stats()
    print(f"Fetched: {stats['stars']} stars, {stats['followers']} followers")

    HIGHLIGHTS = [h.format(**stats) for h in HIGHLIGHTS_TEMPLATE]

    lines = []
    y = 60

    # Header: username@github
    lines.append({
        "type": "header",
        "y": y,
        "delay": 0.15,
    })
    y += 20.5

    # Info section
    for key, value in INFO.items():
        lines.append({
            "type": "info",
            "key": key,
            "value": value,
            "y": y,
            "delay": len(lines) * 0.06 + 0.15,
        })
        y += LINE_HEIGHT

    y += 10  # gap before stack

    # Stack section header
    lines.append({
        "type": "section",
        "title": "Stack",
        "y": y,
        "delay": len(lines) * 0.06 + 0.15,
    })
    y += LINE_HEIGHT

    # Stack items
    for key, value in STACK.items():
        lines.append({
            "type": "info",
            "key": key,
            "value": value,
            "y": y,
            "delay": len(lines) * 0.06 + 0.15,
        })
        y += LINE_HEIGHT

    y += 10  # gap before highlights

    # Highlights section header
    lines.append({
        "type": "section",
        "title": "Highlights",
        "y": y,
        "delay": len(lines) * 0.06 + 0.15,
    })
    y += LINE_HEIGHT

    # Highlight items
    for item in HIGHLIGHTS:
        lines.append({
            "type": "highlight",
            "text": item,
            "y": y,
            "delay": len(lines) * 0.06 + 0.15,
        })
        y += LINE_HEIGHT

    height = y + 20

    # Build SVG
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" font-family="{FONT}">
  <defs>
    <linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{BG_TOP}"/>
      <stop offset="1" stop-color="{BG_BOTTOM}"/>
    </linearGradient>
  </defs>

  <!-- Window frame -->
  <rect width="{WIDTH}" height="{height}" rx="12" fill="url(#ibg)"/>
  <rect x="0.5" y="0.5" width="{WIDTH-1}" height="{height-1}" rx="12" fill="none" stroke="{BORDER}"/>
  <line x1="0" y1="{TITLE_BAR}" x2="{WIDTH}" y2="{TITLE_BAR}" stroke="{BORDER}"/>

  <!-- Traffic lights -->
  <circle cx="20" cy="15" r="5" fill="{RED}"/>
  <circle cx="36" cy="15" r="5" fill="{YELLOW}"/>
  <circle cx="52" cy="15" r="5" fill="{TRAFFIC_GREEN}"/>

  <!-- Title -->
  <text x="{WIDTH/2}" y="19" fill="{DIM}" font-size="12" text-anchor="middle">{USERNAME}@github: ~$ neofetch</text>
'''

    for item in lines:
        delay = item["delay"]
        y = item["y"]

        anim = f'''<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>
    <animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" begin="{delay:.2f}s" dur="0.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>'''

        if item["type"] == "header":
            svg += f'''
  <g opacity="0" transform="translate(0,5)">
    <text x="{PADDING}" y="{y}" font-size="14" font-weight="700">
      <tspan fill="{GREEN}">{USERNAME}</tspan><tspan fill="{DIM}">@</tspan><tspan fill="{CYAN}">github</tspan>
    </text>
    <line x1="130" y1="{y-4}" x2="{WIDTH-PADDING}" y2="{y-4}" stroke="{BORDER}" stroke-opacity="0.8"/>
    {anim}
  </g>'''

        elif item["type"] == "info":
            svg += f'''
  <g opacity="0" transform="translate(0,5)">
    <text x="{PADDING}" y="{y}" fill="{ORANGE}" font-size="12.5" font-weight="700">{escape_xml(item["key"])}</text>
    <text x="{LABEL_X}" y="{y}" fill="{TEXT}" font-size="12.5">{escape_xml(item["value"])}</text>
    {anim}
  </g>'''

        elif item["type"] == "section":
            # Line starts after section title
            line_start = 85 if item["title"] == "Stack" else 110
            svg += f'''
  <g opacity="0" transform="translate(0,5)">
    <text x="{PADDING}" y="{y}" fill="{BLUE}" font-size="12.5" font-weight="700">— {item["title"]}</text>
    <line x1="{line_start}" y1="{y-4}" x2="{WIDTH-PADDING}" y2="{y-4}" stroke="{BORDER}" stroke-opacity="0.8"/>
    {anim}
  </g>'''

        elif item["type"] == "highlight":
            svg += f'''
  <g opacity="0" transform="translate(0,5)">
    <circle cx="23" cy="{y-4}" r="2.5" fill="{GREEN}"/>
    <text x="34" y="{y}" fill="{TEXT}" font-size="12.5">{escape_xml(item["text"])}</text>
    {anim}
  </g>'''

    svg += '\n</svg>'

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"Generated info card: {output_path}")


def main():
    script_dir = Path(__file__).parent.parent
    output_path = script_dir / "info-card.svg"
    generate_info_card(str(output_path))


if __name__ == "__main__":
    main()
