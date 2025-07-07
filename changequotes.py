import json
import datetime
from collections import OrderedDict
from pathlib import Path


def insert_quote(date_str, quote_obj):
    quotes_path = Path("public/quotes.json")

    with quotes_path.open("r", encoding="utf-8") as f:
        quotes = json.load(f)

    quotes_to_bump = {dt:q for dt, q in quotes.items() if dt >= date_str}
    _new_quotes = {}
    for dt, quote in quotes_to_bump.items():
        new_date = datetime.datetime.strptime(dt, "%Y-%m-%d") + datetime.timedelta(days=1)
        new_date_str = new_date.strftime("%Y-%m-%d")
        _new_quotes[new_date_str] = quote

    _new_quotes[date_str] = quote_obj

    quotes.update(_new_quotes)
    return quotes

def remove_quote(date_str):
    quotes_path = Path("public/quotes.json")
    with quotes_path.open("r", encoding="utf-8") as f:
        quotes = json.load(f)
    
    if date_str not in quotes:
        print(f"No quote found for date: {date_str}")
        return quotes
    
    del quotes[date_str]
    
    quotes_to_shift = {dt: q for dt, q in quotes.items() if dt > date_str}
    
    for dt in quotes_to_shift.keys():
        del quotes[dt]
    
    for dt, quote in quotes_to_shift.items():
        old_date = datetime.datetime.strptime(dt, "%Y-%m-%d")
        new_date = old_date - datetime.timedelta(days=1)
        new_date_str = new_date.strftime("%Y-%m-%d")
        quotes[new_date_str] = quote
    
    return quotes

def save_quotes(quotes):
    quotes_path = Path("public/quotes.json")
    with quotes_path.open("w", encoding="utf-8") as f:
        json.dump(quotes, f, indent=4, ensure_ascii=False)



if __name__ == "__main__":
    # date = "2025-05-10"  
    # new_quote = {
    #     "quote": "Yeah! Is he gonna be--oh please please Bitter, defeated, angry doesn't want to be along for the ride. Oh, please oh we might do another stream next week, please.[...] Please I will up it to six out of ten",
    #     "title": "New Content",
    #     "url": "https://example.com/video",
    #     "year": 2023,
    #     "type": "Stream",
    #     "game": "Example Game",
    # }

    # quotes = insert_quote(date, new_quote)
    # save_quotes(quotes)

    quotes = remove_quote("2025-10-27")
    save_quotes(quotes)
