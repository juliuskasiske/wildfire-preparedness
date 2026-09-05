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

/* Address parsing, duplicated from index.html on purpose. The browser copy is
   there to give a useful message while typing; this copy is the one that
   decides, because a POST can come from anywhere. Two copies of forty lines
   beats adding a build step for one file.

   California only: we have no data anywhere else, so an out-of-state address
   is a report we cannot produce, not merely one we would rather not. */
const CA_ZIP_MIN = 90001, CA_ZIP_MAX = 96162;
const US_STATES = new Set(['AL','AK','AZ','AR','CO','CT','DE','FL','GA','HI','ID','IL','IN',
  'IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY',
  'NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']);

function parseAddress(raw) {
  const bad = (why) => ({ ok: false, why });
  const s = String(raw ?? '').trim().replace(/\s+/g, ' ');
  if (s.length < 8 || s.length > 300) return bad('bad address');

  const zipM = s.match(/\b(\d{5})(?:-\d{4})?\b(?![\s\S]*\b\d{5}\b)/);
  if (!zipM) return bad('no zip');
  const zip = Number(zipM[1]);

  let before = s.slice(0, zipM.index).replace(/[\s,]+$/, '');

  const stateM = before.match(/[\s,]((?:[A-Za-z]{2})|California|Calif\.?)\s*$/i);
  let stateAbbr = null;
  if (stateM) {
    const t = stateM[1].replace(/\./g, '').toUpperCase();
    if (t === 'CALIFORNIA' || t === 'CALIF' || t === 'CA') stateAbbr = 'CA';
    else if (US_STATES.has(t)) stateAbbr = t;
    if (stateAbbr) before = before.slice(0, stateM.index).replace(/[\s,]+$/, '');
  }
  if (stateAbbr && stateAbbr !== 'CA') return bad('outside california');
  if (zip < CA_ZIP_MIN || zip > CA_ZIP_MAX) return bad('outside california');

  const numM = before.match(/^(\d{1,6}[A-Za-z]?(?:\s?[-\u2013/]\s?\d{1,6}[A-Za-z]?)?)(?=[\s,])/);
  if (!numM) return bad('no house number');

  const rest = before.slice(numM[0].length).replace(/^[\s,]+/, '');
  if (!rest) return bad('no street or city');

  const parts = rest.split(',').map((x) => x.trim()).filter(Boolean);
  let street, city;
  if (parts.length >= 2) { street = parts[0]; city = parts.slice(1).join(', '); }
  else {
    const w = rest.split(' ').filter(Boolean);
    if (w.length < 3) return bad('no street or city');
    street = w.slice(0, w.length - 1).join(' ');
    city = w[w.length - 1];
  }
  const letters = (t) => (t.match(/[A-Za-z]/g) || []).length;
  if (letters(street) < 2 || letters(city) < 2) return bad('no street or city');

  return { ok: true, houseNumber: numM[1], street, city, state: 'CA', zip: String(zip).padStart(5, '0') };
}

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

  const addr = parseAddress(address);
  if (!addr.ok)       return json({ error: addr.why }, 400);
  if (!isEmail(email)) return json({ error: 'bad email' }, 400);

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
         (created_at, due_date, address, addr_parts, email, answers, consent,
          country, user_agent, status)
       VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, 'new')`
    ).bind(
      now.toISOString(),
      due,
      address,
      // The parsed pieces, so step two does not have to parse the string again.
      JSON.stringify({ house_number: addr.houseNumber, street: addr.street,
                       city: addr.city, state: addr.state, zip: addr.zip }),
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
