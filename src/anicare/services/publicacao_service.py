from anicare.domain.animal import Animal
from anicare.domain.publicacao import Publicacao
from anicare.erros import ErroDominio, ErroNegocio
from anicare.repositories.animal_repository import AnimalRepository
from anicare.repositories.publicacao_repository import PublicacaoRepository


def _texto(valor) -> str | None:
    valor = (valor or "").strip()
    return valor or None


class PublicacaoService:
    def __init__(self, publicacoes, animais):
        self.publicacoes = publicacoes
        self.animais = animais

    @classmethod
    def com_sessao(cls, sessao):
        return cls(PublicacaoRepository(sessao), AnimalRepository(sessao))

    # ---- leitura -------------------------------------------------------

    def listar_especies(self) -> list[dict]:
        return self.animais.listar_especies()

    def pins_geojson(self) -> dict:
        """Os pins do mapa em GeoJSON: um por avistamento."""
        features = []
        for p in self.publicacoes.listar_pins():
            features.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [p["longitude"], p["latitude"]]},
                    "properties": {
                        "id": p["id"],
                        "titulo": p["titulo"],
                        "especie": p["especie"],
                        "cor": p["cor"],
                        "porte": p["porte"],
                        "data": p["data_avistamento"].isoformat(),
                    },
                }
            )
        return {"type": "FeatureCollection", "features": features}

    def obter_detalhe(self, publicacao_id: int) -> dict | None:
        detalhe = self.publicacoes.obter_detalhe(publicacao_id)
        if detalhe is None:
            return None
        return detalhe

    # ---- escrita -------------------------------------------------------

    def criar_avistamento(self, utilizador_id: int, dados: dict) -> int:
        """Cria o animal e a publicação (o avistamento). Devolve o id da publicação."""
        try:
            animal = Animal(
                especie_id=dados.get("especie_id"),
                cor=dados.get("cor"),
                porte=dados.get("porte"),
                sexo=dados.get("sexo") or "desconhecido",
                nome=_texto(dados.get("nome")),
                idade_aproximada=_texto(dados.get("idade_aproximada")),
                estado_saude=_texto(dados.get("estado_saude")),
            )
            publicacao = Publicacao(
                utilizador_id=utilizador_id,
                animal_id=None,
                titulo=dados.get("titulo"),
                descricao=dados.get("descricao"),
                latitude=dados.get("latitude"),
                longitude=dados.get("longitude"),
                data_avistamento=dados.get("data_avistamento"),
            )
        except (ErroDominio, TypeError) as erro:
            raise ErroNegocio(str(erro) if isinstance(erro, ErroDominio) else "Dados inválidos.") from None

        publicacao.animal_id = self.animais.criar(animal)
        return self.publicacoes.criar(publicacao)
