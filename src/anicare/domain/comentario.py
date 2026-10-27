from dataclasses import dataclass
from datetime import datetime

from anicare.erros import ErroDominio


@dataclass
class Comentario:
    publicacao_id: int
    utilizador_id: int
    texto: str
    id: int | None = None
    criado_em: datetime | None = None
