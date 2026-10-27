from dataclasses import dataclass
from datetime import datetime

from anicare.erros import ErroDominio


@dataclass
class Fotografia:
    """Uma imagem que pertence a uma publicação OU a um comentário (nunca aos dois)."""

    caminho: str
    publicacao_id: int | None = None
    comentario_id: int | None = None
    ordem: int = 1
    id: int | None = None
    criado_em: datetime | None = None

