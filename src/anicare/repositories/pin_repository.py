"""Único sítio com SQL para os pins."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from anicare.domain.pin import Pin

_COLUNAS = "id, titulo, descricao, especie, latitude, longitude, criado_em"


class PinRepository:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar(self) -> list[dict]:
        linhas = self.sessao.execute(text(f"SELECT {_COLUNAS} FROM pins ORDER BY criado_em DESC"))
        return [dict(linha._mapping) for linha in linhas]

    def criar(self, pin: Pin) -> dict:
        linha = self.sessao.execute(
            text(
                f"""
                INSERT INTO pins (titulo, descricao, especie, latitude, longitude)
                VALUES (:titulo, :descricao, :especie, :latitude, :longitude)
                RETURNING {_COLUNAS}
                """
            ),
            {
                "titulo": pin.titulo,
                "descricao": pin.descricao,
                "especie": pin.especie,
                "latitude": pin.latitude,
                "longitude": pin.longitude,
            },
        ).one()
        return dict(linha._mapping)
