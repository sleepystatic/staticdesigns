from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from models import db, ContactSubmission
import re
import time
import threading
import resend

contact_bp = Blueprint('contact', __name__)

SPAM_URL_PATTERN = re.compile(r'https?://\S+', re.IGNORECASE)
SPAM_PHRASES = [
    'telegra.ph', 'bit.ly', 'tinyurl', 'click here', 'act now',
    'congratulations', 'you have been selected', 'lottery', 'winner',
    'casino', 'viagra', 'crypto', 'bitcoin', 'nft', 'forex',
    'make money', 'earn money', 'work from home', 'lamborghini',
]


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_spam(name, email, project_type, comments, honeypot, form_loaded_at):
    if honeypot:
        print(f"[SPAM] Honeypot filled: {honeypot}", flush=True)
        return True

    if form_loaded_at:
        try:
            elapsed = (time.time() * 1000 - float(form_loaded_at)) / 1000
            if elapsed < 3:
                print(f"[SPAM] Submitted too fast: {elapsed:.1f}s", flush=True)
                return True
        except (ValueError, TypeError):
            print("[SPAM] Invalid timestamp", flush=True)
            return True
    else:
        print("[SPAM] No timestamp (bot didn't run JS)", flush=True)
        return True

    combined = f"{name} {project_type} {comments}".lower()
    for phrase in SPAM_PHRASES:
        if phrase in combined:
            print(f"[SPAM] Blocked phrase: '{phrase}'", flush=True)
            return True

    url_count = len(SPAM_URL_PATTERN.findall(comments))
    if url_count > 2:
        print(f"[SPAM] Too many URLs in comments: {url_count}", flush=True)
        return True

    if comments.upper() == comments and len(comments) > 30:
        print(f"[SPAM] All-caps comments", flush=True)
        return True

    return False


@contact_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        website_url = request.form.get('website_url', '').strip()
        project_type = request.form.get('project_type', '').strip()
        budget = request.form.get('budget', '').strip()
        comments = request.form.get('comments', '').strip()
        honeypot = request.form.get('company_url', '').strip()
        form_loaded_at = request.form.get('form_loaded_at', '').strip()

        if is_spam(name, email, project_type, comments, honeypot, form_loaded_at):
            flash('Thank you for reaching out! We\'ll get back to you within 24 hours.', 'success')
            return redirect(url_for('contact.contact'))

        errors = []

        if not name:
            errors.append('Name is required')
        if not email:
            errors.append('Email is required')
        elif not is_valid_email(email):
            errors.append('Please enter a valid email address')
        if not project_type:
            errors.append('Project type is required')
        if not budget:
            errors.append('Budget is required')
        if not comments:
            errors.append('Additional comments are required')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('contact.html')

        try:
            submission = ContactSubmission(
                name=name,
                email=email,
                project_type=project_type,
                budget=budget,
                comments=comments
            )
            db.session.add(submission)
            db.session.commit()

            def send_email(api_key, sender, recipient, subject, body):
                try:
                    resend.api_key = api_key
                    resp = resend.Emails.send({
                        "from": sender,
                        "to": [recipient],
                        "subject": subject,
                        "text": body,
                    })
                    print(f"[MAIL] Resend success: {resp}", flush=True)
                except Exception as e:
                    print(f"[MAIL ERROR] {type(e).__name__}: {e}", flush=True)

            try:
                api_key = current_app.config.get('RESEND_API_KEY', '')
                sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@staticdesigns.dev')
                admin_email = current_app.config.get('ADMIN_EMAIL', 't.bryan.dev@gmail.com')

                print(f"[MAIL] Sending via Resend to {admin_email}", flush=True)

                body = f"""New contact form submission from Static Designs website:

Name: {name}
Email: {email}
Current Website: {website_url or 'Not provided'}
Project Type: {project_type}
Budget: {budget}

Comments:
{comments}

Submitted at: {submission.submitted_at}"""

                thread = threading.Thread(
                    target=send_email,
                    args=(
                        api_key,
                        sender,
                        admin_email,
                        f'New Contact Form Submission - {name}',
                        body,
                    )
                )
                thread.start()
            except Exception as e:
                print(f"[MAIL ERROR] Setup failed: {e}", flush=True)

            flash('Thank you for reaching out! We\'ll get back to you within 24 hours.', 'success')
            return redirect(url_for('contact.contact'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again or email us directly.', 'error')
            print(f"Database error: {str(e)}")

    return render_template('contact.html')
