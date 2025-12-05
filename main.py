import requests
import json
import os
import sys

# --- CONFIG ---
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
SEEN_FILE = "seen_games.json"

if not WEBHOOK_URL:
    print("Error: WEBHOOK_URL secret is missing!")
    sys.exit(1)

def get_seen_games():
    if not os.path.exists(SEEN_FILE):
        return []
    with open(SEEN_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_seen_games(seen_ids):
    with open(SEEN_FILE, "w") as f:
        json.dump(seen_ids, f)

def send_discord_notification(game):
    embed = {
        "title": game['title'],
        "description": game['description'],
        "url": game['open_giveaway_url'],
        "color": 5763719, # Green
        "image": {"url": game['image']},
        "fields": [
            {"name": "Worth", "value": game.get('worth', 'N/A'), "inline": True},
            {"name": "Platform", "value": game['platforms'], "inline": True},
            {"name": "End Date", "value": game.get('end_date', 'Unknown'), "inline": True}
        ],
        "footer": {"text": "Free Game Alert • GamerPower API"}
    }
    
    payload = {
        "username": "Free Games Bot",
        "avatar_url": "https://i.imgur.com/4M34hi2.png",
        "embeds": [embed]
    }
    
    requests.post(WEBHOOK_URL, json=payload)

def main():
    # 1. Load History
    seen_ids = get_seen_games()
    
    # 2. Fetch Active Giveaways (PC only to reduce spam, remove filter if you want Console too)
    print("Fetching games...")
    r = requests.get("https://www.gamerpower.com/api/giveaways?platform=pc")
    games = r.json()
    
    new_seen_ids = seen_ids.copy()
    has_new_games = False

    # 3. Check for new games
    # We iterate in reverse so older games are processed first if multiple appear
    for game in reversed(games):
        # We only care about "Game" (ignoring DLCs usually)
        if game.get("type") != "Game":
            continue
            
        game_id = str(game['id'])
        
        if game_id not in seen_ids:
            print(f"Found new game: {game['title']}")
            send_discord_notification(game)
            new_seen_ids.append(game_id)
            has_new_games = True
            
    # 4. Save History
    if has_new_games:
        print("Saving new games to history...")
        save_seen_games(new_seen_ids)
    else:
        print("No new games found.")

if __name__ == "__main__":
    main()
