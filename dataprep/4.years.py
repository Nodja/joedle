import json
import csv
from pathlib import Path
from collections import defaultdict


def open_json(file, default=None):
    p = Path(file)
    if not p.exists():
        return default
    else:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)


def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


title_map = open_json("title_map.json", {})


def get_stream_years(title_map):
    stream_years = defaultdict(set)
    with open("streamdata.tsv", "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)  # Skip header
        for row in reader:
            date, game, stream_nr, src1, src2, src3 = row[0], row[1], row[2], row[3], row[4], row[5]
            if game in title_map:
                game = title_map[game]

            year = date[-4:]
            stream_years[game].add(year)

    return stream_years


quote_data = open_json("quotedata.json", {})
stream_years = get_stream_years(title_map)

for quote_id, quote in quote_data.items():
    year = quote.get("year", None)
    if year:
        quote["year"] = int(year)
        continue

    if quote["type"] != "Stream":
        continue

    title = quote.get("title", None)
    if title is None:
        print(f"Quote {quote_id} has no title, skipping")
        continue

    if title not in stream_years:
        mapping = input(f"Not found in stream years {title}: ")
        title_map[mapping] = title
        save_json("title_map.json", title_map)
        stream_years = get_stream_years(title_map)

    if title not in stream_years:
        print(f"Still not found in stream years {title}, skipping")
        continue
    try:
        years = sorted([int(y) for y in stream_years[title]])
    except ValueError:
        input(f"Failed to convert years for {title}, {stream_years[title]}")

    if len(years) == 1:
        quote["year"] = years[0]
    else:
        year = input(f"Unknown years for {quote['url']}, {years}: ")
        quote["year"] = int(year)

    save_json("quotedata.json", quote_data)

save_json("quotedata.json", quote_data)


# # final check
# for quote_id, quote in quote_data.items():
#     for field in ["quote", "title", "url", "type", "year"]:
#         if field not in quote:
#             print(f"Missing {field} for {quote_id}")
#             continue


# stream_years = {k: sorted(list(v)) for k, v in stream_years.items()}
# save_json("quotedata.json", quote_data)
# save_json("stream_years.json", stream_years)
