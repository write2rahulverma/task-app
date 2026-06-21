import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

def create_app(config_name="default"):
    app = Flask(__name__)
    CORS(app)

    if config_name == "testing":
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")

    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        from . import models
        from .routes import tasks_bp, users_bp
        app.register_blueprint(tasks_bp, url_prefix="/api")
        app.register_blueprint(users_bp, url_prefix="/api")

    return app