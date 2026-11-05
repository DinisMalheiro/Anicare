from sqlalchemy import text
from sqlalchemy.orm import Session

from anicare.domain.fotografia import Fotografia


class FotografiaRepository:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def criar(self, fotografia: Fotografia) -> int:
        return self.sessao.execute(
            text(
                """
                INSERT INTO fotografias (publicacao_id, comentario_id, caminho, ordem)
                VALUES (:publicacao_id, :comentario_id, :caminho, :ordem)
                RETURNING id
                """
            ),
            {
                "publicacao_id": fotografia.publicacao_id,
                "comentario_id": fotografia.comentario_id,
                "caminho": fotografia.caminho,
                "ordem": fotografia.ordem,
            },
        ).scalar_one()

    def listar_por_publicacao(self, publicacao_id: int) -> list[str]:
        linhas = self.sessao.execute(
            text(
                "SELECT caminho FROM fotografias WHERE publicacao_id = :id ORDER BY ordem, id"
            ),
            {"id": publicacao_id},
        )
        return [linha.caminho for linha in linhas]

    def substituir_principal(self, publicacao_id: int, caminho: str) -> str | None:
        antigo = self.sessao.execute(
            text(
                """
                SELECT caminho FROM fotografias
                WHERE publicacao_id = :id
                ORDER BY ordem, id LIMIT 1
                """
            ),
            {"id": publicacao_id},
        ).scalar()
        if antigo:
            self.sessao.execute(
                text(
                    """
                    UPDATE fotografias SET caminho = :caminho
                    WHERE id = (
                        SELECT id FROM fotografias
                        WHERE publicacao_id = :id
                        ORDER BY ordem, id LIMIT 1
                    )
                    """
                ),
                {"id": publicacao_id, "caminho": caminho},
            )
        else:
            self.criar(Fotografia(caminho=caminho, publicacao_id=publicacao_id))
        return antigo

    def listar_por_comentarios(self, comentario_ids: list[int]) -> dict[int, list[str]]:
        if not comentario_ids:
            return {}
        linhas = self.sessao.execute(
            text(
                """
                SELECT comentario_id, caminho FROM fotografias
                WHERE comentario_id = ANY(CAST(:ids AS bigint[]))
                ORDER BY ordem, id
                """
            ),
            {"ids": comentario_ids},
        )
        resultado: dict[int, list[str]] = {}
        for linha in linhas:
            resultado.setdefault(linha.comentario_id, []).append(linha.caminho)
        return resultado
