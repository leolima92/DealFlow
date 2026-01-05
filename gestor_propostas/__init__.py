import os
import logging
from flask import Flask

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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
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

    # importa e registra o blueprint da UI
    from .ui import bp as ui_bp
    app.register_blueprint(ui_bp)

    return app
