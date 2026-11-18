// bfe-watchtower-archive v1.0.2 — target feed is read from the canonical cedwyn-watchtower repository.
// bfe-watchtower-archive — weekly Wayback Machine (Save Page Now) backup of every outside page watchtower tracks.
// Clock: a Durable Object alarm (no cron slot needed; the free plan's 5 cron triggers are all in use). The alarm fires
// Sundays 03:15 UTC and then a new run 2 minutes after each run ends until the week's list is done. Each run takes the next batch of targets for this ISO week from
// targets.json in the canonical cedwyn-watchtower repository, asks web.archive.org/save/<url> once per page (one at a time, paced),
// and records capture time / status in KV. GET /watchtower/api/wayback.json serves the status. No other writes anywhere.
// — Sion's Tab agent
const TARGETS = 'https://raw.githubusercontent.com/unclehowell/cedwyn-watchtower/main/public/data/targets.json';
const UA = "Mozilla/5.0 (compatible; watchtower-archiver; +https://bucklerfamily.estate/watchtower/)";
import { DurableObject } from 'cloudflare:workers';
const PER_RUN = 30, BUDGET_MS = 11 * 60 * 1000, PACE_MS = 6000, VERSION = '1.0.8';
function isoWeek(d) { const t = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate())); const day = t.getUTCDay() || 7;
  t.setUTCDate(t.getUTCDate() + 4 - day); const y0 = new Date(Date.UTC(t.getUTCFullYear(), 0, 1));
  return t.getUTCFullYear() + '-W' + String(Math.ceil(((t - y0) / 86400000 + 1) / 7)).padStart(2, '0'); }
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function spn(u) {
  const t0 = Date.now(); const r = { at: new Date().toISOString().slice(0, 19) + 'Z' };
  try {
    const x = await fetch('https://web.archive.org/save/' + u, { redirect: 'manual', headers: { 'User-Agent': UA }, signal: AbortSignal.timeout(100000) });
    r.code = x.status; const loc = x.headers.get('location') || x.headers.get('content-location') || '';
    const m = loc.match(/\/web\/(\d{14})\//); if (m) { r.ok = true; r.ts = m[1]; }
    try { await x.body?.cancel(); } catch (e) {}
  } catch (e) { r.code = 'err ' + (e && e.name || 'fetch'); }
  r.s = Math.round((Date.now() - t0) / 100) / 10; return r;
}
function retryCandidates(urls, status, week) {
  return urls.filter((u) => {
    const p = (status.pages || {})[u] || {};
    const code = String(p.code || '');
    return !p.ts && p.week === week &&
      (p.skipped || code === '520' || code === '523' || code === '429' || code.startsWith('err'));
  });
}
async function run(env, why) {
  const t0 = Date.now(), now = new Date(), week = isoWeek(now);
  const st = (await env.WB.get('status', 'json')) || { pages: {}, runs: [] };
  const cur = (await env.WB.get('cursor', 'json')) || {};
  if (cur.week !== week) {
    cur.week = week; cur.i = 0; cur.started = now.toISOString(); cur.done = null;
    cur.retry_urls = []; cur.retry_i = 0; cur.retry_active = false; cur.retry_done_week = null;
  }
  let primary = [];
  try {
    const r = await fetch(TARGETS + '?v=' + Date.now(), { headers: { 'User-Agent': UA } });
    const j = await r.json();
    primary = j.order || (j.targets || j).map(x => x.u || x);
  } catch (e) {
    st.runs.unshift({ at: now.toISOString(), why, week, error: 'target list unreadable' });
    st.runs = st.runs.slice(0, 30);
    await env.WB.put('status', JSON.stringify(st));
    return false;
  }
  const retryActive = cur.retry_active === true && cur.retry_week === week && Array.isArray(cur.retry_urls);
  const list = retryActive ? cur.retry_urls : primary;
  let pos = retryActive ? (cur.retry_i || 0) : (cur.i || 0);
  if (!retryActive && cur.done && pos >= primary.length && cur.retry_done_week === week) return true;
  let n = 0, ok = 0, rate = false;
  while (pos < list.length && n < PER_RUN && Date.now() - t0 < BUDGET_MS) {
    const u = list[pos];
    const r = await spn(u); n++;
    if (r.code === 429) { rate = true; break; }
    const p = st.pages[u] || {};
    p.last_try = r.at; p.code = r.code; p.week = week; delete p.skipped;
    if (r.ok) { p.ts = r.ts; p.ok_at = r.at; ok++; }
    st.pages[u] = p;
    pos++;
    if (retryActive) cur.retry_i = pos;
    else cur.i = pos;
    await sleep(PACE_MS);
  }
  let retryQueued = false;
  if (retryActive) {
    if (pos >= list.length) {
      cur.retry_active = false;
      cur.retry_done_week = week;
      cur.retry_completed = new Date().toISOString();
      cur.done = cur.main_completed || new Date().toISOString();
    }
  } else if (pos >= primary.length) {
    if (cur.retry_done_week !== week) {
      const failed = retryCandidates(primary, st, week);
      if (failed.length) {
        cur.retry_urls = failed;
        cur.retry_i = 0;
        cur.retry_week = week;
        cur.retry_active = true;
        cur.done = null;
        retryQueued = true;
      } else {
        cur.done = new Date().toISOString();
        cur.retry_done_week = week;
      }
      cur.main_completed = new Date().toISOString();
    } else {
      cur.done = cur.main_completed || new Date().toISOString();
    }
  } else {
    cur.done = null;
  }
  const finished = retryActive ? pos >= list.length : (pos >= primary.length && !retryQueued && cur.retry_done_week === week);
  const position = retryActive ? cur.retry_i : cur.i;
  const total = retryActive ? list.length : primary.length;
  st.runs.unshift({ at: now.toISOString(), why, week, pass: retryActive ? 'retry' : 'primary', tried: n, ok, rate_limited: rate, position, of: total, retry_queued: retryQueued });
  st.runs = st.runs.slice(0, 30);
  st.week = week;
  st.week_progress = {
    done: cur.i || 0,
    of: primary.length,
    finished: finished ? (cur.done || new Date().toISOString()) : null,
    retry: { done: cur.retry_i || 0, of: (cur.retry_urls || []).length, queued: cur.retry_active === true, finished: cur.retry_completed || null }
  };
  st.updated = new Date().toISOString(); st.version = VERSION;
  await env.WB.put('status', JSON.stringify(st));
  await env.WB.put('cursor', JSON.stringify(cur));
  return { finished, rate, retry_queued: retryQueued };
}
const H = { 'content-type': 'application/json; charset=utf-8', 'access-control-allow-origin': '*', 'cache-control': 'public, max-age=300' };
function nextSunday(now) {               // next Sunday 03:15 UTC strictly after now
  const d = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), 3, 15));
  d.setUTCDate(d.getUTCDate() + ((7 - d.getUTCDay()) % 7)); if (d <= now) d.setUTCDate(d.getUTCDate() + 7); return d;
}
export class Clock extends DurableObject {
  async alarm() {
    const r = await run(this.env, 'weekly alarm'); const finished = r === true || (r && r.finished);
    const now = new Date();                 // archive busy (429): wait 15 minutes; otherwise the next run 2 minutes after this one
    await this.ctx.storage.setAlarm(finished ? nextSunday(now).getTime() : now.getTime() + ((r && r.rate) ? 15 : 2) * 60 * 1000);
  }
  async fetch(req) {
    const u = new URL(req.url); let a = await this.ctx.storage.getAlarm();
    if (a === null) { a = nextSunday(new Date()).getTime(); await this.ctx.storage.setAlarm(a); }
    const week = isoWeek(new Date());
    if (u.searchParams.get('start') === '1') {
      const cur = (await this.env.WB.get('cursor', 'json')) || {};
      if (cur.week !== week) { a = Date.now() + 5000; await this.ctx.storage.setAlarm(a); }
    }
    let continuationQueued = false, continuationReason = null, currentTargetCount = null;
    let retryQueued = false, retryCount = 0;
    if (u.searchParams.get('continue') === '1') {
      const cur = (await this.env.WB.get('cursor', 'json')) || {};
      if (cur.week === week && Number.isInteger(cur.i)) {
        try {
          const r = await fetch(TARGETS + '?v=' + Date.now(), { headers: { 'User-Agent': UA } });
          const j = await r.json();
          const list = j.order || (j.targets || j).map(x => x.u || x);
          currentTargetCount = list.length;
        } catch (e) {}
        const retryPending = cur.retry_active === true && Array.isArray(cur.retry_urls) && (cur.retry_i || 0) < cur.retry_urls.length;
        const appendedTargets = Number.isInteger(currentTargetCount) && cur.i < currentTargetCount;
        if (!cur.done || appendedTargets || retryPending) {
          if (cur.done && appendedTargets) { cur.done = null; await this.env.WB.put('cursor', JSON.stringify(cur)); }
          a = Date.now() + 5000; await this.ctx.storage.setAlarm(a);
          continuationQueued = true;
          continuationReason = retryPending ? 'resume queued retry pass' : (appendedTargets ? 'new targets appended after the previous weekly pass' : 'resume incomplete weekly pass');
        }
      }
    }
    if (u.searchParams.get('retry') === '1') {
      const cur = (await this.env.WB.get('cursor', 'json')) || {};
      const st = (await this.env.WB.get('status', 'json')) || { pages: {} };
      let primary = [];
      try {
        const r = await fetch(TARGETS + '?v=' + Date.now(), { headers: { 'User-Agent': UA } });
        const j = await r.json();
        primary = j.order || (j.targets || j).map(x => x.u || x);
      } catch (e) {}
      if (primary.length) {
        if (cur.week !== week) { cur.week = week; cur.i = primary.length; cur.started = cur.started || new Date().toISOString(); }
        if (cur.retry_active === true && cur.retry_week === week) {
          retryQueued = true; retryCount = (cur.retry_urls || []).length;
        } else {
          const failed = retryCandidates(primary, st, week);
          retryCount = failed.length;
          if (failed.length) {
            cur.retry_urls = failed; cur.retry_i = 0; cur.retry_week = week;
            cur.retry_active = true; cur.retry_done_week = null; cur.done = null;
            await this.env.WB.put('cursor', JSON.stringify(cur));
            a = Date.now() + 5000; await this.ctx.storage.setAlarm(a);
            retryQueued = true;
          }
        }
      }
    }
    const out = { next_run: new Date(a).toISOString(), continuation_queued: continuationQueued, continuation_reason: continuationReason, current_target_count: currentTargetCount, retry_queued: retryQueued, retry_count: retryCount };
    if (u.searchParams.get('selftest') === '1') {
      const last = (await this.ctx.storage.get('selftest')) || 0;
      if (Date.now() - last > 3600000) { await this.ctx.storage.put('selftest', Date.now()); out.selftest = await spn('https://bucklerfamily.estate/watchtower/'); }
      else out.selftest = 'skipped: ran within the last hour';
    }
    return new Response(JSON.stringify(out), { headers: H });
  }
}
export default {
  async fetch(req, env) {
    const u = new URL(req.url);
    if (u.pathname.endsWith('/api/wayback.json')) {
      // Trigger paths use the Durable Object as the only authority for scheduling.
      // Preserve the existing status JSON shape and add an explicit trigger result,
      // so an HTTP 200 can never be mistaken for a successfully queued continuation.
      let trigger = null, trigger_error = null;
      const requested = u.searchParams.get('start') === '1' || u.searchParams.get('continue') === '1' || u.searchParams.get('retry') === '1';
      if (requested && env.CLOCK) {
        try {
          const r = await env.CLOCK.get(env.CLOCK.idFromName('main')).fetch(req.url);
          trigger = await r.json();
        } catch (e) { trigger_error = String(e && e.message || e); }
      }
      const raw = (await env.WB.get('status')) || '{"pages":{},"runs":[]}';
      let data;
      try { data = JSON.parse(raw); } catch (e) { data = { pages: {}, runs: [], parse_error: true }; }
      if (requested) {
        data.trigger = trigger;
        if (trigger_error) data.trigger_error = trigger_error;
        data.trigger_requested = true;
      }
      return new Response(JSON.stringify(data), { headers: requested ? Object.assign({}, H, {'cache-control':'no-store'}) : H });
    }
    if (u.pathname.endsWith('/api/wayback/about.json') || u.pathname.endsWith('/api/wayback/arm')) {
      const c = env.CLOCK ? await (await env.CLOCK.get(env.CLOCK.idFromName('main')).fetch(req.url)).json() : {};
      return new Response(JSON.stringify(Object.assign({ worker: 'bfe-watchtower-archive', version: VERSION, schedule: 'weekly: Sundays from 03:15 UTC, one page at a time, runs back to back, ' + PER_RUN + ' pages per run; failed targets receive one separate paced retry pass', targets: TARGETS, method: 'web.archive.org/save/<url>, one page at a time' }, c)), { headers: H });
    }
    return new Response('Not found', { status: 404 });
  }
};
