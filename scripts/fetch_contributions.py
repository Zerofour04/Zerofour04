#!/usr/bin/env python3
"""
Fetch GitHub contribution data from the public contributions page.
No API token required - scrapes the public HTML.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "Zerofour04"


def fetch_contributions() -> dict:
    """Fetch contribution data from GitHub's public contributions page."""
    url = f"https://github.com/users/{USERNAME}/contributions"

    response = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; ProfileReadme/1.0)"
    })
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Get total from h2 heading (e.g., "668 contributions in the last year")
    total = 0
    h2 = soup.find("h2", class_="f4")
    if h2:
        import re
        match = re.search(r'([\d,]+)\s+contributions', h2.get_text())
        if match:
            total = int(match.group(1).replace(',', ''))

    # Find all contribution cells
    cells = soup.find_all("td", class_="ContributionCalendar-day")

    days = []
    for cell in cells:
        date = cell.get("data-date")
        level = cell.get("data-level", "0")

        if date:
            days.append({
                "date": date,
                "level": int(level)
            })

    # Sort by date
    days.sort(key=lambda x: x["date"])

    # Current streak (based on level > 0)
    current_streak = 0
    today = datetime.now().date()
    for d in reversed(days):
        day_date = datetime.strptime(d["date"], "%Y-%m-%d").date()
        if day_date > today:
            continue
        if d["level"] > 0:
            current_streak += 1
        else:
            break

    # Longest streak
    longest_streak = 0
    streak = 0
    for d in days:
        if d["level"] > 0:
            streak += 1
            longest_streak = max(longest_streak, streak)
        else:
            streak = 0

    return {
        "username": USERNAME,
        "generated_at": datetime.now().isoformat(),
        "days": days,
        "stats": {
            "total": total,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
        }
    }


def main():
    script_dir = Path(__file__).parent.parent
    data_dir = script_dir / "data"
    data_dir.mkdir(exist_ok=True)

    output_path = data_dir / "contributions.json"

    print(f"Fetching contributions for {USERNAME}...")
    data = fetch_contributions()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Saved {len(data['days'])} days of data to {output_path}")
    print(f"Total contributions: {data['stats']['total']}")
    print(f"Current streak: {data['stats']['current_streak']} days")


if __name__ == "__main__":
    main()
