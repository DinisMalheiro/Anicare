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

    def __post_init__(self):
        if self.remetente_id == self.destinatario_id:
            raise ErroDominio("Não podes enviar mensagens a ti próprio.")
        self.texto = (self.texto or "").strip()
        if not self.texto:
            raise ErroDominio("A mensagem não pode estar vazia.")
        if len(self.texto) > 5000:
            raise ErroDominio("A mensagem tem demasiados caracteres (máximo 5000).")

    @property
    def por_ler(self) -> bool:
        return self.lida_em is None
