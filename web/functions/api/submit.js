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

const ALLOWED = {
  q1:         ['insured_ok','insured_expensive','non_renewed','fair_plan','uninsured','unknown'],
  q2:         ['zone0_clear','vents','roof','windows','deck','gutters','none','unknown'],
  q3:         ['mulch','plants','firewood','furniture','fence','clear','unknown'],
  q4_vents:   ['listed','plain','unknown'],
  q4_windows: ['tempered','dual','single','unknown'],
  q5:         ['not_interested','under_5k','5_15k','15_40k','over_40k','depends'],
};

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  });

const isEmail = (s) =>
  typeof s === 'string' && s.length <= 254 && /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(s);

/** Keep only values we published as options, so a hand-rolled POST cannot
 *  write arbitrary strings into the research data. */
const clean = (value, allowed) => {
  const list = Array.isArray(value) ? value : [value];
  return list.filter((v) => allowed.includes(v));
};

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
  const answers = {
    q1:         clean(a.q1, ALLOWED.q1)[0] ?? null,
    q2:         clean(a.q2, ALLOWED.q2),
    q3:         clean(a.q3, ALLOWED.q3),
    q4_vents:   clean(a.q4_vents, ALLOWED.q4_vents)[0] ?? null,
    q4_windows: clean(a.q4_windows, ALLOWED.q4_windows)[0] ?? null,
    q5:         clean(a.q5, ALLOWED.q5)[0] ?? null,
  };

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
