from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from anicare.erros import ErroDominio


class Porte(str, Enum):
    PEQUENO = "pequeno"
    MEDIO = "medio"
    GRANDE = "grande"


class Sexo(str, Enum):
    MACHO = "macho"
    FEMEA = "femea"
    DESCONHECIDO = "desconhecido"


def _enum(classe, valor, nome: str):
    try:
        return classe(valor)
    except ValueError:
        raise ErroDominio(f"Valor inválido para {nome}.") from None


@dataclass
class Animal:
    especie_id: int
    cor: str
    porte: Porte
    sexo: Sexo = Sexo.DESCONHECIDO
    nome: str | None = None
    idade_aproximada: str | None = None
    estado_saude: str | None = None
    id: int | None = None
    criado_em: datetime | None = None

    def __post_init__(self):
        if not isinstance(self.especie_id, int):
            raise ErroDominio("Escolhe a espécie do animal.")
        self.cor = (self.cor or "").strip()
        if not self.cor:
            raise ErroDominio("A cor do animal é obrigatória.")
        if len(self.cor) > 50:
            raise ErroDominio("A cor tem demasiados caracteres (máximo 50).")
        self.porte = _enum(Porte, self.porte, "porte")
        self.sexo = _enum(Sexo, self.sexo, "sexo")
