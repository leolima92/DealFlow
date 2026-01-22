from __future__ import annotations

from datetime import date
from typing import Optional

from .models import Cliente, Proposta, TemplateProposta
from .value_objects import CondicoesPagamento


class PropostaFactory:
    @staticmethod
    def construir(
        cliente: Cliente,
        titulo: str,
        responsavel: str,
        validade: Optional[date],
        forma_pagamento: str,
        num_parcelas: str,
        pagamento_obs: str,
        template: TemplateProposta | None = None,
    ) -> Proposta:
        cond_pag = str(CondicoesPagamento.from_parts(forma_pagamento, num_parcelas, pagamento_obs))

        if template:
            if not titulo and template.titulo_padrao:
                titulo = template.titulo_padrao
            if not responsavel and template.responsavel_padrao:
                responsavel = template.responsavel_padrao
            if not cond_pag and template.condicoes_pagamento_padrao:
                cond_pag = template.condicoes_pagamento_padrao

        return Proposta(
            cliente=cliente,
            titulo=titulo,
            validade=validade,
            responsavel=responsavel,
            condicoes_pagamento=cond_pag,
            template_id=template.id if template else None,
        )


class TemplateFactory:
    @staticmethod
    def construir(
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
        return TemplateProposta(
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
