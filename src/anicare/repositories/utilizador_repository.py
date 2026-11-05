from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from anicare.domain.utilizador import Utilizador
from anicare.erros import ErroNegocio

_SELECT = """
    SELECT u.id, u.username::text AS username, u.email::text AS email,
           u.password_hash, r.nome AS role, u.ativo,
           host(u.ultimo_ip) AS ultimo_ip, u.ultimo_login_em, u.criado_em
    FROM utilizadores u
    JOIN roles r ON r.id = u.role_id
"""


class UtilizadorRepository:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def obter_por_id(self, utilizador_id: int) -> Utilizador | None:
        linha = self.sessao.execute(
            text(_SELECT + " WHERE u.id = :id"), {"id": utilizador_id}
        ).first()
        return Utilizador(**linha._mapping) if linha else None

    def obter_por_username_ou_email(self, valor: str) -> Utilizador | None:
        linha = self.sessao.execute(
            text(
                _SELECT
                + " WHERE u.username = CAST(:v AS citext) OR u.email = CAST(:v AS citext)"
            ),
            {"v": valor},
        ).first()
        return Utilizador(**linha._mapping) if linha else None

    def criar(self, username: str, email: str, password_hash: str) -> int:
        """Cria um utilizador com o role 'utilizador' (nunca administrador)."""
        try:
            return self.sessao.execute(
                text(
                    """
                    INSERT INTO utilizadores (role_id, username, email, password_hash)
                    VALUES ((SELECT id FROM roles WHERE nome = 'utilizador'),
                            :username, :email, :password_hash)
                    RETURNING id
                    """
                ),
                {"username": username, "email": email, "password_hash": password_hash},
            ).scalar_one()
        except IntegrityError:
            raise ErroNegocio("Esse username ou email já está registado.") from None

    def registar_login(self, utilizador_id: int, ip: str | None) -> None:
        self.sessao.execute(
            text(
                """
                UPDATE utilizadores
                SET ultimo_ip = CAST(:ip AS inet), ultimo_login_em = now()
                WHERE id = :id
                """
            ),
            {"id": utilizador_id, "ip": ip},
        )
