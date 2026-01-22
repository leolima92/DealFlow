class StatusPolicy:
    VALID_STATUSES = ("rascunho", "enviada", "aceita", "recusada", "cancelada")

    @classmethod
    def normalize(cls, status: str) -> str:
        return (status or "").strip().lower()

    @classmethod
    def is_valid(cls, status: str) -> bool:
        return cls.normalize(status) in cls.VALID_STATUSES

    @classmethod
    def ensure_valid(cls, status: str) -> str:
        normalized = cls.normalize(status)
        if normalized not in cls.VALID_STATUSES:
            raise ValueError(f"Status inválido: {status}")
        return normalized
