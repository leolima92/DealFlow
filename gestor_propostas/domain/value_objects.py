from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Desconto:
    tipo: str | None
    percentual: float
    valor: float

    @classmethod
    def nenhum(cls) -> "Desconto":
        return cls(tipo=None, percentual=0.0, valor=0.0)

    @classmethod
    def percentual(cls, percentual: float) -> "Desconto":
        return cls(tipo="%", percentual=max(0.0, percentual), valor=0.0)

    @classmethod
    def valor(cls, valor: float) -> "Desconto":
        return cls(tipo="R", percentual=0.0, valor=max(0.0, valor))

    @classmethod
    def from_db_fields(cls, tipo: str | None, percentual: float | None, valor: float | None) -> "Desconto":
        if tipo == "%":
            return cls.percentual(percentual or 0.0)
        if tipo == "R":
            return cls.valor(valor or 0.0)
        return cls.nenhum()

    def calcular(self, subtotal: float) -> float:
        if self.tipo == "%":
            return subtotal * (self.percentual / 100.0)
        if self.tipo == "R":
            return self.valor
        return 0.0

    def as_db_fields(self) -> tuple[str | None, float, float]:
        return (self.tipo, self.percentual, self.valor)


@dataclass(frozen=True)
class CondicoesPagamento:
    texto: str

    @classmethod
    def from_parts(cls, forma_pagamento: str, num_parcelas: str, pagamento_obs: str) -> "CondicoesPagamento":
        parts = []
        if forma_pagamento:
            parts.append(f"Forma: {forma_pagamento}")
        if num_parcelas:
            parts.append(f"Parcelas: {num_parcelas}x")
        if pagamento_obs:
            parts.append(f"Obs: {pagamento_obs}")
        return cls(" | ".join(parts))

    def __str__(self) -> str:
        return self.texto
