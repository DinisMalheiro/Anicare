from dataclasses import dataclass
from datetime import datetime


@dataclass
class Utilizador:
    id: int | None
    username: str
    email: str
    password_hash: str
    criado_em: datetime | None = None
