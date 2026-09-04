# prepmyproperty.tech

The signup page. One HTML file, one server function, one database table.

```
web/
  index.html              the whole page: copy, form, success screen, privacy notice
  functions/api/submit.js runs on Cloudflare when the form is submitted
  schema.sql              the database table (already applied, kept for reference)
```

---

## Before it can go live

**One blocking item.** The privacy notice needs a postal address for the person
collecting the data. Both the California CPRA and the EU GDPR require it to be
shown before consent is taken, so this is not optional and not something to
guess at.

Open `index.html`, find `const CONTROLLER`, and fill in the three nulls:

```js
const CONTROLLER = {
  name:    "Julius Kasiske",
  street:  null,          // <- REQUIRED before launch
  city:    null,          // <- REQUIRED before launch
  country: null,          // <- REQUIRED before launch
  email:   "juliuskasiske@gmail.com"
};
```

Until they are filled in, the privacy notice shows a red warning in place of the
address, so the page cannot quietly go live looking complete when it is not.

---

## Deploying

The database already exists. It was created and the table verified with a real
insert and delete.

| | |
|---|---|
| Database name | `prepmyproperty` |
| Database ID | `2af1ccbb-2a3f-4553-8348-5edee9e5e21c` |
| Table | `submissions` |

### 1. Push to GitHub

The repo is `juliuskasiske/wildfire-preparedness`. This site lives in `web/`.

### 2. Create the Pages project

In the Cloudflare dashboard: **Workers & Pages → Create → Pages → Connect to Git**,
pick the repo, then set:

- **Build command**, leave empty. There is no build step.
- **Build output directory**: `web`
- **Root directory**: leave as `/`

Cloudflare finds `web/functions/` on its own and turns it into the `/api/submit`
endpoint.

### 3. Bind the database

**Settings → Bindings → Add → D1 database**

- Variable name: `DB` (exactly this, the function looks for `env.DB`)
- Database: `prepmyproperty`

Add it for **both** Production and Preview, then redeploy. A binding added
without a redeploy does not take effect, and the form will return
"storage not configured".

### 4. Point the domain

**Custom domains → Set up a custom domain →** `prepmyproperty.tech`.

The QR code on the flyer encodes `https://prepmyproperty.tech`, so that exact
hostname has to serve this page. Cloudflare issues the certificate itself.

---

## Reading the submissions

```sql
-- the work queue, oldest promise first
SELECT id, created_at, due_date, address, email, answers
FROM submissions WHERE status = 'new' ORDER BY due_date;

-- mark one as sent
UPDATE submissions SET status = 'sent', sent_at = datetime('now') WHERE id = ?;

-- someone asked to be deleted
DELETE FROM submissions WHERE email = ?;
```

`answers` is JSON, so you can query into it directly:

```sql
-- the headline number: what people say they would spend
SELECT json_extract(answers,'$.q5_budget_usd') AS usd, COUNT(*)
FROM submissions GROUP BY usd ORDER BY usd;

-- does feeling unprepared track with willingness to spend?
SELECT json_extract(answers,'$.q2_preparedness') AS prepared,
       ROUND(AVG(json_extract(answers,'$.q5_budget_usd'))) AS avg_usd,
       COUNT(*) AS n
FROM submissions GROUP BY prepared ORDER BY prepared;

-- why the unprepared have not acted (one row per reason given)
SELECT j.value AS barrier, COUNT(*) AS n
FROM submissions, json_each(json_extract(answers,'$.q3_barriers')) j
GROUP BY barrier ORDER BY n DESC;

-- what motivates those who did act, weighted by where they ranked it
SELECT j.value AS motive, COUNT(*) AS times_picked,
       ROUND(AVG(j.key + 1),2) AS avg_rank
FROM submissions, json_each(json_extract(answers,'$.q3_motivations')) j
GROUP BY motive ORDER BY avg_rank;
```

## The survey

Six questions on paper, five in practice: question 3 forks on the answer to
question 2, so nobody sees both halves.

| Key | Question | Shape |
|---|---|---|
| `q1_concern_change` | How concern has changed over two years | 1 to 5 |
| `q2_preparedness` | How ready the home is | 1 to 5 |
| `q3_motivations` | What drove the work, **asked when q2 is 4 or 5** | ranked list |
| `q3_barriers` | What stopped them, **asked when q2 is 1 to 3** | multi-select |
| `q4_interest` | Interest in doing more | 1 to 5 |
| `q5_budget_usd` | What they would spend | whole dollars |

`q3_branch` records which fork was asked, so an empty `q3_barriers` means
"not asked" rather than "asked and left blank". `q3_motivations` is order
carrying: position 0 is what they picked first.

To change the questions, edit the matching `<section class="step">` in
`index.html` and the `ALLOWED` lists in `functions/api/submit.js`. The server
only stores values that appear in those lists.

## Promises this code makes to the user

Worth knowing, because breaking them silently is the failure mode that matters.

- **Five days.** The success screen says the assessment arrives by today + 5,
  and `due_date` records the date actually promised. The server computes it, not
  the browser, so the date in the database is the one you are held to.
- **Consent is required.** A submission without `consent: true` is rejected and
  never stored. Consent is the legal basis for contacting anyone later.
- **24 months.** The privacy notice promises deletion after 24 months. Nothing
  enforces that yet. It needs a scheduled job before the first records age out.
- **No IP addresses.** Only country and browser string are kept, for spam
  triage. Do not add IP logging without updating the notice.
- **Answers are whitelisted.** The function only stores values that appear as
  options on the page, so a hand-rolled POST cannot write junk into the
  research data.
