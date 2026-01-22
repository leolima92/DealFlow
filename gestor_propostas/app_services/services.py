from __future__ import annotations

from typing import Optional

from ..domain import Cliente, ItemProposta, Proposta, TemplateProposta, PropostaFactory, TemplateFactory
from ..infra import ClienteRepository, PropostaRepository, TemplateRepository
from ..domain import GestorPropostas
from .view_models import DashboardViewModel, PropostasListViewModel


class ClienteService:
    def __init__(self, gestor: GestorPropostas, repo: ClienteRepository):
        self._gestor = gestor
        self._repo = repo

    def listar(self):
        return self._gestor.listar_clientes()

    def obter_por_id(self, cliente_id: int) -> Optional[Cliente]:
        return next((c for c in self._gestor.listar_clientes() if c.id == cliente_id), None)

    def criar(self, nome: str, documento: str = "", contato: str = "") -> Cliente:
        cliente = self._gestor.criar_cliente(nome, documento, contato)
        self._repo.salvar(cliente)
        return cliente


class PropostaService:
    def __init__(self, gestor: GestorPropostas, repo: PropostaRepository):
        self._gestor = gestor
        self._repo = repo

    def listar(self):
        return self._gestor.listar_propostas()

    def obter_por_id(self, proposta_id: int) -> Optional[Proposta]:
        return next((p for p in self._gestor.listar_propostas() if p.id == proposta_id), None)

    def criar(
        self,
        cliente: Cliente,
        titulo: str = "",
        validade=None,
        responsavel: str = "",
        condicoes_pagamento: str = "",
        template_id: Optional[int] = None,
    ) -> Proposta:
        proposta = self._gestor.criar_proposta(
            cliente,
            titulo,
            validade=validade,
            responsavel=responsavel,
            condicoes_pagamento=condicoes_pagamento,
            template_id=template_id,
        )
        self._repo.salvar(proposta)
        self._repo.sincronizar_itens(proposta)
        return proposta

    def criar_com_template(
        self,
        cliente: Cliente,
        titulo: str,
        responsavel: str,
        forma_pagamento: str,
        num_parcelas: str,
        pagamento_obs: str,
        validade=None,
        template: TemplateProposta | None = None,
    ) -> Proposta:
        proposta = PropostaFactory.construir(
            cliente=cliente,
            titulo=titulo,
            responsavel=responsavel,
            validade=validade,
            forma_pagamento=forma_pagamento,
            num_parcelas=num_parcelas,
            pagamento_obs=pagamento_obs,
            template=template,
        )
        self._gestor.propostas.append(proposta)
        self._repo.salvar(proposta)
        self._repo.sincronizar_itens(proposta)
        return proposta

    def adicionar_item(self, proposta: Proposta, descricao: str, quantidade: int, valor_unitario: float) -> ItemProposta:
        item = ItemProposta(descricao, quantidade, valor_unitario)
        proposta.adicionar_item(item)
        self._repo.sincronizar_itens(proposta)
        self._repo.salvar(proposta)
        return item

    def aplicar_desconto(self, proposta: Proposta, tipo: str, valor: float | None = None) -> None:
        if tipo == "nenhum":
            proposta.remover_desconto()
        elif tipo == "%":
            proposta.definir_desconto_percentual(valor or 0.0)
        elif tipo == "R":
            proposta.definir_desconto_valor(valor or 0.0)

        self._repo.salvar(proposta)

    def atualizar_pagamento(self, proposta: Proposta, condicoes_pagamento: str) -> None:
        proposta.condicoes_pagamento = condicoes_pagamento
        self._repo.salvar(proposta)

    def atualizar_template(self, proposta: Proposta, template_id: Optional[int]) -> None:
        proposta.template_id = template_id
        self._repo.salvar(proposta)

    def alterar_status(self, proposta: Proposta, status: str) -> None:
        proposta.alterar_status(status)
        self._repo.salvar(proposta)

    def excluir(self, proposta_id: int) -> bool:
        self._gestor.propostas = [p for p in self._gestor.propostas if p.id != proposta_id]
        try:
            self._repo.excluir(proposta_id)
            return True
        except Exception:
            return False

class TemplateService:
    def __init__(self, gestor: GestorPropostas, repo: TemplateRepository, proposta_repo: PropostaRepository):
        self._gestor = gestor
        self._repo = repo
        self._proposta_repo = proposta_repo

    def listar(self):
        return self._gestor.listar_templates()

    def obter_por_id(self, template_id: int) -> Optional[TemplateProposta]:
        return self._gestor.obter_template_por_id(template_id)

    def criar(
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
        template = TemplateFactory.construir(
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
        self._gestor.templates.append(template)
        self._repo.salvar(template)
        return template

    def atualizar(self, template: TemplateProposta) -> None:
        self._repo.salvar(template)

    def excluir(self, template_id: int) -> None:
        for proposta in self._gestor.propostas:
            if proposta.template_id == template_id:
                proposta.template_id = None
                self._proposta_repo.salvar(proposta)

        self._gestor.templates = [t for t in self._gestor.templates if t.id != template_id]
        self._repo.excluir(template_id)


class DashboardService:
    def __init__(self, gestor: GestorPropostas):
        self._gestor = gestor

    def build_dashboard(self, q: str, status: str) -> DashboardViewModel:
        return DashboardViewModel.build(
            propostas_all=self._gestor.listar_propostas(),
            clientes_all=self._gestor.listar_clientes(),
            q=q,
            status=status,
        )

    def build_propostas_list(
        self,
        q: str,
        status: str,
        page: int,
        per_page: int,
    ) -> PropostasListViewModel:
        return PropostasListViewModel.build(
            propostas_all=self._gestor.listar_propostas(),
            q=q,
            status=status,
            page=page,
            per_page=per_page,
        )
