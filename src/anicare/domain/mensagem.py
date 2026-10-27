from dataclasses import dataclass
from datetime import datetime

from anicare.erros import ErroDominio


@dataclass
class Mensagem:
    remetente_id: int
    destinatario_id: int
    texto: str
    id: int | None = None
    criado_em: datetime | None = None
    lida_em: datetime | None = None


    @property
    def por_ler(self) -> bool:
        return self.lida_em is None
