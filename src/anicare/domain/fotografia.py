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

    def __post_init__(self):
        if (self.publicacao_id is None) == (self.comentario_id is None):
            raise ErroDominio(
                "A fotografia tem de pertencer a uma publicação ou a um comentário."
            )
        caminho = (self.caminho or "").strip()
        partes = caminho.replace("\\", "/").split("/")
        if not caminho or caminho.startswith("/") or ".." in partes:
            raise ErroDominio("Caminho de fotografia inválido.")
        self.caminho = caminho
