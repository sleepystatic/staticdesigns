# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py

# Run with Flask CLI
flask run

# Production (gunicorn)
gunicorn app:app
```

There are no tests or linting configured in this project.

## Environment

Copy `.env` variables or set them manually. Required for full functionality:

- `DATABASE_URL` — PostgreSQL connection string; falls back to `sqlite:///static_designs.db` if absent
- `SECRET_KEY` — Flask session secret
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD` — SMTP config (currently Mailjet)
- `ADMIN_EMAIL` — receives contact form submissions

## Architecture

Flask app using the **application factory pattern** (`create_app()` in `app.py`). Two blueprints are registered:

- `routes/main.py` (`main_bp`) — static pages: home, portfolio, services, about
- `routes/contact.py` (`contact_bp`) — GET/POST `/contact` that validates the form, saves a `ContactSubmission` to the DB, and sends an email notification via Flask-Mail

`config.py` reads all config from environment variables. It patches `postgres://` → `postgresql://` for Render compatibility.

`models.py` defines one model: `ContactSubmission`. Tables are created on startup via `db.create_all()` inside the app context in `app.py`.

All templates extend `templates/base.html`, which provides the navbar, flash message display, footer, and JS/CSS includes.

**Portfolio projects are hardcoded in `routes/main.py`** (not database-driven) — edit the `projects` list there to add/remove/update entries. Each project needs a `name`, `url`, `image` (filename under `static/images/`), and `technologies` list.

The hero slideshow in `templates/index.html` has its own hardcoded image list managed in `static/js/main.js`.
