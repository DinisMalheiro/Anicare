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

    def __post_init__(self):
        self.titulo = (self.titulo or "").strip()
        if not self.titulo:
            raise ErroDominio("O título é obrigatório.")
        if len(self.titulo) > 150:
            raise ErroDominio("O título tem demasiados caracteres (máximo 150).")

        self.descricao = (self.descricao or "").strip() or None
        if self.descricao and len(self.descricao) > 5000:
            raise ErroDominio("A descrição tem demasiados caracteres (máximo 5000).")

        if not (-90 <= self.latitude <= 90) or not (-180 <= self.longitude <= 180):
            raise ErroDominio("Coordenadas inválidas: escolhe o local no mapa.")

        if self.data_avistamento.tzinfo is None:
            # datas sem fuso (formulário) são tratadas como hora local do servidor
            self.data_avistamento = self.data_avistamento.astimezone()
        if self.data_avistamento > datetime.now(timezone.utc) + timedelta(minutes=5):
            raise ErroDominio("A data do avistamento não pode estar no futuro.")
