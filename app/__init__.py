from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "change-this-in-production"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tcg.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access the scanner."
    login_manager.login_message_category = "info"

    from app.blueprints.auth import auth_bp
    from app.blueprints.scan import scan_bp
    from app.blueprints.library import library_bp
    from app.blueprints.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(scan_bp, url_prefix="/scan")
    app.register_blueprint(library_bp, url_prefix="/library")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.route("/")
    def index():
        return redirect(url_for("scan.scanner"))

    with app.app_context():
        db.create_all()

    return app
