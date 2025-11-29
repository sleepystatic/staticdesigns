from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from models import db, ContactSubmission
from flask_mail import Message, Mail
import re

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

            # Send email notification
            try:
                # Create Mail instance with current app
                mail = Mail(current_app)

                msg = Message(
                    subject=f'New Contact Form Submission - {name}',
                    recipients=[current_app.config['ADMIN_EMAIL']],
                    body=f"""
New contact form submission from Static Designs website:

Name: {name}
Email: {email}
Project Type: {project_type}
Budget: {budget}

Comments:
{comments}

Submitted at: {submission.submitted_at}
                    """
                )
                mail.send(msg)
                print("Email sent successfully!")
            except Exception as e:
                # Log email error but don't fail the submission
                print(f"Email sending failed: {str(e)}")
                import traceback
                traceback.print_exc()

            flash('Thank you for reaching out! We\'ll get back to you within 24 hours.', 'success')
            return redirect(url_for('contact.contact'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again or email us directly.', 'error')
            print(f"Database error: {str(e)}")

    return render_template('contact.html')