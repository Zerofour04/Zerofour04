#!/usr/bin/env python3
"""
Generate macOS terminal-style ASCII portrait SVG with typing animation.
Based on avivashishta's design.
"""

from pathlib import Path
from PIL import Image, ImageEnhance

# ASCII density ramp: bright (sparse) -> dark (dense)
RAMP = " .`:-=+*cs#%@"

# Grid dimensions
COLS = 100
ROWS = 53

# SVG styling
FONT_FAMILY = 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace'
FONT_SIZE = 12.9
LINE_HEIGHT = 15
CHAR_WIDTH = 8  # textLength / COLS

TEXT_COLOR = "#c9d1d9"
DIM_COLOR = "#7d8590"
BG_GRADIENT_TOP = "#111722"
BG_GRADIENT_BOTTOM = "#0d1117"
BORDER_COLOR = "#30363d"

# Traffic light colors
RED = "#ff5f56"
YELLOW = "#ffbd2e"
GREEN = "#27c93f"

# Layout
PADDING = 20
TITLE_BAR_HEIGHT = 30
STATUS_BAR_HEIGHT = 43
CONTENT_WIDTH = 800

# Animation
ROW_DURATION = 0.11  # seconds per row

# User info
USERNAME = "zerofour04"
REAL_NAME = "Ben Ho"


def image_to_ascii(image_path: str) -> list[str]:
    """Convert prepped image to ASCII lines."""
    img = Image.open(image_path).convert("L")

    # Resize with aspect correction
    img = img.resize((COLS, int(ROWS * 1.8)), Image.Resampling.LANCZOS)
    img = img.resize((COLS, ROWS), Image.Resampling.LANCZOS)

    lines = []
    for y in range(ROWS):
        line = ""
        for x in range(COLS):
            brightness = img.getpixel((x, y))
            idx = int(brightness / 256 * len(RAMP))
            idx = min(idx, len(RAMP) - 1)
            line += RAMP[idx]
        lines.append(line)

    return lines


def generate_svg(ascii_lines: list[str], output_path: str):
    """Generate the macOS terminal-style SVG."""

    width = CONTENT_WIDTH + PADDING * 2
    height = TITLE_BAR_HEIGHT + len(ascii_lines) * LINE_HEIGHT + STATUS_BAR_HEIGHT + PADDING

    svg_parts = []

    # Header
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="{FONT_FAMILY}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{BG_GRADIENT_TOP}"/>
      <stop offset="1" stop-color="{BG_GRADIENT_BOTTOM}"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="{width}" height="{height}" rx="12" fill="url(#bg)"/>
  <rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="12" fill="none" stroke="{BORDER_COLOR}" stroke-width="1"/>

  <!-- Title bar -->
  <line x1="0" y1="{TITLE_BAR_HEIGHT}" x2="{width}" y2="{TITLE_BAR_HEIGHT}" stroke="{BORDER_COLOR}"/>

  <!-- Traffic lights -->
  <circle cx="20" cy="15" r="5" fill="{RED}"/>
  <circle cx="36" cy="15" r="5" fill="{YELLOW}"/>
  <circle cx="52" cy="15" r="5" fill="{GREEN}"/>

  <!-- Title -->
  <text x="{width/2}" y="19" fill="{DIM_COLOR}" font-size="12" text-anchor="middle">{USERNAME}@github: ~$ ./portrait.sh</text>
''')

    # ASCII rows with typing animation
    for i, line in enumerate(ascii_lines):
        y_base = TITLE_BAR_HEIGHT + 7 + i * LINE_HEIGHT
        y_text = y_base + LINE_HEIGHT - 3.9
        delay = i * ROW_DURATION
        end_time = delay + ROW_DURATION

        # Escape special chars
        escaped = (line
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))

        # Clip path for typing reveal
        svg_parts.append(f'''
  <!-- Row {i} -->
  <clipPath id="r{i}">
    <rect x="{PADDING}" y="{y_base}" height="{LINE_HEIGHT}" width="0">
      <animate attributeName="width" from="0" to="{CONTENT_WIDTH}" begin="{delay:.3f}s" dur="{ROW_DURATION}s" fill="freeze"/>
    </rect>
  </clipPath>
  <g clip-path="url(#r{i})">
    <text xml:space="preserve" x="{PADDING}" y="{y_text}" fill="{TEXT_COLOR}" font-size="{FONT_SIZE}" textLength="{CONTENT_WIDTH}" lengthAdjust="spacing">{escaped}</text>
  </g>

  <!-- Cursor for row {i} -->
  <rect y="{y_base + 1}" width="8" height="13" fill="{TEXT_COLOR}" opacity="0">
    <animate attributeName="x" from="{PADDING}" to="{PADDING + CONTENT_WIDTH}" begin="{delay:.3f}s" dur="{ROW_DURATION}s" fill="freeze"/>
    <set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>
    <set attributeName="opacity" to="0" begin="{end_time:.3f}s"/>
  </rect>''')

    # Status bar
    status_y = TITLE_BAR_HEIGHT + len(ascii_lines) * LINE_HEIGHT + 7

    svg_parts.append(f'''

  <!-- Status bar -->
  <line x1="0" y1="{status_y}" x2="{width}" y2="{status_y}" stroke="{BORDER_COLOR}"/>
  <text x="{PADDING}" y="{status_y + 19}" fill="{DIM_COLOR}" font-size="13">{USERNAME}@github:~$ whoami <tspan fill="{TEXT_COLOR}">{REAL_NAME}</tspan></text>

  <!-- Blinking cursor -->
  <rect x="{PADDING + 200}" y="{status_y + 7}" width="8" height="14" fill="{TEXT_COLOR}">
    <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/>
  </rect>
</svg>''')

    svg_content = "".join(svg_parts)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"Generated ASCII SVG: {output_path}")


def main():
    script_dir = Path(__file__).parent.parent
    input_path = script_dir / "source-prepped.png"
    output_path = script_dir / "ascii-portrait.svg"

    if not input_path.exists():
        print(f"Error: {input_path} not found. Run prep_photo_simple.py first.")
        return

    ascii_lines = image_to_ascii(str(input_path))
    generate_svg(ascii_lines, str(output_path))


if __name__ == "__main__":
    main()
