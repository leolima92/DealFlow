import os

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

from ..models import Proposta, TemplateProposta
from .. import ROOT_DIR


class PdfReportGenerator:
    @classmethod
    def gerar_pdf_proposta(
        cls,
        proposta: Proposta,
        caminho: str,
        template: TemplateProposta | None = None,
    ):
        c = canvas.Canvas(caminho, pagesize=A4)
        largura, altura = A4

        margem_esquerda = 20 * mm
        margem_superior = altura - 20 * mm
        margem_inferior = 20 * mm

        y = margem_superior

        def parse_cor(hex_color: str):
            try:
                hex_color = hex_color.strip().lstrip("#")
                if len(hex_color) != 6:
                    raise ValueError("invalid color")
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
                return colors.Color(r, g, b)
            except Exception:
                return colors.HexColor("#1f4e79")

        def linha(texto: str, negrito: bool = False, pula: float = 6 * mm):
            nonlocal y
            if y <= margem_inferior:
                c.showPage()
                y = margem_superior
            if negrito:
                c.setFont("Helvetica-Bold", 11)
            else:
                c.setFont("Helvetica", 10)
            c.drawString(margem_esquerda, y, texto)
            y -= pula

        # Cabecalho com layout do template
        if template:
            cor = parse_cor(template.cor_primaria or "#1f4e79")
            c.setFillColor(cor)
            c.rect(0, altura - 30 * mm, largura, 30 * mm, stroke=0, fill=1)
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(margem_esquerda, altura - 20 * mm, f"Proposta #{proposta.id}")

            if template.usar_logo and template.logo_path:
                logo_path = os.path.join(ROOT_DIR, template.logo_path)
                if os.path.exists(logo_path):
                    c.drawImage(
                        logo_path,
                        largura - 55 * mm,
                        altura - 27 * mm,
                        width=35 * mm,
                        height=18 * mm,
                        preserveAspectRatio=True,
                        mask="auto",
                    )
            y = altura - 35 * mm
            c.setFillColor(colors.black)
        else:
            linha(f"Proposta #{proposta.id}", negrito=True, pula=8 * mm)

        linha(f"Titulo: {proposta.titulo}")
        linha(f"Cliente: {proposta.cliente.nome}")
        if proposta.cliente.documento:
            linha(f"Documento: {proposta.cliente.documento}")
        if proposta.cliente.contato:
            linha(f"Contato: {proposta.cliente.contato}")

        linha(f"Status: {proposta.status}")
        linha(f"Data de criacao: {proposta.data_criacao.strftime('%d/%m/%Y %H:%M')}")
        if proposta.validade:
            linha(f"Validade: {proposta.validade.strftime('%d/%m/%Y')}")

        if proposta.responsavel:
            linha(f"Responsavel: {proposta.responsavel}")
        if proposta.condicoes_pagamento:
            linha(f"Condicoes de pagamento: {proposta.condicoes_pagamento}")

        if template and template.intro_texto:
            linha("")
            linha("Apresentacao", negrito=True, pula=7 * mm)
            for trecho in template.intro_texto.splitlines():
                if trecho.strip():
                    linha(trecho.strip())

        linha("")  # espaco

        # Resumo financeiro
        subtotal = proposta.calcular_subtotal()
        desconto = proposta.calcular_desconto()
        total = proposta.calcular_total()

        linha("Resumo financeiro", negrito=True, pula=7 * mm)
        linha(f"Subtotal: R$ {subtotal:.2f}")
        linha(f"Desconto: R$ {desconto:.2f}")
        linha(f"Total:    R$ {total:.2f}")

        linha("")  # espaco

        # Itens da proposta
        linha("Itens da proposta", negrito=True, pula=7 * mm)

        if not proposta.itens:
            linha("Nenhum item cadastrado.")
        else:
            c.setFont("Helvetica-Bold", 9)
            c.drawString(margem_esquerda, y, "Descricao")
            c.drawString(margem_esquerda + 90 * mm, y, "Qtd")
            c.drawString(margem_esquerda + 110 * mm, y, "Unitario")
            c.drawString(margem_esquerda + 140 * mm, y, "Total")
            y -= 6 * mm

            c.setFont("Helvetica", 9)
            for item in proposta.itens:
                if y <= margem_inferior:
                    c.showPage()
                    y = margem_superior
                    c.setFont("Helvetica-Bold", 9)
                    c.drawString(margem_esquerda, y, "Descricao")
                    c.drawString(margem_esquerda + 90 * mm, y, "Qtd")
                    c.drawString(margem_esquerda + 110 * mm, y, "Unitario")
                    c.drawString(margem_esquerda + 140 * mm, y, "Total")
                    y -= 6 * mm
                    c.setFont("Helvetica", 9)

                desc = item.descricao[:60]  # corta pra nao estourar muito
                c.drawString(margem_esquerda, y, desc)
                c.drawRightString(margem_esquerda + 100 * mm, y, str(item.quantidade))
                c.drawRightString(margem_esquerda + 130 * mm, y, f"R$ {item.valor_unitario:.2f}")
                c.drawRightString(margem_esquerda + 170 * mm, y, f"R$ {item.total:.2f}")
                y -= 5 * mm

        if template and template.termos:
            linha("")
            linha("Termos", negrito=True, pula=7 * mm)
            for trecho in template.termos.splitlines():
                if trecho.strip():
                    linha(trecho.strip())

        if template and template.rodape:
            linha("")
            linha(template.rodape)

        c.showPage()
        c.save()
