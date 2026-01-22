from __future__ import annotations

from .storage import StorageManager
from ..domain import Cliente, Proposta, TemplateProposta


class ClienteRepository:
    def __init__(self, storage: StorageManager):
        self._storage = storage

    def salvar(self, cliente: Cliente) -> None:
        self._storage.salvar_ou_atualizar_cliente(cliente)


class PropostaRepository:
    def __init__(self, storage: StorageManager):
        self._storage = storage

    def salvar(self, proposta: Proposta) -> None:
        self._storage.salvar_ou_atualizar_proposta(proposta)

    def sincronizar_itens(self, proposta: Proposta) -> None:
        self._storage.sincronizar_itens_proposta(proposta)

    def excluir(self, proposta_id: int) -> None:
        if hasattr(self._storage, "excluir_proposta"):
            self._storage.excluir_proposta(proposta_id)
        else:
            self._storage.deletar_proposta(proposta_id)


class TemplateRepository:
    def __init__(self, storage: StorageManager):
        self._storage = storage

    def salvar(self, template: TemplateProposta) -> None:
        self._storage.salvar_ou_atualizar_template(template)

    def excluir(self, template_id: int) -> None:
        self._storage.deletar_template(template_id)
