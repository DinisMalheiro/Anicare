from dataclasses import dataclass
from datetime import datetime


@dataclass
class Utilizador:
    id: int | None
    username: str
    email: str
    password_hash: str
    role: str  # nome do role: "utilizador" ou "administrador"
    ativo: bool = True
    ultimo_ip: str | None = None
    ultimo_login_em: datetime | None = None
    criado_em: datetime | None = None

    @property
    def e_admin(self) -> bool:
        return self.role == "administrador"
