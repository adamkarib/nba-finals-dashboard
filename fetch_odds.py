#!/usr/bin/env python3
"""Fetch NBA Finals player props from The Odds API and write odds.json.
Key comes from env var ODDS_API_KEY (GitHub secret). Never hardcode it.
Fails SOFT: if no props are available yet (props usually post game-day
morning), it writes/keeps a valid file and exits 0 so the Action is green."""
import os, sys, json, time, urllib.request, urllib.error

KEY = os.environ.get("ODDS_API_KEY", "").strip()
BASE = "https://api.the-odds-api.com/v4"
MARKETS = "player_points,player_rebounds,player_assists"
STAT_MAP = {"player_points": "pts", "player_rebounds": "reb", "player_assists": "ast"}

def get(url):
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.load(r)

def main():
    out = {"updated": int(time.time()), "lines": {}, "note": ""}
    if not KEY:
        out["note"] = "No ODDS_API_KEY set"; write(out); return 0
    try:
        events = get(f"{BASE}/sports/basketball_nba/events?apiKey={KEY}")
    except urllib.error.HTTPError as e:
        out["note"] = f"events HTTP {e.code}"; write(out); return 0
    except Exception as e:
        out["note"] = f"events error {e}"; write(out); return 0

    game = next((e for e in events
                 if "spurs" in (e.get("home_team","")+e.get("away_team","")).lower()
                 or "knicks" in (e.get("home_team","")+e.get("away_team","")).lower()), None)
    if not game:
        out["note"] = "No NYK/SAS event listed yet"; write(out); return 0

    try:
        odds = get(f"{BASE}/sports/basketball_nba/events/{game['id']}/odds"
                   f"?apiKey={KEY}&regions=us&markets={MARKETS}&oddsFormat=american")
    except urllib.error.HTTPError as e:
        # 422 = market not offered yet (props not posted). Soft-pass.
        out["note"] = f"odds HTTP {e.code} (props may not be posted yet)"; write(out); return 0
    except Exception as e:
        out["note"] = f"odds error {e}"; write(out); return 0

    # Average the line across all books for each player+stat
    agg = {}
    for bk in odds.get("bookmakers", []):
        for mk in bk.get("markets", []):
            stat = STAT_MAP.get(mk.get("key"))
            if not stat: continue
            for o in mk.get("outcomes", []):
                pt = o.get("point")
                if pt is None: continue
                k = f"{o.get('description','')}|{stat}"
                agg.setdefault(k, []).append(pt)
    out["lines"] = {k: round(sum(v)/len(v), 1) for k, v in agg.items()}
    out["game"] = f"{game.get('away_team')} @ {game.get('home_team')}"
    out["note"] = f"{len(out['lines'])} prop lines (averaged across books)"
    write(out); return 0

def write(out):
    json.dump(out, open("odds.json", "w"), indent=1)
    print(out["note"])

if __name__ == "__main__":
    sys.exit(main())
