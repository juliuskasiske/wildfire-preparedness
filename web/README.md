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
-- what people say a defence system is worth
SELECT json_extract(answers,'$.q5') AS worth, COUNT(*) FROM submissions GROUP BY worth;
```

---

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
