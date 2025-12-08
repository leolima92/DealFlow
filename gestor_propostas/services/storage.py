from typing import Optional

from .. import db
from ..models import Cliente, Proposta, ItemProposta


class StorageManager:
    """
    Helper para operações de persistência usando SQLAlchemy.
    """
    
    @classmethod
    def init_db(cls):
        """
        Mantido apenas por compatibilidade com a versão antiga.

        No modelo novo, quem cuida do schema é:
        - Flask-Migrate (migrations) ou
        - db.create_all() (se você quiser algo mais simples em ambiente local).
        """
        pass

    @classmethod
    def salvar_ou_atualizar_cliente(cls, cliente: Cliente) -> Cliente:
        """
        Salva ou atualiza um cliente via ORM.
        Se o cliente já está no banco, faz update; se não, faz insert.
        """
        db.session.add(cliente)
        db.session.commit()
        return cliente

    @classmethod
    def deletar_cliente(cls, cliente_id: int) -> bool:
        """
        Remove um cliente pelo ID.
        Se houver cascade configurado em Cliente.propostas, as propostas associadas
        também serão removidas.
        """
        cliente: Optional[Cliente] = Cliente.query.get(cliente_id)
        if not cliente:
            return False
        db.session.delete(cliente)
        db.session.commit()
        return True

    @classmethod
    def salvar_ou_atualizar_proposta(cls, proposta: Proposta) -> Proposta:
        """
        Salva ou atualiza uma proposta via ORM.
        Itens relacionados serão salvos automaticamente, desde que estejam
        em proposta.itens.
        """
        db.session.add(proposta)
        for item in proposta.itens:
            db.session.add(item)
        db.session.commit()
        return proposta

    @classmethod
    def sincronizar_itens_proposta(cls, proposta: Proposta) -> Proposta:
        db.session.add(proposta)
        for item in proposta.itens:
            db.session.add(item)
        db.session.commit()
        return proposta

    @classmethod
    def deletar_proposta(cls, proposta_id: int) -> bool:
        """
        Remove uma proposta (e seus itens, graças ao cascade no relacionamento).
        """
        proposta: Optional[Proposta] = Proposta.query.get(proposta_id)
        if not proposta:
            return False
        db.session.delete(proposta)
        db.session.commit()
        return True

    @classmethod
    def carregar_tudo(cls, *args, **kwargs):
        """
        Método legado da versão com GestorPropostas.

        No modelo novo, não faz mais sentido preencher um objeto gestor em memória,
        porque o ORM já faz toda a consulta direto no banco.

        Mantido como no-op para evitar quebra de import/chamada antiga.
        """
        return

    @classmethod
    def salvar_tudo(cls, *args, **kwargs):
        """
        Método legado da versão com GestorPropostas.

        Agora, a aplicação deve chamar salvar_ou_atualizar_cliente / proposta
        conforme altera os dados, em vez de "salvar tudo" de uma vez.

        Mantido como no-op apenas por compatibilidade.
        """
        return
