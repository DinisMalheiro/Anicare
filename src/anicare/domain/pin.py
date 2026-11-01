import math
from dataclasses import dataclass
from datetime import datetime

from anicare.erros import ErroDominio

ESPECIES = ("cão", "gato", "outro")


@dataclass
class Pin:
    """Um animal avistado num ponto do mapa."""

    titulo: str
    especie: str
    latitude: float
    longitude: float
    descricao: str | None = None
    id: int | None = None
    criado_em: datetime | None = None

    def __post_init__(self):
        self.titulo = (self.titulo or "").strip()
        if not self.titulo:
            raise ErroDominio("O título é obrigatório.")
        if len(self.titulo) > 150:
            raise ErroDominio("O título tem demasiados caracteres (máximo 150).")

        self.descricao = (self.descricao or "").strip() or None
        if self.descricao and len(self.descricao) > 2000:
            raise ErroDominio("A descrição tem demasiados caracteres (máximo 2000).")

        if self.especie not in ESPECIES:
            raise ErroDominio("Escolhe a espécie: cão, gato ou outro.")

        try:
            self.latitude, self.longitude = float(self.latitude), float(self.longitude)
        except (TypeError, ValueError):
            raise ErroDominio("Escolhe o local no mapa.") from None
        if not (math.isfinite(self.latitude) and math.isfinite(self.longitude)) or not (
            -90 <= self.latitude <= 90 and -180 <= self.longitude <= 180
        ):
            raise ErroDominio("Coordenadas inválidas: escolhe o local no mapa.")
