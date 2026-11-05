from anicare.domain.animal import Animal, EstadoAnimal
from anicare.domain.fotografia import Fotografia
from anicare.domain.publicacao import Publicacao
from anicare.erros import ErroDominio, ErroNegocio
from anicare.repositories.animal_repository import AnimalRepository
from anicare.repositories.fotografia_repository import FotografiaRepository
from anicare.repositories.publicacao_repository import PublicacaoRepository
from anicare.services.imagem_service import ImagemService, caminho_miniatura


def _texto(valor) -> str | None:
    valor = (valor or "").strip()
    return valor or None


class PublicacaoService:
    def __init__(self, publicacoes, animais, fotografias, imagens):
        self.publicacoes = publicacoes
        self.animais = animais
        self.fotografias = fotografias
        self.imagens = imagens

    @classmethod
    def com_sessao(cls, sessao):
        return cls(
            PublicacaoRepository(sessao),
            AnimalRepository(sessao),
            FotografiaRepository(sessao),
            ImagemService(),
        )

    # ---- leitura -------------------------------------------------------

    def listar_especies(self) -> list[dict]:
        return self.animais.listar_especies()

    def pins_geojson(self, especie_id: int | None = None, estado: str | None = None,
                     pesquisa: str | None = None, pagina: int = 1) -> dict:
        """Os pins do mapa em GeoJSON: um por animal, no último avistamento."""
        if estado:
            try:
                EstadoAnimal(estado)
            except ValueError:
                raise ErroNegocio("Estado inválido.") from None
        features = []
        for p in self.publicacoes.listar_pins(especie_id, estado, pesquisa, pagina=pagina):
            features.append(
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [p["longitude"], p["latitude"]]},
                    "properties": {
                        "id": p["id"],
                        "animal_id": p["animal_id"],
                        "titulo": p["titulo"],
                        "autor": p["autor"],
                        "autor_username": p["autor_username"],
                        "autor_avatar": p["autor_avatar"],
                        "nome": p["animal_nome"],
                        "especie": p["especie"],
                        "cor": p["cor"],
                        "porte": p["porte"],
                        "estado": p["estado"],
                        "data": p["data_avistamento"].isoformat(),
                        "pontos": int(p["pontos"]),
                        "foto": caminho_miniatura(p["foto"]) if p["foto"] else None,
                    },
                }
            )
        return {"type": "FeatureCollection", "features": features}

    def obter_detalhe(self, publicacao_id: int) -> dict | None:
        detalhe = self.publicacoes.obter_detalhe(publicacao_id)
        if detalhe is None:
            return None
        detalhe["fotos"] = self.fotografias.listar_por_publicacao(publicacao_id)
        detalhe["avistamentos"] = self.publicacoes.listar_avistamentos_do_animal(
            detalhe["animal_id"]
        )
        return detalhe

    def animais_proximos(
        self, latitude: float, longitude: float, raio_m: int = 1000, especie_id: int | None = None
    ) -> list[dict]:
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise ErroNegocio("Coordenadas inválidas.")
        resultado = []
        for a in self.publicacoes.animais_proximos(latitude, longitude, raio_m, especie_id):
            resultado.append(
                {
                    "animal_id": a["animal_id"],
                    "publicacao_id": a["publicacao_id"],
                    "titulo": a["titulo"],
                    "especie": a["especie"],
                    "cor": a["cor"],
                    "porte": a["porte"],
                    "distancia_m": round(a["distancia_m"]),
                    "foto": caminho_miniatura(a["foto"]) if a["foto"] else None,
                }
            )
        return resultado

    # ---- escrita -------------------------------------------------------

    def criar_avistamento(self, utilizador_id: int, dados: dict, ficheiro=None) -> int:
        """Cria uma publicação (e o animal, se for novo). Devolve o id da publicação.

        dados["animal_id"] preenchido = novo avistamento de um animal que já existe.
        """
        animal_id = dados.get("animal_id")
        try:
            novo_animal = None
            if animal_id is None:
                novo_animal = Animal(
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
                animal_id=animal_id,
                titulo=dados.get("titulo"),
                descricao=dados.get("descricao"),
                latitude=dados.get("latitude"),
                longitude=dados.get("longitude"),
                data_avistamento=dados.get("data_avistamento"),
            )
        except (ErroDominio, TypeError) as erro:
            raise ErroNegocio(str(erro) if isinstance(erro, ErroDominio) else "Dados inválidos.") from None

        if animal_id is not None and self.animais.obter_por_id(animal_id) is None:
            raise ErroNegocio("O animal escolhido não existe.")

        caminho = None
        if ficheiro is not None and getattr(ficheiro, "filename", ""):
            caminho = self.imagens.guardar(ficheiro)  # valida antes de tocar na BD
        try:
            if novo_animal is not None:
                publicacao.animal_id = self.animais.criar(novo_animal)
            publicacao_id = self.publicacoes.criar(publicacao)
            if caminho:
                self.fotografias.criar(Fotografia(caminho=caminho, publicacao_id=publicacao_id))
        except Exception:
            if caminho:
                self.imagens.apagar(caminho)  # não deixar ficheiros órfãos
            raise
        return publicacao_id

    def atualizar(self, publicacao_id: int, utilizador_id: int, dados: dict, ficheiro=None) -> None:
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
                utilizador_id=utilizador_id, animal_id=dados.get("animal_id"),
                titulo=dados.get("titulo"), descricao=dados.get("descricao"),
                latitude=dados.get("latitude"), longitude=dados.get("longitude"),
                data_avistamento=dados.get("data_avistamento"),
            )
        except (ErroDominio, TypeError) as erro:
            raise ErroNegocio(str(erro) if isinstance(erro, ErroDominio) else "Dados inválidos.") from None
        caminho = None
        antigo = None
        if ficheiro is not None and getattr(ficheiro, "filename", ""):
            caminho = self.imagens.guardar(ficheiro)
        try:
            if not self.publicacoes.atualizar(
                publicacao_id, utilizador_id,
                {"titulo": publicacao.titulo, "descricao": publicacao.descricao,
                 "lat": publicacao.latitude, "lon": publicacao.longitude,
                 "data": publicacao.data_avistamento},
            ):
                raise ErroNegocio("Não tens permissão para editar esta publicação.")
            if not self.animais.atualizar(dados["animal_id"], {
                "especie_id": animal.especie_id, "nome": animal.nome, "cor": animal.cor,
                "porte": animal.porte.value, "sexo": animal.sexo.value,
                "idade_aproximada": animal.idade_aproximada, "estado_saude": animal.estado_saude,
            }):
                raise ErroNegocio("O animal associado já não existe.")
            if caminho:
                antigo = self.fotografias.substituir_principal(publicacao_id, caminho)
        except Exception:
            if caminho:
                self.imagens.apagar(caminho)
            raise
        if antigo:
            self.imagens.apagar(antigo)

    def atualizar_estado(self, animal_id: int, estado: str) -> None:
        try:
            estado_animal = EstadoAnimal(estado)
        except ValueError:
            raise ErroNegocio("Estado inválido.") from None
        if self.animais.obter_por_id(animal_id) is None:
            raise ErroNegocio("O animal não existe.")
        self.animais.atualizar_estado(animal_id, estado_animal.value)
