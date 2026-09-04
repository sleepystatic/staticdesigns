from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from models import db, ContactSubmission
from flask_mail import Message
import re
import sys
import threading

contact_bp = Blueprint('contact', __name__)


def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@contact_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact form page with submission handling"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        website_url = request.form.get('website_url', '').strip()
        project_type = request.form.get('project_type', '').strip()
        budget = request.form.get('budget', '').strip()
        comments = request.form.get('comments', '').strip()

        # Validation
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
            # Save to database
            submission = ContactSubmission(
                name=name,
                email=email,
                project_type=project_type,
                budget=budget,
                comments=comments
            )
            db.session.add(submission)
            db.session.commit()

            def send_email(app, msg):
                with app.app_context():
                    try:
                        from app import mail
                        cfg = app.config
                        print(f"[MAIL DEBUG] server={cfg.get('MAIL_SERVER')}, port={cfg.get('MAIL_PORT')}, tls={cfg.get('MAIL_USE_TLS')}", flush=True)
                        print(f"[MAIL DEBUG] username={'SET' if cfg.get('MAIL_USERNAME') else 'NOT SET'}, password={'SET' if cfg.get('MAIL_PASSWORD') else 'NOT SET'}", flush=True)
                        print(f"[MAIL DEBUG] sender={cfg.get('MAIL_DEFAULT_SENDER')}, recipient={msg.recipients}", flush=True)
                        mail.send(msg)
                        print("[MAIL] Email sent successfully!", flush=True)
                    except Exception as e:
                        print(f"[MAIL ERROR] {type(e).__name__}: {e}", flush=True)
                        import traceback
                        traceback.print_exc()
                        sys.stderr.flush()

            try:
                admin_email = current_app.config.get('ADMIN_EMAIL')
                print(f"[MAIL] Preparing email to {admin_email}", flush=True)
                msg = Message(
                    subject=f'New Contact Form Submission - {name}',
                    recipients=[admin_email],
                    body=f"""
New contact form submission from Static Designs website:

Name: {name}
Email: {email}
Current Website: {website_url or 'Not provided'}
Project Type: {project_type}
Budget: {budget}

Comments:
{comments}

Submitted at: {submission.submitted_at}
                    """
                )
                thread = threading.Thread(
                    target=send_email,
                    args=(current_app._get_current_object(), msg)
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