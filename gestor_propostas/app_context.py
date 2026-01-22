from dataclasses import dataclass

from flask import current_app

from .domain import GestorPropostas
from .infra import StorageManager, ClienteRepository, PropostaRepository, TemplateRepository
from .app_services import (
    ClienteService,
    PropostaService,
    TemplateService,
    DashboardService,
    AuthService,
    ReportService,
)


@dataclass
class AppContext:
    gestor: GestorPropostas
    storage: StorageManager
    cliente_service: ClienteService
    proposta_service: PropostaService
    template_service: TemplateService
    dashboard_service: DashboardService
    auth_service: AuthService
    report_service: ReportService

    @classmethod
    def bootstrap(cls) -> "AppContext":
        gestor = GestorPropostas()
        storage = StorageManager()
        storage.init_db()
        storage.carregar_tudo(gestor)
        cliente_repo = ClienteRepository(storage)
        proposta_repo = PropostaRepository(storage)
        template_repo = TemplateRepository(storage)
        return cls(
            gestor=gestor,
            storage=storage,
            cliente_service=ClienteService(gestor, cliente_repo),
            proposta_service=PropostaService(gestor, proposta_repo),
            template_service=TemplateService(gestor, template_repo, proposta_repo),
            dashboard_service=DashboardService(gestor),
            auth_service=AuthService(),
            report_service=ReportService(gestor),
        )


def get_context() -> AppContext:
    return current_app.extensions["app_context"]
