from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

from ..models import Proposta


class PdfReportGenerator:
    @classmethod
    def gerar_pdf_proposta(cls, proposta: Proposta, caminho: str):
        c = canvas.Canvas(caminho, pagesize=A4)
        largura, altura = A4

        margem_esquerda = 20 * mm
        margem_superior = altura - 20 * mm
        margem_inferior = 20 * mm

        y = margem_superior

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

        # Cabeçalho
        linha(f"Proposta #{proposta.id}", negrito=True, pula=8 * mm)
        linha(f"Título: {proposta.titulo}")
        linha(f"Cliente: {proposta.cliente.nome}")
        if proposta.cliente.documento:
            linha(f"Documento: {proposta.cliente.documento}")
        if proposta.cliente.contato:
            linha(f"Contato: {proposta.cliente.contato}")

        linha(f"Status: {proposta.status}")
        linha(f"Data de criação: {proposta.data_criacao.strftime('%d/%m/%Y %H:%M')}")
        if proposta.validade:
            linha(f"Validade: {proposta.validade.strftime('%d/%m/%Y')}")

        if proposta.responsavel:
            linha(f"Responsável: {proposta.responsavel}")
        if proposta.condicoes_pagamento:
            linha(f"Condições de pagamento: {proposta.condicoes_pagamento}")

        linha("")  # espaço

        # Resumo financeiro
        subtotal = proposta.calcular_subtotal()
        desconto = proposta.calcular_desconto()
        total = proposta.calcular_total()

        linha("Resumo financeiro", negrito=True, pula=7 * mm)
        linha(f"Subtotal: R$ {subtotal:.2f}")
        linha(f"Desconto: R$ {desconto:.2f}")
        linha(f"Total:    R$ {total:.2f}")

        linha("")  # espaço

        # Itens da proposta
        linha("Itens da proposta", negrito=True, pula=7 * mm)

        if not proposta.itens:
            linha("Nenhum item cadastrado.")
        else:
            c.setFont("Helvetica-Bold", 9)
            c.drawString(margem_esquerda, y, "Descrição")
            c.drawString(margem_esquerda + 90 * mm, y, "Qtd")
            c.drawString(margem_esquerda + 110 * mm, y, "Unitário")
            c.drawString(margem_esquerda + 140 * mm, y, "Total")
            y -= 6 * mm

            c.setFont("Helvetica", 9)
            for item in proposta.itens:
                if y <= margem_inferior:
                    c.showPage()
                    y = margem_superior
                    c.setFont("Helvetica-Bold", 9)
                    c.drawString(margem_esquerda, y, "Descrição")
                    c.drawString(margem_esquerda + 90 * mm, y, "Qtd")
                    c.drawString(margem_esquerda + 110 * mm, y, "Unitário")
                    c.drawString(margem_esquerda + 140 * mm, y, "Total")
                    y -= 6 * mm
                    c.setFont("Helvetica", 9)

                desc = item.descricao[:60]  # corta pra não estourar muito
                c.drawString(margem_esquerda, y, desc)
                c.drawRightString(margem_esquerda + 100 * mm, y, str(item.quantidade))
                c.drawRightString(margem_esquerda + 130 * mm, y, f"R$ {item.valor_unitario:.2f}")
                c.drawRightString(margem_esquerda + 170 * mm, y, f"R$ {item.total:.2f}")
                y -= 5 * mm

        c.showPage()
        c.save()
