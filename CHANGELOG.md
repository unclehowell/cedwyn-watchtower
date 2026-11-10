## [3.3.0] - 2026-11-10

### Added
- Judicial citation register for BP Properties Ltd v Buckler [1987] EWCA Civ 2, searched by case-name, neutral-citation and reported-citation variants rather than only property-name matches.
- Three primary-text-verified later judgments: Colin Dawson Windows Ltd [2005] EWCA Civ 9 (paras 33, 38–40); Totton and Eling Town Council v Caunter [2008] EWHC 3630 (Ch) (paras 17–20); and Smith v Molyneaux [2016] UKPC 35 (paras 28–30).
- Added the three later judgment URLs to the weekly Wayback target feed. First captures are pending the next archive-worker cycle.
- Published machine-readable citation data at public/data/case-citations.json.

### Corrected
- Excluded Brown v Ridley [2024] UKUT 14 (LC): the published judgment text contains no occurrence of “Buckler”, so it is not a citation to the 1987 case.

# Changelog

## [3.2.1] - 2026-11-03

### Fixed
- Peekaboo links in the "Peekaboo sources watched" rows open the matching Peekaboo card (`/peekaboo/#pk-…`).

## [3.2.0] - 2026-11-03

### Added
- Section "Peekaboo sources watched for later changes" (`#peekaboo-watch`): one row per Peekaboo incident with a stable anchor (`#wt-pkb-newman-ia`, `#wt-pkb-dbdt79`, `#wt-pkb-toc-f05`, `#wt-pkb-toc-f01`, `#wt-pkb-toc-f02`, `#wt-pkb-toc-f03`). The Internet Archive item page for Newman, Glamorgan (1995) is re-read every 5 days by the farm-page recapture, and a wording change becomes a new version of its local copy under `/wayback/websites/`. Data: `public/data/peekaboo-watch.json`.

## [3.1.2] - 2026-11-02

### Improved
- Weekly status in plain words ("the archive could not fetch it this week", "site unreachable this week", "archive busy, retrying") instead of a bare code.
- Where a page could not be fetched by the archive this week but an earlier Wayback capture exists, the row links that earlier capture and says so.

## [3.1.1] - 2026-11-02

### Fixed
- The Wayback section works after the site build routes every outside address in data files through `/wayback/go/`: rows, captures and the weekly status still match, and each outside page opens through `/wayback/go/` like the rest of the site.
- `data/targets.json` carries the first-pass captures saved so far (capture links are built from the timestamp); the weekly re-save now runs back to back from Sunday 03:15 UTC until the list is done.

## [3.1.0] - 2026-11-02

### Added
- New section "Outside pages citing the farm's names, saved to the Wayback Machine": 277 outside pages (216 from the farm list, 61 found by search on 2 Nov 2026 across the name variants), each with the name it cites, when it was first seen, its latest Wayback Machine capture and its weekly re-save status. Data: `public/data/targets.json`.
- Every page and this page's own files are submitted to the Internet Archive's Save Page Now; the Cloudflare Worker `bfe-watchtower-archive` saves them again every week (Sundays from 03:15 UTC) and publishes the status at `/watchtower/api/wayback.json`.

## [3.0.1] - 2026-10-24

### Improved
- Add a consistent, high-contrast keyboard-focus treatment for the institution filter, chart controls and page/capture links.
- Refresh the CSS cache key and tag the machine-readable change list with the release version.

### Validated
- The visible summary (9 points, 9 pages, 6 institutions) matches `changes.json`.
- All 9 change records have an after-capture link; the current change types are all `appeared`, so none requires a before link.
- Data snapshot generated 24 Oct 2026 13:23 UTC. These are archive observations, not proof that the institution’s underlying statements are true.
