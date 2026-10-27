from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from anicare.erros import ErroDominio


@dataclass
class Publicacao:
    """Um avistamento: onde e quando um animal foi visto."""

    utilizador_id: int
    animal_id: int | None  # None = o animal ainda vai ser criado
    titulo: str
    latitude: float
    longitude: float
    data_avistamento: datetime
    descricao: str | None = None
    id: int | None = None
    criado_em: datetime | None = None
    atualizado_em: datetime | None = None


