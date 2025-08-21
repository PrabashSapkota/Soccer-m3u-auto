import requests
import re
from datetime import datetime, timedelta, timezone

# Source M3U URL
SOURCE_URL = "https://raw.githubusercontent.com/abusaeeidx/IPTV-Scraper-Zilla/refs/heads/main/daddylive-schedule.m3u"
OUTPUT_FILE = "soccer_schedule.m3u"

# Nepal timezone offset (UTC+5:45)
NEPAL_OFFSET = timedelta(hours=5, minutes=45)

def fetch_and_filter():
    r = requests.get(SOURCE_URL)
    r.raise_for_status()
    data = r.text.splitlines()

    seen_titles = set()
    filtered = ["#EXTM3U"]

    for i, line in enumerate(data):
        if line.startswith("#EXTINF") and 'group-title="Soccer"' in line:
            # Extract match title
            match = re.search(r',(.+)', line)
            if not match:
                continue
            title = match.group(1).strip()

            # Prevent duplicates
            if title in seen_titles:
                continue
            seen_titles.add(title)

            # Extract time in GMT if available
            time_match = re.search(r'tvg-name="(\d{2}:\d{2}) GMT"', line)
            if time_match:
                gmt_time_str = time_match.group(1)
                gmt_time = datetime.strptime(gmt_time_str, "%H:%M").replace(tzinfo=timezone.utc)
                local_time = (gmt_time + NEPAL_OFFSET).time().strftime("%H:%M")
                title = f"{title} ({local_time} NPT)"

            # Add only the title (no link)
            filtered.append(f"#EXTINF:-1,{title}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(filtered))

if __name__ == "__main__":
    fetch_and_filter()
    print(f"Updated {OUTPUT_FILE}")
