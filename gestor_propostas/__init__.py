import logging
from logging.handlers import RotatingFileHandler
import os

from flask import Flask
from flask_wtf import CSRFProtect

from .models import GestorPropostas
from .services.storage import StorageManager

# === caminhos base ===
# pasta do pacote gestor_propostas
PKG_DIR = os.path.dirname(__file__)
# raiz do projeto (onde está app.py)
ROOT_DIR = os.path.dirname(PKG_DIR)

TEMPLATE_DIR = os.path.join(ROOT_DIR, "webapp", "templates")
STATIC_DIR = os.path.join(ROOT_DIR, "static")

# === configuração de logging ===
LOG_DIR = os.path.join(ROOT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

LOG_LEVEL = os.environ.get("DEALFLOW_LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding='utf-8'),
        logging.StreamHandler()  # também para console
    ]
)
logger = logging.getLogger(__name__)

# instância global do gestor (usada no ui.py)
gestor = GestorPropostas()
StorageManager.init_db()
StorageManager.carregar_tudo(gestor)


def create_app():
    # indica explicitamente onde estão templates e estáticos
    app = Flask(
        __name__,
        template_folder=TEMPLATE_DIR,
        static_folder=STATIC_DIR,
    )

    app.secret_key = os.environ.get(
        "DEALFLOW_SECRET_KEY",
        "troque-este-segredo-depois",
    )

    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE=os.environ.get("DEALFLOW_SESSION_SAMESITE", "Lax"),
        SESSION_COOKIE_SECURE=os.environ.get("DEALFLOW_SECURE_COOKIES", "").lower() in {"1", "true", "yes"},
    )

    CSRFProtect(app)

    # importa e registra o blueprint da UI
    from .ui import bp as ui_bp
    app.register_blueprint(ui_bp)
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    return app
