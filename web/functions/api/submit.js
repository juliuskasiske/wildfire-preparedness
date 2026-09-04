/**
 * POST /api/submit
 *
 * Cloudflare Pages Function. Runs on the same domain as the page, so the form
 * needs no CORS, no API key and no third party.
 *
 * Everything here re-validates what the browser already checked. The client
 * checks are there to be helpful; these are the ones that count, because a
 * form post can come from anywhere.
 *
 * Binding required: DB -> the D1 database (see schema.sql).
 */

const MAX_BODY = 8 * 1024;          // a legitimate submission is well under 2 KB

const LIKERT = ['1','2','3','4','5'];

const ALLOWED = {
  q3_motivations: ['keep_coverage','lower_premium','family','attachment','rules','peace'],
  q3_barriers:    ['too_expensive','never_got_round','dont_know_works','wont_happen',
                   'trust_fire','hoa','not_my_call','done_enough'],
  q3_branch:      ['motivations','barriers'],
};

const MAX_BUDGET = 100000000;   // $100M, a sanity ceiling not a real limit

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  });

const isEmail = (s) =>
  typeof s === 'string' && s.length <= 254 && /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(s);

export async function onRequestPost({ request, env }) {
  if (!env.DB) return json({ error: 'storage not configured' }, 500);

  // ---- read the body, with a hard ceiling -------------------------------
  const raw = await request.text();
  if (raw.length > MAX_BODY) return json({ error: 'too large' }, 413);

  let body;
  try { body = JSON.parse(raw); }
  catch { return json({ error: 'bad json' }, 400); }

  // ---- the two things we actually need ----------------------------------
  const address = String(body.address ?? '').trim();
  const email   = String(body.email ?? '').trim().toLowerCase();

  if (address.length < 8 || address.length > 300) return json({ error: 'bad address' }, 400);
  if (!isEmail(email))                            return json({ error: 'bad email' }, 400);

  // Consent is the legal basis for contacting them later. If it is not
  // explicitly true we do not store the record at all.
  if (body.consent !== true) return json({ error: 'consent required' }, 400);

  // ---- answers ----------------------------------------------------------
  const a = body.answers ?? {};

  // 1 to 5 scales. Stored as integers so they can be averaged without parsing.
  const likert = (v) => (LIKERT.includes(String(v)) ? Number(v) : null);

  // Ranking is order-carrying, so dedupe while preserving the order tapped.
  const ranked = (v, allowed) => {
    if (!Array.isArray(v)) return [];
    const seen = new Set();
    return v.filter((x) => allowed.includes(x) && !seen.has(x) && seen.add(x));
  };

  // The page always sends a number here, so anything out of range is a
  // hand-rolled POST. Rejecting keeps every stored row fully answered rather
  // than leaving nulls that read as "declined to say".
  const budget = Number(a.q5_budget_usd);
  const budgetOk = Number.isFinite(budget) && budget >= 0 && budget <= MAX_BUDGET;

  const branch = ALLOWED.q3_branch.includes(a.q3_branch) ? a.q3_branch : null;

  const answers = {
    q1_concern_change: likert(a.q1_concern_change),
    q2_preparedness:   likert(a.q2_preparedness),
    q4_interest:       likert(a.q4_interest),
    q5_budget_usd:     budgetOk ? Math.round(budget) : null,
    q3_branch:         branch,
    // Only the branch that was actually asked is stored, so an empty array
    // means "not asked" rather than "asked and left blank".
    q3_motivations: branch === 'motivations' ? ranked(a.q3_motivations, ALLOWED.q3_motivations) : [],
    q3_barriers:    branch === 'barriers'
      ? ranked(a.q3_barriers, ALLOWED.q3_barriers) : [],
  };

  // The three scales and the branch are the spine of the research set. A row
  // missing any of them is not worth storing.
  if (answers.q1_concern_change === null ||
      answers.q2_preparedness === null ||
      answers.q4_interest === null ||
      answers.q3_branch === null ||
      !budgetOk) {
    return json({ error: 'incomplete answers' }, 400);
  }

  // ---- the promise made on the success screen ---------------------------
  // Computed here, not taken from the client, so the date in the database is
  // the date we are actually held to.
  const now = new Date();
  const due = new Date(now.getTime() + 5 * 86400 * 1000).toISOString().slice(0, 10);

  // Coarse request context. Country and user agent only, for spam triage.
  // No IP address is stored: it is not needed, and not storing it is one less
  // thing to explain in the privacy notice.
  const country = request.headers.get('CF-IPCountry') ?? null;
  const ua      = (request.headers.get('User-Agent') ?? '').slice(0, 300);

  try {
    await env.DB.prepare(
      `INSERT INTO submissions
         (created_at, due_date, address, email, answers, consent, country, user_agent, status)
       VALUES (?, ?, ?, ?, ?, 1, ?, ?, 'new')`
    ).bind(
      now.toISOString(),
      due,
      address,
      email,
      JSON.stringify(answers),
      country,
      ua
    ).run();
  } catch (e) {
    // Never leak the database error to the page.
    console.error('insert failed', e);
    return json({ error: 'could not save' }, 500);
  }

  return json({ ok: true, due });
}

/** Anything other than POST on this path. */
export async function onRequest({ request }) {
  if (request.method === 'POST') return; // handled above
  return json({ error: 'method not allowed' }, 405);
}
