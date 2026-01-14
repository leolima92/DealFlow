from abc import ABC, abstractmethod


class ProposalReportGenerator(ABC):
    @classmethod
    @abstractmethod
    def gerar(cls, proposta, caminho, template=None) -> None:
        raise NotImplementedError


class PropostasReportGenerator(ABC):
    @classmethod
    @abstractmethod
    def gerar(cls, gestor, caminho: str | None = None) -> str:
        raise NotImplementedError
