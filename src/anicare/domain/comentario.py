from dataclasses import dataclass
from datetime import datetime

from anicare.erros import ErroDominio


@dataclass
class Comentario:
    publicacao_id: int
    utilizador_id: int
    texto: str
    parent_id: int | None = None
    id: int | None = None
    criado_em: datetime | None = None

    def __post_init__(self):
        self.texto = (self.texto or "").strip()
        if not self.texto:
            raise ErroDominio("O comentário não pode estar vazio.")
        if len(self.texto) > 2000:
            raise ErroDominio("O comentário tem demasiados caracteres (máximo 2000).")
