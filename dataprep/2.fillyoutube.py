import json
import yt_dlp
from urllib.parse import urlparse


def get_youtube_data(url):
    ydl_opts = {
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            channel = info.get("channel")
            title = info.get("title")
            year = info.get("upload_date")[0:4]
            return channel, title, year
        except Exception as e:
            print(f"Error processing {url}: {e}")
            return None, None, None


# Read JSON file
with open("quotedata.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Process each entry
for key, entry in data.items():
    if entry.get("type", "") != "":
        continue

    url = entry.get("url", "")
    parsed_url = urlparse(url)
    print(f"Processing {url}")
    if "reddit.com" in parsed_url.netloc:
        entry["year"] = None
        entry["type"] = "Reddit"
        entry["title"] = "Reddit Post"
    elif "youtube.com" in parsed_url.netloc or "youtu.be" in parsed_url.netloc:
        channel, title, year = get_youtube_data(url)
        if channel is None:
            print(f"Failed to get data for {url}")
            continue
        if channel == "Joseph Anderson":
            entry["title"] = title
            entry["type"] = "YouTube"
            entry["year"] = year
        else:
            entry["title"] = None
            entry["type"] = "Stream"
            entry["year"] = None

    else:
        entry["title"] = None
        entry["type"] = "Unknown"
        entry["year"] = None

    with open("quotedata.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
