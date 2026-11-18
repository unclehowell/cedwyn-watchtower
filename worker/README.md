# Watchtower archive Worker

Source for Cloudflare Worker `bfe-watchtower-archive`.

- Entry point: `worker/index.js`
- Canonical target feed: `https://raw.githubusercontent.com/unclehowell/cedwyn-watchtower/main/public/data/targets.json`
- Bindings retained from production: Durable Object namespace `CLOCK` (class `Clock`) and KV namespace `WB`.
- Weekly pass: Sundays at 03:15 UTC, one URL at a time, 6-second pacing, 30 URLs per invocation, and bounded retry delays.
- Version 1.0.7: a guarded `?continue=1` resumes a completed current-week cursor only when the canonical target feed has grown beyond the saved cursor. It resumes at the old position and does not rewind or re-archive the earlier list.
- Version 1.0.8: each primary URL is attempted once per weekly pass at the existing six-second pace; a separate retry pass is queued for every URL that still has no successful capture timestamp. Three failures on one host no longer suppress attempts for its other URLs. `?retry=1` can queue the current week's failed URLs explicitly; the retry pass is once per week and remains bounded by the existing 30-URL runs and 429 back-off.
- Refusal guard: after three refusals for a host during a weekly pass, remaining URLs for that host are skipped for that week; 429 responses defer the run.

The source is versioned here so the deployed Worker no longer depends on the retired `unclehowell/cedwyn` repository. A deployment must preserve the existing `CLOCK` Durable Object and `WB` KV bindings. Do not clear either namespace during a code update.
