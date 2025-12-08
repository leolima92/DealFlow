from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    template_dir = os.path.join(root_dir, "webapp", "templates")
    static_dir = os.path.join(root_dir, "static")

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )

    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(base_dir, "gestor_propostas.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "trocar-depois"

    # init db
    db.init_app(app)
    migrate.init_app(app, db)

    # importar e registrar blueprints
    from .ui import bp as ui_bp
    from .auth import bp as auth_bp

    app.register_blueprint(ui_bp)
    app.register_blueprint(auth_bp)

    return app
