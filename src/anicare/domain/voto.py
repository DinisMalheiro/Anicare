from dataclasses import dataclass

from anicare.erros import ErroDominio

UPVOTE = 1
DOWNVOTE = -1


@dataclass
class Voto:
    """Voto de um utilizador numa publicação ou num comentário (+1 ou -1)."""

    utilizador_id: int
    valor: int

    def __post_init__(self):
        if self.valor not in (UPVOTE, DOWNVOTE):
            raise ErroDominio("O voto tem de ser +1 (upvote) ou -1 (downvote).")
