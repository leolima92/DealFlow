import argparse
import os

from gestor_propostas.auth import AuthManager, USERS_FILE
from gestor_propostas.services.storage import StorageManager


def main() -> None:
    parser = argparse.ArgumentParser(description="Inicializa o banco do DealFlow")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Remove o banco e os usuários antes de recriar as tabelas.",
    )
    args = parser.parse_args()

    if args.reset:
        if os.path.exists(StorageManager.DB_PATH):
            os.remove(StorageManager.DB_PATH)
        if os.path.exists(USERS_FILE):
            os.remove(USERS_FILE)

    StorageManager.init_db()
    AuthManager.ensure_default_admin()

    print("Banco inicializado. Usuário admin garantido.")


if __name__ == "__main__":
    main()
