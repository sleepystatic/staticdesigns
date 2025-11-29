from flask import Flask
from flask_mail import Mail
from config import Config
from models import db
import os

# Initialize extensions
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with app
    db.init_app(app)
    mail.init_app(app)

    # Register blueprints
    from routes.main import main_bp
    from routes.contact import contact_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(contact_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


# Create app instance for gunicorn
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)