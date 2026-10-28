#!/usr/bin/env python3
"""Checks the Codex data before it is published.

Run from the repo root:  python3 scripts/check_data.py
Exits with code 1 (and lists the problems) if anything fails, so the daily
refresh and the GitHub Action can refuse to publish bad data.
These are the same checks the page runs in its footer, plus structure checks.
"""
import json, re, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
COLS = ["meta", "classes", "specs", "leveling", "tiers", "races", "news",
        "history", "gear", "dungeons", "digests"]
problems, warnings, n = [], [], 0


def check(ok, msg, warn=False):
    global n
    n += 1
    if not ok:
        (warnings if warn else problems).append(msg)


def iso(s):
    try:
        datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


D = {}
for c in COLS:
    try:
        D[c] = json.loads((DATA / f"{c}.json").read_text(encoding="utf-8"))
        check(isinstance(D[c], dict), f"{c}.json must be an object keyed by id")
    except Exception as e:  # missing or broken JSON stops everything
        print(f"FAIL: data/{c}.json can't be read: {e}")
        sys.exit(1)

meta, classes, specs = D["meta"], D["classes"], D["specs"]
app = meta.get("app", {})
for k in ["app", "dates", "legacy", "crafting", "launch"]:
    check(k in meta, f"meta.json is missing '{k}'")
check(iso(app.get("lastRefreshed")), "meta.app.lastRefreshed is not a valid ISO date")
for s in app.get("sources", []):
    check(str(s.get("url", "")).startswith("https://"), f"Source '{s.get('name')}' has no https link")
urls = [s.get("url") for s in app.get("sources", [])]
check(len(urls) == len(set(urls)), "meta.app.sources has duplicate links", warn=True)
for e in meta.get("dates", {}).get("events", []):
    check(iso(e.get("iso")), f"Date '{e.get('label')}' is not a valid ISO date")

known = set(classes)
ids = [i.get("id") for ph in meta.get("launch", {}).get("phases", []) for i in ph.get("items", [])]
check(len(ids) == len(set(ids)) and all(ids), "Plan items need unique, non-empty ids")
for ph in meta.get("launch", {}).get("phases", []):
    for k in ("from", "to"):
        if ph.get(k):
            check(iso(ph[k]), f"Plan phase '{ph.get('id')}' has an invalid '{k}' date")
tiers = list(D["tiers"].values())
ranks = sorted(t.get("rank") for t in tiers)
check(ranks == list(range(1, len(ranks) + 1)), "Tier list ranks have gaps or repeats")
for tid, t in D["tiers"].items():
    check(isinstance(t.get("dps"), (int, float)) and t["dps"] > 0, f"Tier '{tid}' has no DPS")
    check(t.get("tier") in {"S", "A", "B", "C", "D"}, f"Tier '{tid}' has an unknown band")

for cid, c in classes.items():
    check(c.get("id") == cid, f"Class '{cid}' has a mismatched id")
    rows = [(s, specs.get(s["id"])) for s in c.get("specs", [])]
    for s, x in rows:
        check(x is not None and isinstance(x.get("newDps"), (int, float)), f"{c['name']}: {s['name']} has no sim number")
    best = c.get("verdict", {}).get("best")
    check(best in specs, f"{c['name']}: the verdict names a spec with no data")
    scored = [(s, x) for s, x in rows if x and isinstance(x.get("newDps"), (int, float))]
    if best in specs and scored:
        top_s, top_x = max(scored, key=lambda r: r[1]["newDps"])
        check(specs[best]["newDps"] >= top_x["newDps"] * 0.99,
              f"{c['name']}: verdict picks {best} but {top_s['id']} sims higher ({top_x['newDps']} vs {specs[best]['newDps']})")
    for s, x in rows:
        if not x:
            continue
        t = next((t for t in tiers if t.get("clsId") == cid and str(t.get("spec", "")).lower() == str(x.get("name", s["name"])).lower()), None)
        if t:
            check((t["rank"], t["dps"], t["tier"]) == (x.get("tierRank"), x.get("tierDps"), x.get("tierBand")),
                  f"{s['name']} {c['name']}: tier list says #{t['rank']}, {t['dps']}, {t['tier']} but the spec says #{x.get('tierRank')}, {x.get('tierDps')}, {x.get('tierBand')}")
    for o in c.get("opinions", []):
        for g in o.get("grades", []):
            check(g.get("grade") in {"S", "A", "B", "C", "D", "F"} and g.get("spec") in specs,
                  f"{c['name']}: {o.get('site')} has an unreadable grade")

races = list(D["races"].values())
spec_ids = {sid for r in races for sid in r.get("boards", {})}
for sid in spec_ids:
    on = [r for r in races if sid in r.get("boards", {})]
    for r in on:
        check(isinstance(r["boards"][sid].get("dps"), (int, float)), f"{r['race']}: {sid} race sim has no number")
    best = [r for r in on if not r["boards"][sid].get("gap")]
    top = max(on, key=lambda r: r["boards"][sid].get("dps") or 0)
    check(len(best) == 1 and best[0] is top, f"Race sims for {sid}: the race marked best isn't the highest number")

for gid, g in D["gear"].items():
    for k in g.get("forClass", {}):
        check(k in known, f"Gear '{g.get('name')}' mentions an unknown class ({k})")
for did, d in D["dungeons"].items():
    for k in d.get("forClass", {}):
        check(k in known, f"Dungeon '{d.get('name')}' mentions an unknown class ({k})")
for nid, x in D["news"].items():
    check(bool(x.get("date")) and bool(x.get("source")), f"News '{x.get('title')}' has no date or source")
    for k in x.get("classes", []):
        check(k in known, f"News '{x.get('title')}' mentions an unknown class ({k})")
check(len(D["news"]) <= 60, "More than 60 news items; trim the oldest", warn=True)

hist = sorted(D["history"].values(), key=lambda h: h.get("date", ""))
for a, b in zip(hist, hist[1:]):
    for k, v in b.get("values", {}).items():
        p = a.get("values", {}).get(k)
        if isinstance(p, (int, float)) and isinstance(v, (int, float)) and p:
            check(abs(v - p) / p <= 0.15, f"{k} jumped {round((v - p) / p * 100)}% on {b['date']}; check it", warn=True)

for did, d in D["digests"].items():
    check(d.get("date") == did, f"Digest '{did}' has a mismatched date")
    for i in d.get("items", []):
        check(bool(i.get("source")), f"Digest {did}: an item has no source")
        check(i.get("confidence") in (None, "checked", "single"), f"Digest {did}: unknown confidence value")

lr = app.get("lastRefreshed")
if lr and iso(lr):
    age = datetime.now(timezone.utc) - datetime.fromisoformat(lr.replace("Z", "+00:00"))
    check(age < timedelta(hours=36), f"Data was last refreshed {lr}", warn=True)

for w in warnings:
    print("WARN:", w)
for p in problems:
    print("FAIL:", p)
print(f"{n} checks, {len(problems)} failed, {len(warnings)} warnings")
sys.exit(1 if problems else 0)
