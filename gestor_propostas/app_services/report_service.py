from __future__ import annotations

import tempfile

from ..domain import GestorPropostas, Proposta, TemplateProposta
from ..services.excel_report import ExcelReportGenerator
from ..services.pdf_report import PdfReportGenerator


class ReportService:
    def __init__(self, gestor: GestorPropostas):
        self._gestor = gestor

    def gerar_excel_temp(self) -> str:
        return ExcelReportGenerator.gerar(self._gestor)

    def gerar_pdf_temp(self, proposta: Proposta, template: TemplateProposta | None = None) -> str:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f"_proposta_{proposta.id}.pdf")
        tmp.close()
        PdfReportGenerator.gerar(proposta, tmp.name, template=template)
        return tmp.name
