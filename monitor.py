import json
import os
import time
from pathlib import Path
from datetime import datetime, timezone

import requests

MAPS = [
    {"name": "Mount Blossom Peak", "place_id": 89188079951257, "url": "https://www.roblox.com/games/89188079951257"},
    {"name": "Sekolah Malam Club", "place_id": 117969282373364, "url": "https://www.roblox.com/games/117969282373364"},
    {"name": "Our Flower Garden", "place_id": 132699740251419, "url": "https://www.roblox.com/games/132699740251419"},
]

WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]
MESSAGE_FILE = "message_id.txt"
ROBLOX_API = "https://games.roblox.com/v1/games/{}/servers/Public"

session = requests.Session()
session.headers.update({"User-Agent": "BRF-Live-Monitor/1.0"})


def get_game_player_count(place_id, fallback_players):
    """Read the experience-wide playing count; fall back to listed server sum."""
    try:
        universe_response = session.get(
            f"https://apis.roblox.com/universes/v1/places/{place_id}/universe",
            timeout=25,
        )
        universe_response.raise_for_status()
        universe_id = universe_response.json()["universeId"]

        game_response = session.get(
            "https://games.roblox.com/v1/games",
            params={"universeIds": universe_id},
            timeout=25,
        )
        game_response.raise_for_status()
        games = game_response.json().get("data", [])
        if games:
            return int(games[0].get("playing", fallback_players)), "Roblox experience stats"
    except (requests.RequestException, KeyError, ValueError, TypeError) as exc:
        print(f"Could not fetch global player count for {place_id}: {exc}")
    return fallback_players, "sum of listed public servers"


def get_public_servers(place_id):
    """Count public server instances visible through Roblox pagination.
    Roblox may limit the server listing before every instance is returned.
    """
    cursor = None
    servers_seen = set()
    total_players = 0
    total_servers = 0
    pages = 0

    while pages < 20:  # safety cap: at most 2,000 listed servers per map
        params = {"sortOrder": "Asc", "limit": 100}
        if cursor:
            params["cursor"] = cursor

        response = session.get(
            ROBLOX_API.format(place_id),
            params=params,
            timeout=25,
        )
        response.raise_for_status()
        payload = response.json()

        for server in payload.get("data", []):
            server_id = server.get("id")
            if server_id and server_id not in servers_seen:
                servers_seen.add(server_id)
                total_servers += 1
                total_players += int(server.get("playing", 0))

        cursor = payload.get("nextPageCursor")
        pages += 1
        if not cursor:
            break
        time.sleep(0.15)

    global_players, player_source = get_game_player_count(place_id, total_players)
    return {
        "players": global_players,
        "servers": total_servers,
        "pages_scanned": pages,
        "capped": bool(cursor),
        "player_source": player_source,
    }


def discord_embed(results):
    total_players = sum(item["players"] for item in results)
    total_servers = sum(item["servers"] for item in results)
    now = datetime.now(timezone.utc).strftime("%d %b %Y • %H:%M UTC")

    lines = []
    for item in results:
        warning = " *(pagination API masih berlanjut)*" if item["capped"] else ""
        lines.append(
            f"**[{item['name']}]({item['url']})**\n"
            f"👥 Pemain online: **{item['players']}**\n"
            f"🖥️ Server publik terpantau: **{item['servers']}**{warning}"
        )

    description = "\n\n".join(lines)
    description += (
        f"\n\n━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 **TOTAL PEMAIN: {total_players}**\n"
        f"🖥️ **TOTAL SERVER TERPANTAU: {total_servers}**"
    )

    return {
        "username": "BRF LIVE MONITOR",
        "embeds": [{
            "title": "🐑 BIRI BIRI FAMILY — ROBLOX LIVE MONITOR",
            "description": description,
            "color": 0xF48FB1,
            "footer": {"text": f"Update otomatis • {now}"},
        }],
        "allowed_mentions": {"parse": []},
    }


def send_or_edit(payload):
    message_id = None
    if os.path.exists(MESSAGE_FILE):
        message_id = Path(MESSAGE_FILE).read_text(encoding="utf-8").strip() or None

    if message_id:
        edit_url = f"{WEBHOOK}/messages/{message_id}"
        response = session.patch(edit_url, json=payload, timeout=25)
        if response.status_code == 404:
            message_id = None
        else:
            response.raise_for_status()
            print(f"Updated Discord message {message_id}")
            return

    response = session.post(
        WEBHOOK + "?wait=true",
        json=payload,
        timeout=25,
    )
    response.raise_for_status()
    new_id = response.json()["id"]
    Path(MESSAGE_FILE).write_text(new_id, encoding="utf-8")
    print(f"Created Discord message {new_id}")


def main():
    results = []
    for game in MAPS:
        print(f"Checking {game['name']}...")
        stats = get_public_servers(game["place_id"])
        results.append({**game, **stats})
        print(
            f"{game['name']}: {stats['players']} players, "
            f"{stats['servers']} public servers"
        )

    send_or_edit(discord_embed(results))


if __name__ == "__main__":
    main()
