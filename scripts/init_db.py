import argparse
import os

from gestor_propostas.infra.auth import AuthManager, USERS_FILE
from gestor_propostas.infra import StorageManager


def main() -> None:
    parser = argparse.ArgumentParser(description="Inicializa o banco do DealFlow")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Remove o banco e os usuários antes de recriar as tabelas.",
    )
    args = parser.parse_args()

    storage = StorageManager()

    if args.reset:
        if os.path.exists(storage.db_path):
            os.remove(storage.db_path)
        if os.path.exists(USERS_FILE):
            os.remove(USERS_FILE)

    storage.init_db()
    AuthManager.ensure_default_admin()

    print("Banco inicializado. Usuário admin garantido.")


if __name__ == "__main__":
    main()
