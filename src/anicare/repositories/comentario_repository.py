from sqlalchemy import text
from sqlalchemy.orm import Session

from anicare.domain.comentario import Comentario


class ComentarioRepository:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar_por_publicacao(self, publicacao_id: int) -> list[dict]:
        linhas = self.sessao.execute(
            text(
                """
                SELECT c.id, c.utilizador_id, u.username::text AS autor, c.texto, c.criado_em,
                       COALESCE((SELECT SUM(v.valor) FROM votos_comentarios v
                                 WHERE v.comentario_id = c.id), 0) AS pontos
                FROM comentarios c
                JOIN utilizadores u ON u.id = c.utilizador_id
                WHERE c.publicacao_id = :id
                ORDER BY c.criado_em, c.id
                """
            ),
            {"id": publicacao_id},
        )
        return [dict(linha._mapping) for linha in linhas]

    def criar(self, comentario: Comentario) -> int:
        return self.sessao.execute(
            text(
                """
                INSERT INTO comentarios (publicacao_id, utilizador_id, texto)
                VALUES (:publicacao_id, :utilizador_id, :texto)
                RETURNING id
                """
            ),
            {
                "publicacao_id": comentario.publicacao_id,
                "utilizador_id": comentario.utilizador_id,
                "texto": comentario.texto,
            },
        ).scalar_one()
