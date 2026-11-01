from anicare.domain.pin import Pin
from anicare.erros import ErroDominio, ErroNegocio
from anicare.repositories.pin_repository import PinRepository


def _feature(p: dict) -> dict:
    """Um pin no formato GeoJSON, que o Leaflet sabe desenhar."""
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [p["longitude"], p["latitude"]]},
        "properties": {
            "id": p["id"],
            "titulo": p["titulo"],
            "descricao": p["descricao"],
            "especie": p["especie"],
            "data": p["criado_em"].isoformat(),
        },
    }


class PinService:
    def __init__(self, pins):
        self.pins = pins

    @classmethod
    def com_sessao(cls, sessao):
        return cls(PinRepository(sessao))

    def listar_geojson(self) -> dict:
        return {"type": "FeatureCollection", "features": [_feature(p) for p in self.pins.listar()]}

    def criar(self, dados: dict) -> dict:
        try:
            pin = Pin(
                titulo=dados.get("titulo"),
                especie=dados.get("especie"),
                latitude=dados.get("latitude"),
                longitude=dados.get("longitude"),
                descricao=dados.get("descricao"),
            )
        except ErroDominio as erro:
            raise ErroNegocio(str(erro)) from None
        return _feature(self.pins.criar(pin))
