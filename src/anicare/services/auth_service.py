import re

from werkzeug.security import check_password_hash, generate_password_hash

from anicare.domain.utilizador import Utilizador
from anicare.erros import ErroNegocio
from anicare.repositories.utilizador_repository import UtilizadorRepository

_RE_USERNAME = re.compile(r"[A-Za-z0-9_.-]{3,30}")
_RE_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
# Usado quando o utilizador não existe, para o tempo de resposta ser igual.
_HASH_FALSO = generate_password_hash("palavra-passe-falsa")


class AuthService:
    def __init__(self, utilizadores):
        self.utilizadores = utilizadores

    @classmethod
    def com_sessao(cls, sessao):
        return cls(UtilizadorRepository(sessao))

    def registar(self, username: str, email: str, password: str) -> int:
        """Regista um utilizador."""
        username = (username or "").strip()
        email = (email or "").strip()
        if not _RE_USERNAME.fullmatch(username):
            raise ErroNegocio(
                "O username deve ter 3 a 30 caracteres: letras, números, ponto, hífen ou _."
            )
        if len(email) > 254 or not _RE_EMAIL.fullmatch(email):
            raise ErroNegocio("Email inválido.")
        if not password or not (8 <= len(password) <= 128):
            raise ErroNegocio("A palavra-passe deve ter entre 8 e 128 caracteres.")
        return self.utilizadores.criar(username, email, generate_password_hash(password))

    def autenticar(self, valor: str, password: str) -> Utilizador | None:
        """Devolve o utilizador se as credenciais estiverem certas, senão None."""
        utilizador = self.utilizadores.obter_por_username_ou_email((valor or "").strip())
        hash_guardado = utilizador.password_hash if utilizador else _HASH_FALSO
        correta = check_password_hash(hash_guardado, password or "")
        if utilizador is None or not correta:
            return None
        return utilizador
