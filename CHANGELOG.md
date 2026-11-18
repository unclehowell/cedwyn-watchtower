## Archive worker 1.0.7 — 18 Nov 2026

- Fixes an append-after-completion edge case. If a new batch of URLs is committed after the current week's archive cursor was marked complete, `?continue=1` now compares the live feed length with the existing cursor and resumes only the appended tail.
- Existing cursor position is preserved; earlier URLs are not replayed and saved status remains in KV. The existing 6-second pacing, 30-URL batch limit, 429 back-off, and three-refusal-per-host guard remain unchanged.
- This specifically allows the ten new party/institution targets in release 3.4.0 to be archived during the current ISO week without resetting the completed run.

## [3.4.0] - 2026-11-18

### Added
- Ten evidence-linked official targets for party/institution coverage: ADS Llandough archive landing page, Heneb institutional and HER-service pages, HM Land Registry, Glamorgan Archives D696 (Western Ground Rents), two NLW Bute/manorial catalogue pages, Companies House 00461464 (Ideal Homes Wales / Persimmon Homes (Wales)), NLW Watch and Listen item 507738, and Cardiff Castle's Bute-family context page.
- Added Archaeology Data Service as a distinct digital repository lead. Its landing-page capture status is not inferred from the separate associated PDF.
- Party cards now resolve the live Wayback worker's latest timestamp/error before falling back to the saved target snapshot, avoiding stale “uncaptured” labels where the weekly worker has since succeeded.

### Qualified gaps
- Direct current online pages for historical planning applications 89/01396/OUT and 92/00671/RES were not verified; no invented application URLs were added.
- No ITV/HTV-owned page for the 1988 Llandough footage was located. NLW item 507738 remains a separate catalogue lead; its page was not readable in this check.
- No exact relevant Mountjoy Ltd archive record was verified in this pass. Existing Companies House/TNA checks remain; unrelated businesses named Mountjoy are excluded.
- Historic England remains a comparator, not an established participant.
- Cardiff Castle's Bute-family page is contextual background only, not evidence that the Castle was a party to the property proceedings.

# Changelog

## [3.3.0] - 2026-11-10

### Added
- Judicial citation register for BP Properties Ltd v Buckler [1987] EWCA Civ 2, searched by case-name, neutral-citation and reported-citation variants rather than only property-name matches.
- Eleven primary-text-verified later judgments, each with pinpoint paragraphs and a treatment class: Good Challenger Navegante [2003] EWCA Civ 1668 (para 106, mentions); Colin Dawson Windows Ltd [2005] EWCA Civ 9 (paras 33, 38–40, distinguishes); Clowes Developments v Walters [2005] EWHC 669 (Ch) (paras 42, 44–45, applies); Batsford Estates v Taylor [2005] EWCA Civ 489 (para 22, mentions); Odey v Barber [2006] EWHC 3109 (Ch) (paras 72–75, cites); Roberts v Swangrove Estates [2007] EWHC 513 (Ch) (para 83, applies); Totton and Eling Town Council v Caunter [2008] EWHC 3630 (Ch) (paras 17–20, cites); Smart v London Borough of Lambeth [2013] EWCA Civ 1375 (paras 34–36, applies); Smith v Molyneaux [2016] UKPC 35 (paras 28–30, applies); Brown v Ridley [2024] UKUT 14 (LC) (paras 154–155, distinguishes / limits); and Kerridge v Hook [2025] UKFTT 1076 (PC) (para 33, cites).
- Added the twelve later judgment and case-text URLs to the weekly Wayback target feed. First captures are pending the next archive-worker cycle.
- Published machine-readable citation data at public/data/case-citations.json, with `scripts/validate_watchtower.py` run on every pull request.

### Corrected
- Brown v Ridley [2024] UKUT 14 (LC) is included, not excluded. An earlier draft of this release excluded it after a mirror search found no match; the official Find Case Law text lists the case among its authorities and holds at paragraph 155 that it "is not authority for the proposition that a registered proprietor can, in any case, put an end to adverse possession by the unilateral grant of a permission or licence to occupy the relevant land". The validator now requires an exclusion to record the full official text searched and every citation variant, and checks Brown v Ridley as a regression case.

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
