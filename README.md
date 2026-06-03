# 2026 NBA Finals Dashboard 🏀
### NYK vs SAS — Projections vs Sportsbook Lines

Static GitHub Pages dashboard comparing model projections (built from playoff game logs) against live sportsbook prop lines, with edge probabilities.

---

## Files
| File | Purpose |
|------|---------|
| `index.html` | The dashboard (self-contained UI + logic) |
| `projections.js` | Auto-generated player projections + σ |
| `regenerate.py` | Re-runs the model from the Excel logs to rebuild `projections.js` |
| `NBA_Finals_Spurs_Knicks_Stats.xlsx` | Your game-log source data |

---

## Deploy to GitHub Pages (2 min)
1. Create a repo, drop all files in the root.
2. `git add . && git commit -m "finals dashboard" && git push`
3. Repo **Settings → Pages → Source: main branch / (root)** → Save.
4. Live at `https://<you>.github.io/<repo>/` within a minute.

Your API key is **never committed** — it's typed into the browser at runtime and stays local.

---

## Using the dashboard
- **Manual mode (default):** type each sportsbook o/u line into the boxes. Edge flags update instantly.
- **Live mode:** paste your [the-odds-api.com](https://the-odds-api.com) key (free tier = 500 req/mo) and switch Mode to *Live*. It auto-fills lines from US books.

**Edge logic:** each stat carries σ (game-to-game std dev). Over probability = `1 − Φ((line − projection)/σ)`. Green = P>55%, red = P<45%.

---

## Updating after each game
1. Add the new game's rows to the Excel file (same columns, append to the round sheet).
2. Run `python regenerate.py` → rewrites `projections.js`.
3. Commit & push. Pages redeploys automatically.

(Optional: a GitHub Action can run step 2 on every push — ask if you want the workflow file.)

---

## The Model
- **Weighting:** GP-adjusted. Base R1 0.20 / Semis 0.30 / CF 0.50, each × (GP ÷ series length), renormalized. Down-weights small samples (e.g. OG's 2-game semis).
- **Points:** rebuilt from components, `2·FGM + 3PM + FTM` (no double-counting threes).
- **Pure form:** no opponent/matchup adjustment, by design.
- **Variance:** pooled σ across all playoff games (incl. the OT game, kept as-is per your call).

Players tracked: top 8 rotation per team, ordered by projected scoring.

---

## Automatic odds refresh (GitHub Action)
A scheduled workflow (`.github/workflows/refresh-odds.yml`) fetches sportsbook player props **every 3 hours on game days** and commits them to `odds.json`. The dashboard auto-loads that file on page open — no key needed in the browser.

**One-time setup:**
1. Repo → **Settings → Secrets and variables → Actions → New repository secret**
2. Name: `ODDS_API_KEY`  ·  Value: your the-odds-api.com key  → Save
3. That's it. The Action reads the secret; the key is encrypted and never appears in the repo or the deployed page.

**Notes:**
- Trigger it manually any time via repo → **Actions → Refresh NBA Finals Odds → Run workflow**.
- Player props usually post the morning of game day; before then the Action soft-passes and the dashboard stays in manual mode (no errors, no crash).
- Lines are averaged across all US books returned.
- Schedule is hard-coded to the 2026 Finals dates (Jun 3,5,8,10,13,16,19, in UTC). If the series ends early, the leftover dates simply find no game and soft-pass.

---

## Finals weighting (after Game 1+)
Once Finals games are played, add a sheet named **`Knicks F`** and **`Spurs F`** (same columns as the round sheets) and append each Finals game's box scores there. The model treats Finals as the **heaviest tier**, and it grows with games played:

| Finals games | Finals tier weight | R1/R2/R3 share the rest |
|---|---|---|
| 1 | 40% | 60% (split .20/.30/.50) |
| 2 | 55% | 45% |
| 3+ | 65% | 35% |

This stops a single noisy game from dominating, while letting the series take over by Game 3-4. With zero Finals games, the model is identical to the original R1/R2/R3 build.
