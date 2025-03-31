import csv
import os
import re
from collections import defaultdict

# --- Configuration ---
JOEVIDEOS_FILE = 'joevideotypes.txt'
QUOTES_FILE = 'quotestodo.txt'
OUTPUT_FILE = 'quotestodo_filled.tsv'
GAME_MAPPINGS_FILE = 'game_mappings.txt' # Optional: File for specific mappings

# --- Helper Functions ---

def parse_date_for_year(date_str):
    """Extracts the year from the date string (e.g., 'Mon, 09/07/2015')."""
    if not date_str or len(date_str) < 4:
        return None
    # Find the last occurrence of 4 consecutive digits, likely the year
    matches = re.findall(r'\b(\d{4})\b', date_str)
    if matches:
        return matches[-1] # Return the last found 4-digit number
    return None

def load_game_mappings(filename):
    """Loads specific game title mappings from a file and includes hardcoded ones."""
    mappings = {}
    # Add hardcoded essential mappings first (lowercase keys and values)
    # Map specific video titles to the general game name likely used in quotes
    hardcoded_mappings = {
        "dark souls critique - part one": "dark souls",
        "dark souls critique - part two": "dark souls",
        "dark souls critique - part three": "dark souls",
        "dark souls critique - part four": "dark souls",
        "dark souls critique - part five": "dark souls",
        "dark souls 2 - series strengths and sequel changes": "dark souls 2",
        "dark souls 2 - level design and bosses": "dark souls 2",
        "dark souls 2 - dlc levels and bosses": "dark souls 2",
        "dark souls 3 critique": "dark souls 3",
        "ashes of ariandel review (dark souls 3 dlc)": "dark souls 3",
        "the ringed city review (dark souls 3 dlc)": "dark souls 3",
        "bloodborne - series strengths and sequel changes": "bloodborne",
        "bloodborne - commentary and critique": "bloodborne",
        "bloodborne - chalice dungeons, and the old hunters": "bloodborne",
        "hollow knight critique": "hollow knight",
        "hollow knight dlc - swansong for silksong": "hollow knight", # Map DLC specific video to base game
        "the lion, the witcher, and the patreon": "the witcher", # Meta video, map if needed
        "the witcher critique - the beginning of a monster": "the witcher",
        "the witcher 2 commentary - a grand experiment": "the witcher 2",
        "god of war - almost a masterpiece": "god of war 2018",
        "god of war 2018 video commentary": "god of war 2018",
        "god of stuck in the room": "god of war 2018", # Assuming related to 2018 game stream
        "a critique of subnautica": "subnautica",
        "super mario odyssey - it's no masterpiece": "super mario odyssey",
        "hob critique - it's like zelda": "hob",
        "elden ring - a shattered masterpiece": "elden ring",
        "phase two (elden ring - shadow of the erdtree critique)": "elden ring",
        "elden ring dlc video commentary": "elden ring",
        "lies of p critique": "lies of p",
        "life is strange: bore the storm": "life is strange: before the storm",
        "life is strange: before the storm": "life is strange: before the storm",
        "a critique of a plague tale: innocence": "a plague tale: innocence",
        "a review of forager": "forager",
        "actraiser - a critique of the original - for true fans only": "actraiser",
        "anno 2205 review -- one small step forward, one small step back": "anno 2205",
        "ashen review and critique": "ashen",
        "breath of the wild - not enough zelda": "breath of the wild",
        "zelda: breath of the wild": "breath of the wild",
        "the legend of zelda: breath of the wild": "breath of the wild",
        "tears of the kingdom": "tears of the kingdom",
        "the legend of zelda: tears of the kingdom": "tears of the kingdom",
        "cuphead - a modest tutorial": "cuphead",
        "darkest dungeon review and critique": "darkest dungeon",
        "diablo 3 and reaper of souls critique": "diablo 3",
        "fallout 4 analysis": "fallout 4",
        "fallout 4 - one year later": "fallout 4",
        "the 1001 glitches of fallout 76": "fallout 76",
        "joseph anderson vs fallout 76": "fallout 76",
        "furi review": "furi",
        "hearthstone - the good, the bad, and the ugly": "hearthstone",
        "an inside joke (inside review)": "inside",
        "joseph anderson vs no man's sky": "no man's sky",
        "three games to refund no man's sky for": "no man's sky",
        "little nightmares, and the importance of the experience": "little nightmares",
        "minit review": "minit",
        "prey - a critique of the mind game": "prey",
        "return of the obra dinn - hopefully a classic": "return of the obra dinn",
        "rise of the tomb raider critique": "rise of the tomb raider",
        "should you play: factorio": "factorio",
        "a critique of soma": "soma",
        "stardew valley review": "stardew valley",
        "stephen's sausage roll - the best puzzle game i've played": "stephen's sausage roll",
        "the villain of edith finch": "what remains of edith finch",
        "the witness - a great game that you shouldn't play": "the witness",
        "tomb raider critique": "tomb raider",
        "a literary analysis of google chrome's t-rex runner": "t-rex runner",
        "vampire: the masquerade - bloodlines": "vampire: masquerade",
        "ai: the somnium files - nirvana initiative": "ai: nirvana initiative",
        "zero escape: virtue's last reward": "virtue's last reward",
        "zero escape: zero time dilemma": "zero time dilemma",
        "nine hours, nine persons, nine doors": "999",
        "999": "999", # Self map important ones
        "beyond: two souls": "beyond two souls",
        "fahrenheit: indigo prophecy": "indigo prophecy",
        "god of war: ragnarök": "god of war ragnarok",
        "god of war ragnarök": "god of war ragnarok",
        "star wars jedi: fallen order": "jedi: fallen order",
        "star wars: jedi survivor": "jedi: survivor",
        "jedi: survivor": "jedi: survivor",
        "va-11 hall-a": "va-11 hall-a", # Handle punctuation/caps variations
        "va-11 hall-a": "va-11 halla", # Alternate spelling if needed
        "the stanley parable": "stanley parable",
        "faster than light": "ftl: faster than light", # map short name often used
        "ftl: faster than light": "ftl: faster than light",
         # Meta videos might need special handling or mapping if quoted
        "subjectivity is implied": "subjectivity is implied",
        "the first annual chan of the year award": "chan of the year",
        "why horror games don't scare me": "horror games",

    }
    for k, v in hardcoded_mappings.items():
         mappings[k.lower()] = v.lower()

    # Optional: Load from file (TSV: original_title<tab>mapped_title)
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                for row in reader:
                    if len(row) == 2:
                        original, mapped = row
                        mappings[original.strip().lower()] = mapped.strip().lower()
            #print(f"Loaded additional mappings from {filename}")
        except Exception as e:
            print(f"Warning: Could not load game mappings from {filename}. Error: {e}")

    # Add self-mappings for all values to ensure consistency if looking up a mapped value
    all_mapped_values = list(mappings.values())
    for val in all_mapped_values:
         if val not in mappings: # Avoid overwriting existing keys pointing elsewhere
              mappings[val] = val

    # Also add self-mappings for common base game names if not already present
    common_games = ["dark souls", "dark souls 2", "dark souls 3", "bloodborne", "hollow knight",
                    "the witcher", "the witcher 2", "the witcher 3", "elden ring", "sekiro",
                    "god of war", "god of war 2", "god of war 3", "god of war 2018", "god of war ragnarok",
                    "subnautica", "super mario odyssey", "hob", "lies of p", "fallout 3", "fallout 4",
                    "fallout 76", "fallout: new vegas", "diablo 3", "factorio", "stardew valley",
                    "persona 3 reload", "persona 4 golden", "persona 5", "nier:automata",
                    "life is strange", "life is strange 2", "life is strange: before the storm", "life is strange: true colors",
                    "life is strange: double exposure", "cyberpunk 2077", "control", "alan wake", "alan wake 2",
                    "danganronpa", "danganronpa 2", "danganronpa v3", "ace attorney", "ace attorney 2", "ace attorney 3",
                    "999", "virtue's last reward", "zero time dilemma", "ai: the somnium files", "ai: nirvana initiative",
                    "balatro", "disco elysium", "undertale", "deltarune", "celeste", "hades", "inscryption",
                    "slay the spire", "return of the obra dinn", "outer wilds", "prey", "doom 2016", "doom eternal",
                    "resident evil 2 remake", "resident evil 3 remake", "resident evil 4 remake", "resident evil 7", "resident evil village",
                    "yakuza 0", "metal gear rising: revengeance", "the binding of isaac", "terraria", "minecraft",
                    "into the breach", "ftl: faster than light", "t-rex runner", "what remains of edith finch",
                    "horizon zero dawn", "uncharted", "uncharted 4", "the last of us", "red dead redemption 2",
                    "grand theft auto v", "path of exile", "genshin impact", "anno 2205", "dungeon keeper",
                    "actraiser", "cuphead", "furi", "inside", "soma", "the witness", "tomb raider", "rise of the tomb raider",
                    "dragon's dogma", "infinifactory", "darkest dungeon", "getting over it", "stephen's sausage roll",
                    "papers, please", "umineko when they cry", "steins;gate", "13 sentinels", "ghost trick",
                    "heavy rain", "beyond two souls", "detroit: become human", "indigo prophecy",
                    "a plague tale: innocence", "forager", "no man's sky", "ashen", "blasphemous", "code vein",
                    "control: awe", "dead space", "deadly premonition", "devil may cry 5", "dujanah",
                    "dusk", "euro truck simulator 2", "final fantasy xvi", "forspoken", "gollum",
                    "gravity rush", "gravity rush 2", "greedfall", "gris", "half-life 1", "half-life 2",
                    "hatsune miku: project diva", "hellpoint", "helldivers 2", "hi-fi rush", "hitman 3",
                    "hotline miami", "house flipper", "hypnospace outlaw", "jedi: fallen order", "jedi: survivor",
                    "jump king", "katana zero", "lisa: the painful", "marble races", "minit", "monster hunter: world",
                    "mortal shell", "neon white", "nine sols", "nioh", "noita", "opus magnum", "outer wilds: echoes of the eye",
                    "oxygen not included", "path of exile", "pizza tower", "portal", "portal 2", "powerwash simulator",
                    "rabi-ribi", "recettear", "returnal", "ruiner", "signalis", "silent hill", "silent hill 2",
                    "starfield", "super mario wonder", "the messenger", "they are billions", "titanfall 2",
                    "twelve minutes", "ufo 50", "ultrakill", "until dawn", "untitled goose game", "va-11 hall-a",
                    "vampire survivors", "wandersong", "wargroove", "xenoblade chronicles 2", "1000xresist"
                    ]
    for game in common_games:
         game_lower = game.lower()
         if game_lower not in mappings:
              mappings[game_lower] = game_lower

    return mappings


def preprocess_joevideos(filename, game_mappings):
    """Reads joevideotypes.txt, handles missing data, extracts year, normalizes game titles."""
    processed_data = []
    last_type = None
    last_date = None
    last_year = None

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            # Skip header line assuming it's the first line
            header = next(f, None)
            # print(f"Skipped header: {header.strip()}") # Debugging
            line_num = 1
            for line in f:
                line_num += 1
                original_line = line # Keep for debugging
                line = line.strip()
                if not line:
                    continue

                parts = line.split('\t')
                # Clean parts and remove empty strings potentially caused by adjacent tabs
                cleaned_parts = [p.strip() for p in parts if p.strip()]

                current_type = None
                current_date = None
                current_game = None
                current_year = None

                # --- Try to parse line structure ---
                if len(cleaned_parts) >= 3 and cleaned_parts[0] in ('Video', 'Stream') and '/' in cleaned_parts[1]:
                    # Standard: Type Date Game (Game might have spaces)
                    current_type = cleaned_parts[0]
                    current_date = cleaned_parts[1]
                    current_game = " ".join(cleaned_parts[2:]) # Join remaining parts as game title
                elif len(cleaned_parts) >= 2 and cleaned_parts[0] in ('Video', 'Stream'):
                     # Type Game (Missing Date?) - Inherit date
                     current_type = cleaned_parts[0]
                     current_date = last_date
                     current_game = " ".join(cleaned_parts[1:])
                elif len(cleaned_parts) >= 2 and '/' in cleaned_parts[0]:
                     # Date Game (Missing Type?) - Inherit type
                     current_type = last_type
                     current_date = cleaned_parts[0]
                     current_game = " ".join(cleaned_parts[1:])
                elif len(cleaned_parts) >= 1:
                     # Only Game? - Inherit type and date
                     # This covers indented lines or lines starting directly with game name
                     current_type = last_type
                     current_date = last_date
                     current_game = " ".join(cleaned_parts)
                # else: # len == 0 case already handled by strip/continue

                # --- Update state and store ---
                if current_game:
                    # Update last known good values IF new ones were found on *this* line structure parse
                    # Be careful not to overwrite with inherited 'None' values unless intended
                    if cleaned_parts[0] in ('Video', 'Stream'): last_type = current_type
                    if len(cleaned_parts) >=2 and '/' in cleaned_parts[0 if cleaned_parts[0] not in ('Video', 'Stream') else 1]:
                         last_date = current_date

                    # Parse year from the *effective* date for this entry
                    effective_date = current_date if current_date is not None else last_date
                    current_year = parse_date_for_year(effective_date)

                    # Update last_year only if a valid year was parsed for this entry's effective date
                    if current_year is not None:
                        last_year = current_year

                    # Normalize game title using mappings
                    game_lower = current_game.lower()
                    # Apply mapping if found, otherwise use the lowercase original
                    normalized_game = game_mappings.get(game_lower, game_lower)

                    # Use the most recently established valid type/year for storage
                    processed_data.append({
                        'type': last_type,      # The type applicable to this entry
                        'year': last_year,      # The year applicable to this entry
                        'game_normalized': normalized_game,
                        'game_original': current_game # Keep original for debugging
                    })
                    # Debugging print:
                    # print(f"L{line_num}: Stored: Type='{last_type}', Year='{last_year}', NormGame='{normalized_game}', OrigGame='{current_game}'")
                # else:
                    # print(f"Warning L{line_num}: Could not determine game from line: {original_line.strip()}")


    except FileNotFoundError:
        print(f"Error: File not found - {filename}")
        return None
    except Exception as e:
        print(f"Error processing {filename} near line {line_num}: {e}")
        print(f"Problematic line: {original_line.strip()}")
        return None

    return processed_data


# --- Main Script ---
if __name__ == "__main__":
    print(f"Loading game mappings...")
    game_mappings = load_game_mappings(GAME_MAPPINGS_FILE)
    print(f"Mappings loaded/generated: {len(game_mappings)}")


    print(f"Preprocessing {JOEVIDEOS_FILE}...")
    video_data = preprocess_joevideos(JOEVIDEOS_FILE, game_mappings)

    if video_data is None:
        print("Failed to preprocess video data. Exiting.")
        exit()
    print(f"Preprocessing complete. {len(video_data)} potential entries found.")

    # --- Build a lookup structure for faster matching ---
    # Key: normalized game title, Value: dict {'types': set(), 'years': set()}
    game_lookup = defaultdict(lambda: {'types': set(), 'years': set()})
    valid_entry_count = 0
    for entry in video_data:
        # Only add entries that have the necessary info resolved
        if entry.get('type') and entry.get('year') and entry.get('game_normalized'):
            game_lookup[entry['game_normalized']]['types'].add(entry['type'])
            game_lookup[entry['game_normalized']]['years'].add(entry['year'])
            valid_entry_count += 1
        # else: # Debugging invalid entries
            # print(f"Skipping invalid entry for lookup: {entry}")


    print(f"Built game lookup table with {len(game_lookup)} unique normalized game titles from {valid_entry_count} valid entries.")

    # --- Process Quotes ---
    print(f"Processing {QUOTES_FILE}...")
    output_lines = []
    quotes_processed = 0
    quotes_matched = 0

    try:
        with open(QUOTES_FILE, 'r', encoding='utf-8') as f_quotes:
            reader = csv.reader(f_quotes, delimiter='\t')
            header = next(reader) # Read header
            # Ensure header has 4 columns for output, even if input only had 2 initially
            output_header = header[:2] + ['Year', 'Type']
            output_lines.append("\t".join(output_header)) # Add header to output

            for i, row in enumerate(reader):
                quotes_processed += 1
                if not row: # Skip empty lines
                    continue
                if len(row) < 2:
                    print(f"Skipping malformed quote row {i+2}: {row}")
                    # Append original row data, padding with empty strings if needed
                    output_lines.append("\t".join(row + [''] * (4 - len(row))))
                    continue

                quote = row[0]
                quote_game_original = row[1].strip() # Game title from the quote file
                # Try to normalize the quote game title using the mappings as well
                quote_game_normalized = game_mappings.get(quote_game_original.lower(), quote_game_original.lower())

                found_types = set()
                found_years = set()

                # Look up using the normalized quote game title
                if quote_game_normalized in game_lookup:
                     match_data = game_lookup[quote_game_normalized]
                     found_types.update(t for t in match_data['types'] if t) # Filter None/empty types
                     found_years.update(y for y in match_data['years'] if y) # Filter None/empty years
                     if match_data['types'] or match_data['years']:
                           quotes_matched += 1
                # else: # Debugging unmatched games
                    # print(f"No match found in lookup for quote game: '{quote_game_original}' (normalized: '{quote_game_normalized}')")


                # --- Determine final type and year based on rules ---
                output_type = ''
                valid_types = {t for t in found_types if t}
                if len(valid_types) == 1:
                    output_type = list(valid_types)[0]
                # Rule: If both Video and Stream found, leave empty ''

                output_year = ''
                valid_years = {y for y in found_years if y} # Already filtered None/empty
                if len(valid_years) == 1:
                    output_year = list(valid_years)[0]
                # Rule: If multiple years found, leave empty ''

                # --- Construct output row ---
                # Ensure 4 columns: Quote, Video (Original Game), Year, Type
                output_row = [
                    quote,
                    quote_game_original, # Keep original game title from quote file
                    output_year,
                    output_type
                ]
                # Handle potential existing data in input cols 3 & 4 - overwrite them
                # output_row = row[:2] + [output_year, output_type] # This assumes input had 4 cols

                output_lines.append("\t".join(output_row))

    except FileNotFoundError:
        print(f"Error: File not found - {QUOTES_FILE}")
        exit()
    except Exception as e:
        print(f"Error processing {QUOTES_FILE}: {e}")
        exit()

    print(f"Processed {quotes_processed} quotes. Matched {quotes_matched} quotes to video/stream data.")

    # --- Write Output ---
    print(f"Writing results to {OUTPUT_FILE}...")
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f_out:
            for line in output_lines:
                f_out.write(line + '\n')
        print("Output file written successfully.")
    except Exception as e:
        print(f"Error writing output file {OUTPUT_FILE}: {e}")