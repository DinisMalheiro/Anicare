import ipaddress
from dataclasses import dataclass
from datetime import datetime, timezone

from anicare.erros import ErroDominio


def normalizar_ip(ip: str | None) -> str | None:
    """Devolve o IP em formato canónico, ou None se não for um IP válido."""
    if not ip:
        return None
    try:
        return str(ipaddress.ip_address(ip.split("%")[0].strip()))
    except ValueError:
        return None


@dataclass
class Bloqueio:
    """Bloqueio de uma conta e/ou de um IP (ou intervalo de IPs, ex.: 203.0.113.0/24)."""

    criado_por: int
    ban_motivo: str
    utilizador_id: int | None = None
    ip: str | None = None
    expira_em: datetime | None = None  # None = permanente
    id: int | None = None
    criado_em: datetime | None = None

    def __post_init__(self):
        if self.utilizador_id is None and not self.ip:
            raise ErroDominio("Indica a conta ou o IP a bloquear.")
        self.ban_motivo = (self.ban_motivo or "").strip()
        if not self.ban_motivo:
            raise ErroDominio("O motivo do bloqueio é obrigatório.")
        if self.ip:
            try:
                self.ip = str(ipaddress.ip_network(self.ip.strip(), strict=False))
            except ValueError:
                raise ErroDominio("IP ou intervalo de IPs inválido.") from None

    def esta_ativo(self, agora: datetime | None = None) -> bool:
        agora = agora or datetime.now(timezone.utc)
        return self.expira_em is None or self.expira_em > agora
