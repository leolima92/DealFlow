import os

# pasta do pacote gestor_propostas
PKG_DIR = os.path.dirname(__file__)
# raiz do projeto (onde está app.py)
ROOT_DIR = os.path.dirname(PKG_DIR)

TEMPLATE_DIR = os.path.join(ROOT_DIR, "webapp", "templates")
STATIC_DIR = os.path.join(ROOT_DIR, "static")
