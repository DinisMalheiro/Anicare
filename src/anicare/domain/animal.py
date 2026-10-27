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


class EstadoAnimal(str, Enum):
    AVISTADO = "avistado"
    RESGATADO = "resgatado"
    ADOTADO = "adotado"


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
    estado: EstadoAnimal = EstadoAnimal.AVISTADO
    id: int | None = None
    criado_em: datetime | None = None

