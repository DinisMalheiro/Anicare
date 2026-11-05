"""Votos (upvote/downvote) em publicações e comentários.

TODO (próximo passo): implementar com SQL como nos outros repositórios.

    votar_publicacao(utilizador_id, publicacao_id, valor)
        INSERT INTO votos_publicacoes (...) VALUES (...)
        ON CONFLICT (utilizador_id, publicacao_id) DO UPDATE SET valor = EXCLUDED.valor
    retirar_voto_publicacao(utilizador_id, publicacao_id)
    votar_comentario(...) / retirar_voto_comentario(...)   (tabela votos_comentarios)
"""

from sqlalchemy.orm import Session


class VotoRepository:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def votar_publicacao(self, utilizador_id: int, publicacao_id: int, valor: int) -> None:
        raise NotImplementedError("Por implementar.")

    def votar_comentario(self, utilizador_id: int, comentario_id: int, valor: int) -> None:
        raise NotImplementedError("Por implementar.")
