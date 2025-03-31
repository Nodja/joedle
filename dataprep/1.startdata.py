import csv
import json

def lowercase_keys(d):
    return {k.lower(): v for k, v in d.items()}

quotes = {}
with open("quotestodo.tsv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        row = lowercase_keys(row)
        quote_id = row.pop("quote_id")
        quotes[quote_id] = row

with open("quotedata.json", "w", encoding="utf-8") as f:
    json.dump(quotes, f, indent=4, ensure_ascii=False)
