from dataclasses import dataclass

from flask import current_app

from .domain import GestorPropostas
from .infra import StorageManager


@dataclass
class AppContext:
    gestor: GestorPropostas
    storage: StorageManager

    @classmethod
    def bootstrap(cls) -> "AppContext":
        gestor = GestorPropostas()
        storage = StorageManager()
        storage.init_db()
        storage.carregar_tudo(gestor)
        return cls(gestor=gestor, storage=storage)


def get_context() -> AppContext:
    return current_app.extensions["app_context"]
