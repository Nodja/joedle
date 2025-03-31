import json
import csv
from pathlib import Path


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


quote_data = open_json("quotedata.json", {})

todo_titles = {}
with open("quotestodo.tsv", "r", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter="\t")
    next(reader)  # Skip header
    for row in reader:
        quote_id, _, title = row[0], row[1], row[2]
        todo_titles[quote_id] = title


title_map = open_json("title_map.json", {})

for quote_id, quote in quote_data.items():
    if quote["type"] == "Stream":
        todo_title = todo_titles.get(quote_id)
        if todo_title and todo_title in title_map:
            quote["title"] = title_map[todo_title]
        else:
            mapping = input(todo_title + ": ")
            if mapping == "":
                quote["title"] = todo_title
                title_map[todo_title] = todo_title
                save_json("game_map.json", title_map)
            else:
                quote["title"] = mapping
                title_map[todo_title] = mapping
                save_json("game_map.json", title_map)

save_json("quotedata.json", quote_data)