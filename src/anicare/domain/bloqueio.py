import ipaddress
from dataclasses import dataclass
from datetime import datetime, timezone

from anicare.erros import ErroDominio


@dataclass
class Bloqueio:

    criado_por: int
    ban_motivo: str
    utilizador_id: int | None = None
    ip: str | None = None
    expira_em: datetime | None = None  # None = permanente
    id: int | None = None
    criado_em: datetime | None = None


