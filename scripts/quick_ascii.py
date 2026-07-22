#!/usr/bin/env python3
"""ASCII portrait with typing animation."""

from PIL import Image, ImageEnhance

# Sparse -> Dense (bright = space, dark = dense)
RAMP = " .:-=+*#%@"

COLS = 80
ROWS = 40

FONT_SIZE = 10
CHAR_WIDTH = 6
CHAR_HEIGHT = 11
TEXT_COLOR = "#c9d1d9"
BG_COLOR = "#0d1117"

def main():
    # Try png first, fallback to jpg
    try:
        img = Image.open("source-photo.png").convert("L")
    except:
        img = Image.open("source-photo.jpg").convert("L")

    # Boost contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.3)

    # Resize with aspect ratio correction for monospace
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

    width = COLS * CHAR_WIDTH + 20
    height = ROWS * CHAR_HEIGHT + 20

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <style>
    @keyframes typeRow {{
      from {{ clip-path: inset(0 100% 0 0); }}
      to {{ clip-path: inset(0 0 0 0); }}
    }}
    .row {{
      font-family: "SF Mono", "Fira Code", monospace;
      font-size: {FONT_SIZE}px;
      fill: {TEXT_COLOR};
      clip-path: inset(0 100% 0 0);
      animation: typeRow 0.2s ease-out forwards;
    }}
  </style>
  <rect width="100%" height="100%" fill="{BG_COLOR}"/>
'''

    for i, line in enumerate(lines):
        y = 15 + i * CHAR_HEIGHT
        delay = i * 0.03
        escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        svg += f'  <text class="row" x="10" y="{y}" style="animation-delay:{delay:.2f}s">{escaped}</text>\n'

    svg += '</svg>'

    with open("ascii-portrait.svg", "w") as f:
        f.write(svg)
    print("Generated ascii-portrait.svg")

if __name__ == "__main__":
    main()
