from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from anicare.erros import ErroNegocio


class PerfilRepository:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def obter(self, username: str) -> dict | None:
        linha = self.sessao.execute(
            text(
                """
                SELECT u.id, u.username, p.nome_exibicao, p.bio, p.avatar_caminho,
                       p.atualizado_em
                FROM utilizadores u LEFT JOIN perfis p ON p.utilizador_id = u.id
                WHERE u.username = CAST(:username AS citext) AND u.ativo
                """
            ), {"username": username},
        ).first()
        return dict(linha._mapping) if linha else None

    def guardar(self, utilizador_id: int, nome: str | None, bio: str | None,
                avatar_caminho: str | None = None) -> str | None:
        if not nome:
            raise ErroNegocio("O nome público é obrigatório.")
        antigo = self.sessao.execute(
            text("SELECT avatar_caminho FROM perfis WHERE utilizador_id = :id"),
            {"id": utilizador_id},
        ).scalar()
        try:
            self.sessao.execute(
                text(
                """
                INSERT INTO perfis (utilizador_id, nome_exibicao, bio, atualizado_em)
                VALUES (:id, :nome, :bio, now())
                ON CONFLICT (utilizador_id) DO UPDATE SET
                    nome_exibicao = EXCLUDED.nome_exibicao,
                    bio = EXCLUDED.bio,
                    avatar_caminho = COALESCE(:avatar, perfis.avatar_caminho),
                    atualizado_em = now()
                """
                ), {"id": utilizador_id, "nome": nome, "bio": bio, "avatar": avatar_caminho},
            )
        except IntegrityError:
            raise ErroNegocio("Esse nome público já está a ser utilizado.") from None
        if avatar_caminho:
            self.sessao.execute(
                text("UPDATE perfis SET avatar_caminho = :avatar WHERE utilizador_id = :id"),
                {"id": utilizador_id, "avatar": avatar_caminho},
            )
        return antigo
