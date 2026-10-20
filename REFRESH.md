# Daily refresh instructions

These are the instructions the scheduled "Forever Codex refresh" follows every morning. Edit them here (not in the scheduled task) so changes are versioned.

Ellis is in the UK (Europe region) and is choosing a main before WoW: Forever launches (4 Nov 2026, raids 9 Dec) between the classes in `data/classes.json` (currently Warlock, Mage, Priest; Warlock is the default view). He cares about raids, dungeons and levelling 1–60, and wants the sims to decide specs.

**Accuracy matters more than completeness: a stale value is acceptable, a wrong or invented one is not.**

## How the site works

- `index.html` is the whole site. It reads `data/*.json` and renders. GitHub Pages republishes it after every push to `main`, but only if `scripts/check_data.py` passes (see `.github/workflows/publish.yml`).
- Do **not** edit `index.html` during a refresh. Only change files in `data/`.
- Each `data/<collection>.json` is one JSON object keyed by document id. `data/meta.json` holds five documents: `app`, `dates`, `legacy`, `crafting`, `launch`.
- Edit the JSON with short Python read-modify-write scripts (`json.load` → change → `json.dump(..., ensure_ascii=False, indent=1)`). Never retype a whole file from memory or from tool output. Change only the fields you mean to change.

## Steps

1. Get the repo: call the `add_repo` tool with owner `EllisKOsborn`, repo `forever-codex`, access `push`, then clone it as that tool says. Copy `data/` to a scratch folder as "yesterday" for the digest.
2. Research (below), following the accuracy protocol.
3. Update `data/*.json`, write today's digest last, set `meta.app.lastRefreshed` (ISO with Europe/London offset) and `meta.app.build`.
4. Run `python3 scripts/check_data.py`. If it prints any FAIL, fix the data and run it again. **Never push data that fails.** Warnings are fine but mention them in the digest.
5. `git add data && git commit -m "Refresh YYYY-MM-DD: <digest headline, short>"`, then `git pull --rebase origin main` and `git push origin main`. If the push fails, retry once; if it still fails, say so in the summary.
6. Finish with a 4–6 line summary for Ellis that matches the digest: headline, the best spec per class and any rank moves, buffs/nerfs, datamine finds, raid or launch news, what was corrected or held back, and anything you couldn't check. If nothing changed, say so in one line.

## Data model (keep field names exactly)

Spec ids are `<spec>-<class>`, e.g. `demonology-warlock`, `fire-mage`, `shadow-priest`.

- `meta.app` {lastRefreshed, build, defaultClass, sources[{name,url}] (no duplicate URLs, all https), facts[] (game-wide), tierNote, gearNote, dungeonNote, compareNote, raidNote (one short line), raidFacts[]}
- `meta.dates` {events[{label, iso, note, showTime?}]}
- `meta.launch` {summary, checklist[{id, text, when? (YYYY-MM-DD), why, classes? []}], cards[{title,items}], addonNote, addons[{name, cat Levelling|Raid|Planning|Maps|Interface, use, status, url?}]}. Checklist ticks are saved in viewers' browsers by id, so never rename an existing id.
- `meta.legacy` {budget, summary, trees[{name, perks[{id,name,ranks,req,prereq?,effect}]}]}
- `meta.crafting` {tailoring{bands, whatsNew}, camping{summary, features[{name,prof,buff,notes{<classId>:text}}], rules}}
- `classes.<classId>` {id, name, order, accent{light,lightSoft,dark,darkSoft,tip}, specs[{id,key,name,experimental,color}], verdict{best (spec id with the highest newest-sim DPS; prefer non-experimental within 1%), headline, body, statsNote, flavour}, latestLabel, latestChanges[{kind buff|nerf|neutral, spec (spec id or "all"), text}], changeLog[{label, items[...]}] (prepend a group per new build), opinions[{site,url,date,note,grades[{spec,grade}]}], raceNote, raceSnapshot, classCards[{title,items}], facts[], compare{role, levelling, utility[], pros[], cons[], population{alliance, horde, note}}, crafting{...}, legacy{recommended{perkId:ranks}, recommendedNote, recommendedLabel, alternate?, alternateLabel?}, macros{note, macros[{name,text,note}]}}
- `specs.<specId>` {id, cls, key, name, experimental, summary, build, race, tierRank, tierDps, tierBand, newDps, newNote (source page, engine, client, date), raidRotation[], dungeonTips[], threatMana[], stats[], trinkets[{name,gain,source}], trinketSnapshot, consumables[], talentNotes[], raceBoard{snapshot,note}, cards[{title,items}]}
- `leveling.<classId>` {summary, bands[{range,spec,title,talents,spells,pet?,pulls?,wand,gear,zonesA,zonesH,dungeons,tip}], professions[], legacy[], gearRules[], habits[], cards[{title,items}], tables[{title,columns,rows}]}
- `tiers.<specId>` {rank, spec, cls, clsId, dps (no-trinket figure), tier S/A/B/C (the section the card sits under), build, engine ("<commit>, <date>"), older (true only if that row's engine is older than the rest), change ("+x.x% vs last run" or "no change"), ranged, experimental} for every MythicSim DPS spec
- `races.<raceId>` {race, faction, order, abilities[{name,effect}], boards{<specId>:{dps, gap ("" for best else "x.xx%"), tier}}, simText{<classId>:text}, classSpells{<classId>:[{name,level,effect}]}, notes{<classId>:text}, classes[]}
- `history.<YYYY-MM-DD>` {date, values{<specId>:dps}, labels{<classId>:source+engine}}: add today's when any tracked spec's newest-sim DPS changed.
- `news.<id>` {date, title, summary (1–2 plain sentences, own words), tag patch|datamine|sim|talents|blizzard, classes[] ([] = everyone), source, url}. id `nYYYYMMDD-<slug>`. Datamines: tag `datamine`, title starts "Found in the files:". No duplicate stories. Keep at most 60; delete the oldest beyond that.
- `gear.<slug>` {name, slot, category wand|levelling|crafted|preraid|raid|trinket, level, source, url?, verified, order, forClass{<classId>:{notes, specs[]}}}. Each tracked class keeps its tier set doc.
- `dungeons.<slug>` {name, levels, min, max, location, isNew, bosses, note, type dungeon|raid, size?, forClass{<classId>:{note?, loot?}}; raids also bossList[], bossNote, attunement, entrance, comp}
- `digests.<YYYY-MM-DD>` (the "Since yesterday" card) {date, at, headline (the most important change for Ellis's choice of main), items[{kind buff|nerf|neutral, classes[], text (with old and new value where relevant), source, url, confidence "checked"|"single"}], unchecked[], checks{verified, method, corrected[], flagged[]}}. Compare today's data with "yesterday" and list every changed sim number, rank, band, verdict, date, build, opinion grade, plus each new news item worth reading. If nothing changed, one neutral item saying so. Keep the newest 14; delete older.

## Research

1. **Shared, once:** Blizzard WoW Forever beta development notes and hotfixes (us.forums.blizzard.com, news.blizzard.com incl. stress test page); Bluetracker for blue and developer posts (Reddit and X can't be fetched; use Bluetracker and articles that quote them); Bind on Forever (bindonforever.com/changes, dungeons, legacy, camping); Wowhead Forever changes and item sets; Icy Veins WoW Forever news; Kami Labs and ForeverChanges patch breakdowns; raid guides (Daybreak Forever /raid/barrow-deeps, warcrafttavern.com/forever/guides/raids, Conquest Capped Hyjal Summit guide, theforeverera.com/en/raids/barrow-deeps, lfcarry.com/guides/wow-forever-raids); MythicSim tier list (mythicsim.com/wow-forever/tier-list; read ALL rows every day, it changes without notice); LFCarry tier list for opinions; census figures if new ones appear (classicplus.io via Icy Veins/Kami Labs); addon support changes; a news search for "WoW Forever" from the last 2 days. From 9 December, check whether Warcraft Logs or Archon publish Forever raid rankings; if so add them as a source, an opinion per class and a news item.
2. **Per class:** MythicSim class page (mythicsim.com/wow-forever/<class>), race boards (mythicsim.com/wow-forever/races?class=<class>&spec=<specId>) and trinket boards (mythicsim.com/wow-forever/best-trinkets/<specId>); TalentsForever (talentsforever.com/<class>/changes and /leveling); ForeverChanges BiS (foreverchanges.pro/bis/<class>); Daybreak Forever (daybreakforever.com/skills/<class>). newDps = the newest-engine number across class page, trinket-board baseline and tier list (say which in newNote).
3. **Adding a class:** if `meta.app.pendingClasses` lists class names, research each and add it everywhere (classes with a distinct accent pair readable in light and dark, specs, leveling, races rows, gear forClass incl. its tier set, dungeon and raid loot, history), then remove it from pendingClasses. Same accuracy rules.

## Accuracy protocol (all of it, before committing)

- **A. Claims ledger.** Keep `claims.json` outside the repo. Every value you write (number, rank, band, date, build, name, percentage, set bonus, boss, change) gets a row {file, id, field, old, new, url, quote} with the exact text from the page. No URL and quote, no write. Never fill a gap from memory, an older patch, or your own working-out; keep the old value or write "not yet known".
- **B. Read twice.** WebFetch answers through a summariser that can misread. Fetch each source again with a different prompt asking for the exact printed text and compare. If they differ, read a third time; if still unclear, keep the old value and add the claim to `checks.flagged`. Count confirmed rows as `checks.verified`.
- **C. Independent check.** If the Agent tool is available, give a fresh general-purpose agent only the ledger (file, id, field, new, url) and ask it to open each URL and mark each row confirmed, wrong or can't tell, quoting the page. Fix or drop anything not confirmed. Without the Agent tool, do this pass yourself and say so in `checks.method`.
- **D. Two sources for game changes.** A patch change, datamine, date change or raid fact needs an official Blizzard source or two independent sites. One-source items go only in news and the digest, marked confidence "single"; keep them out of verdicts, facts, levelling and gear advice until confirmed.
- **E. Consistency sweep.** After changing any number, rank or band, search every text field in classes, specs, leveling, meta and dungeons for the old values (verdict body, headline, statsNote, opinion notes, spec summary, compare, facts, newNote) and rewrite every sentence that now disagrees. `scripts/check_data.py` then checks the structural rules; the page runs the same checks in its footer.
- **F. Sanity.** A day-on-day sim change above 10%, a band jump of two letters, a rank move of more than 5, or a moved date needs a third read and a digest item explaining it.
- **G. Correct, don't just add.** Fix any existing value you find to be wrong or out of date and list it in `checks.corrected`.

Plain English, British spelling, no em-dashes.
