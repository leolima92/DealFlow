from datetime import datetime
from typing import List, Optional

from .policies import StatusPolicy
from .value_objects import Desconto

class Cliente:
    _contador_id = 1

    def __init__(self, nome: str, documento: str = "", contato: str = ""):
        self.id = Cliente._contador_id
        Cliente._contador_id += 1

        self.nome = nome
        self.documento = documento
        self.contato = contato

    def __str__(self) -> str:
        doc = f" | Doc: {self.documento}" if self.documento else ""
        contato = f" | Contato: {self.contato}" if self.contato else ""
        return f"({self.id}) {self.nome}{doc}{contato}"


class ItemProposta:
    def __init__(self, descricao: str, quantidade: int, valor_unitario: float):
        self.descricao = descricao
        self.quantidade = quantidade
        self.valor_unitario = valor_unitario

    @property
    def total(self) -> float:
        return self.quantidade * self.valor_unitario

    def __str__(self) -> str:
        return (
            f"{self.descricao} | Qtd: {self.quantidade} | "
            f"Unit: R$ {self.valor_unitario:.2f} | Total: R$ {self.total:.2f}"
        )


class TemplateProposta:
    _contador_id = 1

    def __init__(
        self,
        nome: str,
        titulo_padrao: str = "",
        responsavel_padrao: str = "",
        condicoes_pagamento_padrao: str = "",
        intro_texto: str = "",
        termos: str = "",
        rodape: str = "",
        cor_primaria: str = "#1f4e79",
        usar_logo: bool = True,
        logo_path: str = "static/img/dealflow_logo.png",
    ):
        self.id = TemplateProposta._contador_id
        TemplateProposta._contador_id += 1

        self.nome = nome
        self.titulo_padrao = titulo_padrao
        self.responsavel_padrao = responsavel_padrao
        self.condicoes_pagamento_padrao = condicoes_pagamento_padrao
        self.intro_texto = intro_texto
        self.termos = termos
        self.rodape = rodape
        self.cor_primaria = cor_primaria
        self.usar_logo = usar_logo
        self.logo_path = logo_path

    def __str__(self) -> str:
        return f"({self.id}) {self.nome}"


class Proposta:
    _contador_id = 1
    STATUS_VALIDOS = list(StatusPolicy.VALID_STATUSES)

    def __init__(
        self,
        cliente: Cliente,
        titulo: str = "",
        validade=None,       
        responsavel: str = "",
        condicoes_pagamento: str = "",
        template_id: Optional[int] = None,
    ):
        self.id = Proposta._contador_id
        Proposta._contador_id += 1

        self.cliente = cliente
        self.titulo = titulo or f"Proposta {self.id}"
        self.data_criacao = datetime.now()
        self.status = "rascunho"
        self.itens: List[ItemProposta] = []
        self.validade = validade         
        self.responsavel = responsavel
        self.condicoes_pagamento = condicoes_pagamento
        self.template_id = template_id

        self.tipo_desconto = None
        self.desconto_percentual = 0.0
        self.desconto_valor = 0.0
        self._desconto = Desconto.nenhum()
        self._sincronizar_desconto()

    def adicionar_item(self, item: ItemProposta):
        self.itens.append(item)

    def calcular_subtotal(self) -> float:
        return sum(item.total for item in self.itens)

    def definir_desconto_percentual(self, percentual: float):
        self._set_desconto(Desconto.percentual(percentual))

    def definir_desconto_valor(self, valor: float):
        self._set_desconto(Desconto.valor(valor))

    def remover_desconto(self):
        self._set_desconto(Desconto.nenhum())

    def calcular_desconto(self) -> float:
        subtotal = self.calcular_subtotal()
        return self._desconto.calcular(subtotal)

    def calcular_total(self) -> float:
        subtotal = self.calcular_subtotal()
        desconto = self.calcular_desconto()
        return max(0.0, subtotal - desconto)

    def alterar_status(self, novo_status: str):
        self.status = StatusPolicy.ensure_valid(novo_status)

    def carregar_desconto_dos_campos(self):
        self._desconto = Desconto.from_db_fields(
            self.tipo_desconto,
            self.desconto_percentual,
            self.desconto_valor,
        )
        self._sincronizar_desconto()

    def _set_desconto(self, desconto: Desconto):
        self._desconto = desconto
        self._sincronizar_desconto()

    def _sincronizar_desconto(self):
        self.tipo_desconto, self.desconto_percentual, self.desconto_valor = self._desconto.as_db_fields()

    def __str__(self) -> str:
        subtotal = self.calcular_subtotal()
        total = self.calcular_total()
        return (
            f"#{self.id} - {self.titulo} | Cliente: {self.cliente.nome} | "
            f"Status: {self.status} | Itens: {len(self.itens)} | "
            f"Subtotal: R$ {subtotal:.2f} | Total: R$ {total:.2f}"
        )


class GestorPropostas:
    def __init__(self):
        self.clientes: List[Cliente] = []
        self.propostas: List[Proposta] = []
        self.templates: List[TemplateProposta] = []

    def criar_cliente(self, nome: str, documento: str = "", contato: str = "") -> Cliente:
        cliente = Cliente(nome, documento, contato)
        self.clientes.append(cliente)
        return cliente

    def listar_clientes(self) -> List[Cliente]:
        return self.clientes

    def obter_cliente_por_indice(self, indice: int) -> Optional[Cliente]:
        if 0 <= indice < len(self.clientes):
            return self.clientes[indice]
        return None

    # ---- Propostas ---- #

    def criar_proposta(
        self,
        cliente: Cliente,
        titulo: str = "",
        validade=None,
        responsavel: str = "",
        condicoes_pagamento: str = "",
        template_id: Optional[int] = None,
    ) -> Proposta:
        proposta = Proposta(
            cliente,
            titulo,
            validade=validade,
            responsavel=responsavel,
            condicoes_pagamento=condicoes_pagamento,
            template_id=template_id,
        )
        self.propostas.append(proposta)
        return proposta

    def listar_propostas(self) -> List[Proposta]:
        return self.propostas

    def obter_proposta_por_indice(self, indice: int) -> Optional[Proposta]:
        if 0 <= indice < len(self.propostas):
            return self.propostas[indice]
        return None

    # ---- Templates ---- #

    def criar_template(
        self,
        nome: str,
        titulo_padrao: str = "",
        responsavel_padrao: str = "",
        condicoes_pagamento_padrao: str = "",
        intro_texto: str = "",
        termos: str = "",
        rodape: str = "",
        cor_primaria: str = "#1f4e79",
        usar_logo: bool = True,
        logo_path: str = "static/img/dealflow_logo.png",
    ) -> TemplateProposta:
        template = TemplateProposta(
            nome=nome,
            titulo_padrao=titulo_padrao,
            responsavel_padrao=responsavel_padrao,
            condicoes_pagamento_padrao=condicoes_pagamento_padrao,
            intro_texto=intro_texto,
            termos=termos,
            rodape=rodape,
            cor_primaria=cor_primaria,
            usar_logo=usar_logo,
            logo_path=logo_path,
        )
        self.templates.append(template)
        return template

    def listar_templates(self) -> List[TemplateProposta]:
        return self.templates

    def obter_template_por_id(self, template_id: int) -> Optional[TemplateProposta]:
        for template in self.templates:
            if template.id == template_id:
                return template
        return None
