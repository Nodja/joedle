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


quote_data = open_json("quotedata.json", {})

for quote_id, quote in quote_data.items():
    if "game" in quote and quote["game"]:
        continue

    if quote["type"] == "Stream":
        quote["game"] = quote["title"]
    else:
        game = input(f"Game for {quote['url']}: ")
        quote["game"] = game
        save_json("quotedata.json", quote_data)
    

save_json("quotedata.json", quote_data)