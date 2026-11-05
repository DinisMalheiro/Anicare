"""Votos (upvote/downvote) em publicações e comentários.

TODO (próximo passo): implementar com SQL como nos outros repositórios.

    votar_publicacao(utilizador_id, publicacao_id, valor)
        INSERT INTO votos_publicacoes (...) VALUES (...)
        ON CONFLICT (utilizador_id, publicacao_id) DO UPDATE SET valor = EXCLUDED.valor
    retirar_voto_publicacao(utilizador_id, publicacao_id)
    votar_comentario(...) / retirar_voto_comentario(...)   (tabela votos_comentarios)
"""

from sqlalchemy import text
from sqlalchemy.orm import Session


class VotoRepository:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def votar_publicacao(self, utilizador_id: int, publicacao_id: int, valor: int) -> None:
        self._votar("votos_publicacoes", "publicacao_id", utilizador_id, publicacao_id, valor)

    def votar_comentario(self, utilizador_id: int, comentario_id: int, valor: int) -> None:
        self._votar("votos_comentarios", "comentario_id", utilizador_id, comentario_id, valor)

    def retirar_voto_publicacao(self, utilizador_id: int, publicacao_id: int) -> None:
        self._retirar("votos_publicacoes", "publicacao_id", utilizador_id, publicacao_id)

    def retirar_voto_comentario(self, utilizador_id: int, comentario_id: int) -> None:
        self._retirar("votos_comentarios", "comentario_id", utilizador_id, comentario_id)

    def obter(self, tipo: str, utilizador_id: int, conteudo_id: int) -> int | None:
        tabela = "votos_publicacoes" if tipo == "publicacao" else "votos_comentarios"
        coluna = "publicacao_id" if tipo == "publicacao" else "comentario_id"
        return self.sessao.execute(
            text(
                f"SELECT valor FROM {tabela} WHERE utilizador_id = :uid AND {coluna} = :cid"
            ),
            {"uid": utilizador_id, "cid": conteudo_id},
        ).scalar()

    def pode_votar_publicacao(self, utilizador_id: int, publicacao_id: int) -> bool:
        return self.sessao.execute(
            text(
                """
                SELECT 1 FROM publicacoes
                WHERE id = :pid AND utilizador_id <> :uid
                """
            ),
            {"pid": publicacao_id, "uid": utilizador_id},
        ).first() is not None

    def _votar(self, tabela, coluna, utilizador_id, conteudo_id, valor):
        self.sessao.execute(
            text(
                f"""
                INSERT INTO {tabela} (utilizador_id, {coluna}, valor)
                VALUES (:uid, :cid, :valor)
                ON CONFLICT (utilizador_id, {coluna})
                DO UPDATE SET valor = EXCLUDED.valor
                """
            ),
            {"uid": utilizador_id, "cid": conteudo_id, "valor": valor},
        )

    def _retirar(self, tabela, coluna, utilizador_id, conteudo_id):
        self.sessao.execute(
            text(
                f"DELETE FROM {tabela} WHERE utilizador_id = :uid AND {coluna} = :cid"
            ),
            {"uid": utilizador_id, "cid": conteudo_id},
        )
