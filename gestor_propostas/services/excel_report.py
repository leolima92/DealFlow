import os
from datetime import datetime
from tempfile import NamedTemporaryFile
from openpyxl import Workbook
from ..models import Proposta  


class ExcelReportGenerator:
    @staticmethod
    def gerar_excel_from_query(propostas, caminho: str | None = None) -> str:

        if caminho is None:
            tmp = NamedTemporaryFile(delete=False, suffix=".xlsx")
            caminho = tmp.name
            tmp.close()

        wb = Workbook()
        ws = wb.active
        ws.title = "Propostas"
        ws.append([
            "ID",
            "Título",
            "Cliente",
            "Status",
            "Data Criação",
            "Validade",
            "Responsável",
            "Condições de Pagamento",
            "Subtotal",
            "Desconto",
            "Total",
        ])

        for p in propostas:
            subtotal = p.calcular_subtotal()
            total = p.calcular_total()

            if p.tipo_desconto == "%":
                desconto_str = f"{p.desconto_percentual:.2f}%"
            elif p.tipo_desconto == "R":
                desconto_str = f"R$ {p.desconto_valor:.2f}"
            else:
                desconto_str = "-"

            ws.append([
                p.id,
                p.titulo,
                p.cliente.nome if p.cliente else "",
                p.status,
                p.data_criacao.strftime("%Y-%m-%d %H:%M") if p.data_criacao else "",
                p.validade.strftime("%Y-%m-%d") if p.validade else "",
                p.responsavel or "",
                p.condicoes_pagamento or "",
                float(f"{subtotal:.2f}"),
                desconto_str,
                float(f"{total:.2f}"),
            ])

        for column_cells in ws.columns:
            length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells)
            col_letter = column_cells[0].column_letter
            ws.column_dimensions[col_letter].width = min(max(length + 2, 12), 40)

        wb.save(caminho)
        return caminho
