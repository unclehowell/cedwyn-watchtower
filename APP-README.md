# watchtower.bucklerfamily.estate

Watchtower: dated changes to public institutional pages, archive records and later legal citations relevant to Great House Farm (Tŷ Mawr), Llandough and the wider Cedwyn / Leckwith research area.

- Pages tracked: property-name and case-citation discoveries, plus evidence-linked official pages for named land-chain entities, developers, public authorities, heritage bodies, archive custodians and broadcasters where an exact page has been verified. Similar place names are disambiguated; Llandough near Cowbridge, Treoes and Llanmaes are different places and excluded.
- Party coverage: `public/data/parties.json` maps role classes, evidence anchors, absence/search checks and exact Wayback target URLs. It distinguishes litigants, land-chain companies, developers, later corporate successors, public authorities, heritage bodies, custodians and broadcasters. A party card is a research map, not a finding of legal liability or universal participation in litigation.
- Method: outside-page discovery uses property-name variants, with a separate curated judicial-citation register. The judicial register is checked against primary judgment texts with pinpoint paragraphs and treatment classifications. It is not a comprehensive automatic legal citator. Known URLs are re-archived weekly; every capture and latest status is read from the Wayback feed and Worker status endpoint.
- Wayback archive worker source: `worker/index.js`; it reads the canonical `unclehowell/cedwyn-watchtower` main-branch feed. Bindings are Durable Object `CLOCK` and KV `WB`; deployments must preserve both namespaces.
- Release 3.4.0/3.4.1 (18 Nov 2026): nineteen official institutional, catalogue and search-index targets added across two passes. Includes the exact ADS Llandough archive landing page (separate from its associated PDF), Heneb, HMLR, D696, Bute/NLW records, Ideal Homes/Persimmon company history, ITV Archive and Wales Broadcast Archive institutional pages, Cardiff Council and Vale planning guidance. The two historic Vale application result pages and a direct relevant Mountjoy company/catalogue record remain unverified. Party cards use live Worker capture/error status. The archive Worker is v1.0.7 and resumes appended targets after a completed weekly cursor without replaying earlier URLs.
- Static site: Cloudflare Pages project `bucklerfamily-watchtower`, output `public/`, no build command. Production source repository: `unclehowell/cedwyn-watchtower`, branch `main`; Cloudflare Pages source was reconnected to this repository on 18 Nov 2026.

© Williams–Buckler family. All rights reserved. Licence: https://bucklerfamily.estate/licence/

— Sion's Tab agent
