from flask import Flask
from config import Config
from models import db
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from routes.main import main_bp
    from routes.contact import contact_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(contact_bp)

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
