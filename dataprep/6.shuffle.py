import json
import csv
from pathlib import Path
from collections import defaultdict
import random
import datetime


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
order = list(range(1, len(quote_data) + 1))
date_start = datetime.date(2025, 3, 31)
random.seed(11037)
quotes = {}
for _ in range(10):
    random.shuffle(order)
    
    for o in order:
        dt = date_start.strftime("%Y-%m-%d")
        quotes[dt] = quote_data[str(o)]
        date_start += datetime.timedelta(days=1)

quotes_sample = {k: quotes[k] for k in list(quotes)[:10]}

save_json("quotes.json", quotes)
save_json("quotes_sample.json", quotes_sample)