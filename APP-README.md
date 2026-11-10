# watchtower.bucklerfamily.estate

Watchtower: dated changes to institutions' own web pages about Great House Farm (Tŷ Mawr), Llandough, from the Internet Archive
(Wayback Machine).

- Pages tracked: institution pages that name Great House Farm, Tŷ Mawr, the Llandough monastic cemetery and its excavations
  (1990, 1994), the Llandough Roman villa, BP v Buckler, or titles WA231076 / WA240304: Archwilio (HER), Coflein (RCAHMW),
  Museum Wales, Welsh Government / Cadw, Llandough Community Council, the Vale of Glamorgan Council, the National Library of
  Wales, the Church in Wales and others as they are found. Llandough near Cowbridge, Treoes and Llanmaes are different places
  and are excluded.
- Method: outside-page discovery uses property-name variants; additional known legal-citation sources for BP Properties Ltd v Buckler [1987] EWCA Civ 2 are added through a separate curated citation register. The judicial citation register is separately checked against primary judgment texts, with pinpoint paragraphs and treatment classifications. The static register is not a comprehensive automatic legal citator; new-case discovery requires a fresh search, while known URLs are re-archived weekly. Every Wayback capture of each monitored page is listed (CDX). Distinct captures are read and the passages about the farm or the
  site are compared capture to capture, narrowing each change down to two adjacent captures. Each change is one dot: page
  appeared, text added, text removed, text changed, or page gone, with links to the before and after captures.
- Landing page: one scatter graph (x = date, y = institution) and the full list of changes underneath.
- Release 3.0.1 adds keyboard-focus styling; data values unchanged. Data: `public/data/changes.json`. Re-checked daily at midday by `work/watchtower/v3/run_daily.py`.
- Release 3.3.0 (10 Nov 2026): adds a primary-text-verified judicial citation register for four later decisions (2005, 2008, 2013 and 2016), adds their source URLs to the weekly archive target feed, and explicitly excludes a checked 2024 candidate that does not cite Buckler. Data: `public/data/case-citations.json` and `public/data/targets.json`.
- Release 3.1.0 (2 Nov 2026): every outside page that cites one of the farm's names is listed in `public/data/targets.json` and saved to the Wayback Machine; the Worker `bfe-watchtower-archive` (Durable Object alarm, Sundays from 03:15 UTC) saves each again every week and serves the status at `/watchtower/api/wayback.json`; `public/wayback.js` shows page, name cited, first seen, latest capture and weekly status.
- Archive: the earlier "Raised & replies" layer (correspondence items) and the v2 page-change data are kept unpublished in
  `archive/` (outside `public/`, so the site does not serve them).
- Static site: Cloudflare Pages project bucklerfamily-watchtower, branch `watchtower`, output `public/`, no build step.

© Williams–Buckler family. All rights reserved. Licence: https://bucklerfamily.estate/licence/

— Sion's Tab agent
