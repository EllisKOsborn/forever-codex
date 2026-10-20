# Forever Codex

A one-page guide to **World of Warcraft: Forever** for choosing and playing a main: news, datamines, MythicSim results, race sims, gear, raids and dungeons, levelling 1–60, crafting and a launch checklist. It covers Warlock, Mage and Shadow Priest so far.

**Live site:** https://elliskosborn.github.io/forever-codex/

## How it updates

- A scheduled Claude task runs every morning at 07:55 UK time. It researches the sources listed in [REFRESH.md](REFRESH.md), checks every claim against its source twice, updates the files in `data/`, and pushes to `main`.
- Each push runs [`scripts/check_data.py`](scripts/check_data.py). If any check fails, the site isn't republished, so bad data never goes live.
- The commit history is a day-by-day record of what changed.

## Files

| Path | What it is |
|---|---|
| `index.html` | The whole site (no build step) |
| `data/*.json` | Everything the site shows, one file per section |
| `scripts/check_data.py` | Accuracy and consistency checks |
| `REFRESH.md` | Instructions the daily refresh follows |
| `.github/workflows/publish.yml` | Runs the checks, then publishes to GitHub Pages |

Your notes, Legacy plans and checklist ticks are stored in your own browser, not in this repo.
