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
                SELECT c.id, c.utilizador_id, c.parent_id,
                       COALESCE(p.nome_exibicao, u.username::text) AS autor,
                       u.username::text AS autor_username,
                       c.texto, c.criado_em,
                       COALESCE((SELECT SUM(v.valor) FROM votos_comentarios v
                                 WHERE v.comentario_id = c.id), 0) AS pontos
                FROM comentarios c
                JOIN utilizadores u ON u.id = c.utilizador_id
                LEFT JOIN perfis p ON p.utilizador_id = u.id
                WHERE c.publicacao_id = :id
                ORDER BY c.parent_id NULLS FIRST, pontos DESC, c.criado_em, c.id
                """
            ),
            {"id": publicacao_id},
        )
        return [dict(linha._mapping) for linha in linhas]

    def criar(self, comentario: Comentario) -> int:
        return self.sessao.execute(
            text(
                """
                INSERT INTO comentarios (publicacao_id, utilizador_id, parent_id, texto)
                VALUES (:publicacao_id, :utilizador_id, :parent_id, :texto)
                RETURNING id
                """
            ),
            {
                "publicacao_id": comentario.publicacao_id,
                "utilizador_id": comentario.utilizador_id,
                "parent_id": comentario.parent_id,
                "texto": comentario.texto,
            },
        ).scalar_one()

    def pertence_a_publicacao(self, comentario_id: int, publicacao_id: int) -> bool:
        return self.sessao.execute(
            text(
                "SELECT 1 FROM comentarios WHERE id = :id AND publicacao_id = :publicacao_id"
            ),
            {"id": comentario_id, "publicacao_id": publicacao_id},
        ).first() is not None

    def apagar(self, comentario_id: int) -> bool:
        resultado = self.sessao.execute(
            text("DELETE FROM comentarios WHERE id = :id"), {"id": comentario_id}
        )
        return resultado.rowcount == 1
