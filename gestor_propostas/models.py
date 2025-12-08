from datetime import datetime, date
from . import db


class Cliente(db.Model):
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    documento = db.Column(db.String(50))
    contato = db.Column(db.String(200))

    propostas = db.relationship(
        "Proposta",
        back_populates="cliente",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __repr__(self):
        return f"<Cliente {self.id} - {self.nome}>"


class ItemProposta(db.Model):
    __tablename__ = "itens_proposta"

    id = db.Column(db.Integer, primary_key=True)
    proposta_id = db.Column(
        db.Integer,
        db.ForeignKey("propostas.id"),
        nullable=False
    )

    descricao = db.Column(db.String(255), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    valor_unitario = db.Column(db.Float, nullable=False, default=0.0)

    proposta = db.relationship("Proposta", back_populates="itens")

    @property
    def total(self) -> float:
        return self.quantidade * self.valor_unitario

    def __repr__(self):
        return (
            f"<ItemProposta {self.id} - {self.descricao} "
            f"Qtd={self.quantidade} Unit={self.valor_unitario}>"
        )


class Proposta(db.Model):
    __tablename__ = "propostas"

    STATUS_VALIDOS = ("rascunho", "enviada", "aceita", "recusada", "cancelada")

    id = db.Column(db.Integer, primary_key=True)

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id"),
        nullable=False
    )

    titulo = db.Column(db.String(200), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default="rascunho", nullable=False)

    validade = db.Column(db.Date, nullable=True)               
    responsavel = db.Column(db.String(200), nullable=True)
    condicoes_pagamento = db.Column(db.Text, nullable=True)
    
    tipo_desconto = db.Column(db.String(1), nullable=True)   
    desconto_percentual = db.Column(db.Float, default=0.0)
    desconto_valor = db.Column(db.Float, default=0.0)


    cliente = db.relationship("Cliente", back_populates="propostas")

    itens = db.relationship(
        "ItemProposta",
        back_populates="proposta",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def adicionar_item(self, descricao: str, quantidade: int, valor_unitario: float):
        item = ItemProposta(
            proposta=self,
            descricao=descricao,
            quantidade=quantidade,
            valor_unitario=valor_unitario,
        )
        db.session.add(item)

    def calcular_subtotal(self) -> float:
        return sum(item.total for item in self.itens)

    def definir_desconto_percentual(self, percentual: float):
        self.tipo_desconto = "%"
        self.desconto_percentual = max(0.0, percentual)
        self.desconto_valor = 0.0

    def definir_desconto_valor(self, valor: float):
        self.tipo_desconto = "R"
        self.desconto_valor = max(0.0, valor)
        self.desconto_percentual = 0.0

    def calcular_desconto(self) -> float:
        subtotal = self.calcular_subtotal()
        if self.tipo_desconto == "%":
            return subtotal * (self.desconto_percentual / 100.0)
        elif self.tipo_desconto == "R":
            return self.desconto_valor
        return 0.0

    def calcular_total(self) -> float:
        subtotal = self.calcular_subtotal()
        desconto = self.calcular_desconto()
        return max(0.0, subtotal - desconto)

    def alterar_status(self, novo_status: str):
        novo_status = (novo_status or "").lower()
        if novo_status not in self.STATUS_VALIDOS:
            raise ValueError(f"Status inválido: {novo_status}")
        self.status = novo_status

    def __repr__(self):
        return (
            f"<Proposta {self.id} - {self.titulo} "
            f"Cliente={self.cliente.nome if self.cliente else 'N/A'} "
            f"Status={self.status}>"
        )
