from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class DashboardViewModel:
    propostas: List
    filtro_q: str
    filtro_status: str
    statuses: List[str]
    total_propostas: int
    total_clientes: int
    qtd_aceitas: int
    valor_total_aceitas: float
    status_data: List[dict]
    arrecadacao_mes_data: List[dict]

    @classmethod
    def build(cls, propostas_all: Iterable, clientes_all: Iterable, q: str, status: str) -> "DashboardViewModel":
        q = (q or "").strip().lower()
        status = (status or "").strip().lower()

        propostas_all_list = list(propostas_all)
        clientes_all_list = list(clientes_all)
        propostas = list(propostas_all_list)
        if status:
            propostas = [p for p in propostas if p.status == status]

        if q:
            propostas = [
                p for p in propostas
                if q in p.titulo.lower() or (p.cliente and q in p.cliente.nome.lower())
            ]

        statuses = sorted({p.status for p in propostas_all_list}, key=str.lower)
        total_propostas = len(propostas_all_list)
        total_clientes = len(clientes_all_list)
        propostas_aceitas = [p for p in propostas_all_list if p.status == "aceita"]
        qtd_aceitas = len(propostas_aceitas)
        valor_total_aceitas = sum(p.calcular_total() for p in propostas_aceitas)

        from collections import Counter, defaultdict
        status_counts = Counter(p.status for p in propostas_all_list)
        status_data = [{"status": k, "count": v} for k, v in status_counts.items()]

        arrecadacao_por_mes = defaultdict(float)
        for p in propostas_aceitas:
            if p.data_criacao:
                mes_ano = p.data_criacao.strftime("%Y-%m")
                arrecadacao_por_mes[mes_ano] += p.calcular_total()
        arrecadacao_mes_data = [{"mes": k, "valor": v} for k, v in sorted(arrecadacao_por_mes.items())]

        return cls(
            propostas=propostas,
            filtro_q=q,
            filtro_status=status,
            statuses=statuses,
            total_propostas=total_propostas,
            total_clientes=total_clientes,
            qtd_aceitas=qtd_aceitas,
            valor_total_aceitas=valor_total_aceitas,
            status_data=status_data,
            arrecadacao_mes_data=arrecadacao_mes_data,
        )


@dataclass
class PropostasListViewModel:
    propostas: List
    filtro_q: str
    filtro_status: str
    statuses: List[str]
    current_page: int
    total_pages: int
    total_propostas: int

    @classmethod
    def build(cls, propostas_all: Iterable, q: str, status: str, page: int, per_page: int) -> "PropostasListViewModel":
        q = (q or "").strip().lower()
        status = (status or "").strip().lower()

        propostas_all_list = list(propostas_all)
        propostas = list(propostas_all_list)
        if status:
            propostas = [p for p in propostas if p.status == status]

        if q:
            propostas = [
                p for p in propostas
                if q in p.titulo.lower()
                or (p.cliente and q in p.cliente.nome.lower())
                or q in str(p.id)
            ]

        total_propostas = len(propostas)
        start = (page - 1) * per_page
        end = start + per_page
        propostas_paginadas = propostas[start:end]
        total_pages = (total_propostas + per_page - 1) // per_page
        statuses = sorted({p.status for p in propostas_all_list}, key=str.lower)

        return cls(
            propostas=propostas_paginadas,
            filtro_q=q,
            filtro_status=status,
            statuses=statuses,
            current_page=page,
            total_pages=total_pages,
            total_propostas=total_propostas,
        )
