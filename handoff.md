# Static Designs — Session Handoff

This document is written for a fresh Claude Code session picking up work on the Static Designs website. It covers everything built so far, what's working, what's broken, and what to do next.

---

## 1. Project Summary

**Static Designs** is a freelance web development business run by Bryan. This is the business website itself — a Flask app deployed on **Render** that showcases portfolio work, services, a blog, and a contact form that doubles as a "Free Website Evaluation" lead funnel.

**Tech stack:** Python/Flask, Jinja2 templates, vanilla CSS/JS, SQLAlchemy (PostgreSQL in production, SQLite in dev), Flask-Mail (Mailgun SMTP), gunicorn for production.

**Live site:** `https://staticdesigns.dev` (deployed on Render)

**Current state:** The site went through a major visual revamp. All changes are local and uncommitted — Bryan handles all git operations himself. Do not commit or push unless he explicitly asks.

---

## 2. Repository Structure

```
staticDesigns/
├── app.py                  # App factory, creates Flask app + extensions
├── config.py               # All config from env vars (DB, mail, secrets)
├── models.py               # SQLAlchemy models (ContactSubmission)
├── requirements.txt        # Python dependencies
├── .env                    # Local env vars (DO NOT read/expose values)
├── .gitignore
├── CLAUDE.md               # Project instructions for Claude Code
├── server.log              # Dev server log (ignore)
│
├── routes/
│   ├── main.py             # Homepage, portfolio, services, about, blog routes
│   └── contact.py          # Contact form GET/POST, validation, email sending
│
├── static/
│   ├── css/style.css       # Single stylesheet (~1900+ lines, heavily modified)
│   ├── js/main.js          # Navbar toggle, hero slideshow, carousel, scroll
│   └── images/
│       ├── *-preview.jpg   # Portfolio project screenshots
│       ├── *-mobile.png    # Mobile mockup screenshots
│       ├── blog-custom-vs-builders.jpg  # Blog post thumbnail
│       ├── staticdesignslogo.png        # Site logo
│       ├── favicon-*.png / apple-touch-icon.png
│       └── logos/          # Client logo strip directory (EMPTY — waiting for PNGs)
│
├── templates/
│   ├── base.html           # Master template: navbar, footer, flash messages
│   ├── index.html          # Homepage with hero, trust stats, logo strip, services, portfolio carousel
│   ├── portfolio.html      # Portfolio grid page
│   ├── services.html       # Services/pricing page
│   ├── about.html          # About page
│   ├── contact.html        # "Free Website Evaluation" form page
│   ├── blog.html           # Blog listing page
│   ├── blogs.html          # (STALE — older version, unused, can be deleted)
│   └── blog/
│       └── why-custom-coded-websites-beat-wordpress.html  # First blog post
```

---

## 3. Architecture

### Application Factory Pattern

`app.py` defines `create_app()` which:
1. Creates the Flask app and loads `Config` from `config.py`
2. Initializes `db` (SQLAlchemy) and `mail` (Flask-Mail) with the app
3. Registers two blueprints: `main_bp` and `contact_bp`
4. Calls `db.create_all()` to ensure tables exist

The `mail` instance is created at module level (`mail = Mail()`) and initialized via `mail.init_app(app)`. The contact route imports it as `from app import mail`. This was a bug fix — previously, the contact route was creating a new `Mail(current_app)` instance on every POST, which caused SMTP connection timeouts and 502 errors on Render.

### Data Model

One model in `models.py`:

```python
class ContactSubmission(db.Model):
    id          = Integer, primary_key
    name        = String(100), required
    email       = String(120), required
    project_type = String(200), required
    budget      = String(50), required
    comments    = Text, required
    submitted_at = DateTime, default=utcnow
```

**IMPORTANT:** The contact form has a `website_url` field that is captured in the form, included in the email notification body, but is **NOT persisted to the database**. The `ContactSubmission` model lacks a `website_url` column. This needs to be added. See Known Issues below.

### Content Management (Hardcoded, Not Database-Driven)

Portfolio projects are hardcoded in `routes/main.py` in the `portfolio()` function — a list of dicts with `name`, `url`, `image`, `technologies`.

Blog posts are hardcoded in `routes/main.py` as the `BLOG_POSTS` list. Each entry has `slug`, `title`, `description`, `date`, `read_time`, `image`, `template`. The template file lives in `templates/blog/`. To add a new blog post: add an entry to `BLOG_POSTS` and create a matching template file.

The hero slideshow images are managed in `static/js/main.js`.

### Config (`config.py`)

All config comes from environment variables. Key detail: there's a `postgres://` → `postgresql://` patch for Render compatibility (Render provides `postgres://` but SQLAlchemy requires `postgresql://`).

Required env vars (names only, never include values):
- `DATABASE_URL` — PostgreSQL connection string (falls back to SQLite)
- `SECRET_KEY` — Flask session secret
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS` — SMTP settings
- `MAIL_USERNAME`, `MAIL_PASSWORD` — SMTP credentials
- `ADMIN_EMAIL` — receives contact form submissions (falls back to MAIL_USERNAME)

---

## 4. Key Flows

### Contact Form / Free Website Evaluation

1. User visits `/contact` → renders `contact.html` with the evaluation-framed form
2. User fills out: name, email, website_url (optional), project_type, budget, comments
3. POST to `/contact` → `routes/contact.py` validates all required fields
4. On success: saves `ContactSubmission` to DB (without website_url — see Known Issues)
5. Sends email notification via Flask-Mail to `ADMIN_EMAIL` (email body includes website_url)
6. Flashes success message, redirects back to `/contact`
7. On mail failure: logs the error but still saves to DB and shows success to user

### Blog System

1. `/blog` → `routes/main.py:blog()` → renders `blog.html` with `BLOG_POSTS` list
2. `/blog/<slug>` → looks up post by slug in `BLOG_POSTS`, renders the post's template file, 404 if not found
3. Blog post templates extend `base.html` and receive `post` context with title, date, etc.

### Hero Slideshow

Managed entirely in `static/js/main.js`. The browser mockup on the homepage cycles through portfolio screenshots with URL text changes. Indicator bars below the mockup show the active slide and are clickable.

---

## 5. Known Issues (Action Required)

### A. `website_url` Not Saved to Database (Bug)

The contact form collects a `website_url` field and includes it in the admin email, but the `ContactSubmission` model in `models.py` has no `website_url` column. The data is lost after the email is sent.

**Fix:** Add `website_url = db.Column(db.String(500), nullable=True)` to the `ContactSubmission` model, and pass `website_url=website_url` in the `ContactSubmission()` constructor call in `routes/contact.py` (line 50). If using PostgreSQL in production, you may need to run a migration or use `ALTER TABLE` directly since `db.create_all()` won't add columns to existing tables — it only creates missing tables.

### B. Contact Form 502 Fix Not Tested Live

The 502 Bad Gateway on the contact form POST was caused by creating a new `Mail()` instance per request. This was fixed by importing the app-level `mail` instance instead. Bryan confirmed it works locally but hasn't tested on the live Render deployment yet.

### C. Testimonials Section is Fabricated

The testimonials section in `templates/index.html` (lines 251-286) is **commented out** because the reviews are fabricated placeholder text with fake names. It should stay commented out until Bryan collects real testimonials from clients.

### D. Client Logo Strip — Empty Directory

`static/images/logos/` exists but contains no files. The homepage (`index.html` lines 63-72) references five logo PNGs:
- `mqbLogo.png` (Moore Quality Builders)
- `equallitieLogo.png` (Equalitie)
- `pfLogo.png` (Pixel Flip)
- `afLogo.png` (Amor Frames)
- `wwLogo.png` (new client)

Bryan said he'll provide these. Once dropped in, the logo strip will work — the HTML and CSS are already wired up. Logos display in grayscale and reveal full color on hover.

### E. Stale `templates/blogs.html` File

There is a `templates/blogs.html` file that appears to be an older/unused version. The active blog listing template is `templates/blog.html`. The stale file can be deleted.

---

## 6. What Works Well (Do Not Break)

These were iterated on and debugged carefully during the revamp:

- **Hamburger animation ("rotate collapse")**: The button rotates 90 degrees and the three lines morph into an X. The `transition` declaration on `.hamburger-line` must include `top` alongside `transform` and `opacity` — removing `top` from the transition causes the animation to glitch (lines snap instead of sliding). This was a debugging win; don't simplify the transition shorthand.

- **Hero gradient text**: `.gradient-accent` spans use `background-clip: text` with a gradient. The trust stat numbers also use gradient text. These rely on `-webkit-background-clip: text` for browser support.

- **CSS cascade order in style.css**: There are responsive breakpoint blocks near the end of the file (~line 1860+) that override `.hero-title`, `.section-title`, `.cta-title`, `.page-title` at `min-width: 768px`, and a separate `min-width: 1024px` block after that for `.hero-title { font-size: 5rem; }`. These MUST come after any earlier responsive rules for those selectors or they'll be overridden. A previous bug had the hero title stuck at 56px on desktop because a later 768px block was overriding the 1024px rule. The fix was specific ordering — don't reorganize these blocks without verifying cascade.

- **Contact form reframe**: The contact page is positioned as a "Free Website Evaluation" with a site audit angle. The left sidebar explains "What You'll Get" and "What Happens Next." The submit button still says "Send Message" and the CTA language throughout the site says "Get Your Free Website Evaluation." This framing is intentional for cold outreach.

- **Blog system**: Works end-to-end. The first post ("Why Custom-Coded Websites Beat WordPress...") has a CTA box at the bottom linking to the contact/evaluation page.

---

## 7. Environment & Deployment

### Local Development

```bash
pip install -r requirements.txt
python app.py
# Runs on http://localhost:5000 with debug=True
```

The `.claude/launch.json` is configured with a `flask-dev` server entry for the Claude Code Browser pane.

### Production (Render)

- Deployed via Render using `gunicorn app:app`
- PostgreSQL database provided by Render
- `DATABASE_URL` env var uses `postgres://` prefix which `config.py` patches to `postgresql://`
- SMTP configured via Mailgun (MAIL_SERVER, MAIL_PORT, etc. env vars on Render)
- `PORT` env var is set by Render; `app.py` reads it with fallback to 5000

### Important Render Detail

Render's free-tier PostgreSQL databases have limited retention. If the database is on a free plan, verify it hasn't expired or been wiped. `db.create_all()` will recreate the table structure on app startup, but existing data would be lost.

---

## 8. Suggested First Steps (Priority Order)

### Priority 1: Intro Video (Bryan's Next Focus)

Bryan is filming a ~90-second intro video based on a storyboard guide from this session. The storyboard covers:
1. Hook (0-10s): "Most web developers hand you a template. I don't."
2. The Problem (10-25s): Page builder limitations
3. The Difference (25-45s): Screen share of custom code + live site
4. Social Proof (45-55s): Client results / quick testimonials
5. The Offer (55-75s): Free website evaluation pitch
6. Call to Action (75-90s): Direct viewers to the site

**Next session tasks:**
- Help Bryan embed the finished video on the site (likely the About page or a new hero/intro section)
- Consider a lightbox or modal player, or an inline embed
- Optimize video for web (compress, consider hosting on a CDN or YouTube embed)

### Priority 2: Fix `website_url` Database Column

Add the column to `ContactSubmission` in `models.py` and update the constructor call in `routes/contact.py`. Handle the migration for the live PostgreSQL database.

### Priority 3: Test Contact Form on Live Site

After the mail fix is deployed, verify the contact form works end-to-end on `https://staticdesigns.dev/contact`. The fix changed the mail import from creating a new instance to using the app-level singleton.

### Priority 4: Drop Client Logo PNGs

When Bryan provides the logo files, drop them into `static/images/logos/` with the exact filenames referenced in `index.html`: `mqbLogo.png`, `equallitieLogo.png`, `pfLogo.png`, `afLogo.png`, `wwLogo.png`.

### Priority 5: Case Study Snippets

Bryan wants brief case study snippets on portfolio cards — a line or two about the business problem solved and the result. Not started yet; Bryan said "we'll implement case study snippets soon."

### Priority 6: More Blog Posts (SEO)

Only one blog post exists. Bryan's strategy is SEO-focused content to support cold outreach. Future post ideas could include topics around small business web presence, local SEO, website speed optimization, etc. Follow the same pattern: add to `BLOG_POSTS` in `routes/main.py`, create a template in `templates/blog/`.

### Priority 7: Real Testimonials

The testimonials section markup exists but is commented out with fake data. Once Bryan collects real reviews from clients, uncomment the section and replace the placeholder content.

---

## 9. Outstanding Questions (Need Bryan's Input)

- **Video hosting**: Will the intro video be self-hosted (in `static/`) or embedded from YouTube/Vimeo? YouTube embeds are easier to manage but add third-party dependencies.
- **Where does the video go?** About page, a new homepage section, or both?
- **Case study content**: Bryan needs to provide the actual client outcomes/metrics for case study snippets.
- **Logo files**: Bryan needs to provide the 5 PNG files for the client logo strip.
- **Live contact form test**: Has the latest code been deployed to Render and tested?

---

## 10. Working Preferences (Important for New Session)

- **Suggest-then-confirm workflow**: Always propose changes and get Bryan's approval before implementing. Don't go ahead with major changes silently.
- **No git operations**: Bryan handles all commits and pushes himself. Never commit, push, or create branches unless he explicitly asks.
- **Bryan's email is `t.bryan.dev@gmail.com`**: Use only for identification/attribution. Never send it to external services.
- **Keep it practical**: Bryan is building this business for cold outreach to local businesses. Features should support that sales angle — everything ties back to converting visitors into leads.
