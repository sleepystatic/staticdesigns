from flask import Flask
from config import Config
from models import db
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Register blueprints
    from routes.main import main_bp
    from routes.contact import contact_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(contact_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)