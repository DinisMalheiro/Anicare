from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from anicare.domain.publicacao import Publicacao

_LOCAL = "ST_Y(p.localizacao::geometry) AS latitude, ST_X(p.localizacao::geometry) AS longitude"
_PONTOS = (
    "COALESCE((SELECT SUM(v.valor) FROM votos_publicacoes v "
    "WHERE v.publicacao_id = p.id), 0) AS pontos"
)
_PRIMEIRA_FOTO = (
    "(SELECT f.caminho FROM fotografias f WHERE f.publicacao_id = p.id "
    "ORDER BY f.ordem, f.id LIMIT 1) AS foto"
)


class PublicacaoRepository:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar_pins(
        self, especie_id: int | None = None, estado: str | None = None,
        pesquisa: str | None = None, limite: int = 100, pagina: int = 1
    ) -> list[dict]:
        """Um pin por animal: usa SEMPRE a vista ultimos_avistamentos (sem repetições)."""
        filtros, params = [], {}
        if especie_id is not None:
            filtros.append("a.especie_id = :especie_id")
            params["especie_id"] = especie_id
        if estado:
            filtros.append("a.estado = CAST(:estado AS estado_animal)")
            params["estado"] = estado
        if pesquisa:
            filtros.append("(p.titulo ILIKE :pesquisa OR p.descricao ILIKE :pesquisa OR a.cor ILIKE :pesquisa)")
            params["pesquisa"] = f"%{pesquisa.strip()}%"
        onde = ("WHERE " + " AND ".join(filtros)) if filtros else ""
        params["limite"] = max(1, min(limite, 100))
        params["offset"] = max(0, pagina - 1) * params["limite"]
        linhas = self.sessao.execute(
            text(
                f"""
                SELECT p.id, p.animal_id, p.titulo, p.data_avistamento, {_LOCAL},
                       COALESCE(perfil.nome_exibicao, u.username::text) AS autor,
                       u.username::text AS autor_username,
                       perfil.avatar_caminho AS autor_avatar,
                       e.nome AS especie, a.nome AS animal_nome, a.cor,
                       a.porte::text AS porte, a.estado::text AS estado,
                       {_PRIMEIRA_FOTO}, {_PONTOS}
                FROM ultimos_avistamentos p
                JOIN animais a ON a.id = p.animal_id
                JOIN especies e ON e.id = a.especie_id
                JOIN utilizadores u ON u.id = p.utilizador_id
                LEFT JOIN perfis perfil ON perfil.utilizador_id = u.id
                {onde}
                ORDER BY p.data_avistamento DESC
                LIMIT :limite OFFSET :offset
                """
            ),
            params,
        )
        return [dict(linha._mapping) for linha in linhas]

    def existe(self, publicacao_id: int) -> bool:
        return (
            self.sessao.execute(
                text("SELECT 1 FROM publicacoes WHERE id = :id"), {"id": publicacao_id}
            ).first()
            is not None
        )

    def obter_detalhe(self, publicacao_id: int) -> dict | None:
        linha = self.sessao.execute(
            text(
                f"""
                SELECT p.id, p.utilizador_id,
                       COALESCE(perfil.nome_exibicao, u.username::text) AS autor,
                       u.username::text AS autor_username,
                       perfil.avatar_caminho AS autor_avatar, p.animal_id,
                       p.titulo, p.descricao, p.data_avistamento, p.criado_em,
                       p.atualizado_em, {_LOCAL},
                       a.especie_id, e.nome AS especie, a.nome AS animal_nome, a.cor,
                       a.porte::text AS porte, a.sexo::text AS sexo,
                       a.idade_aproximada, a.estado_saude, a.estado::text AS estado,
                       {_PONTOS}
                FROM publicacoes p
                JOIN utilizadores u ON u.id = p.utilizador_id
                LEFT JOIN perfis perfil ON perfil.utilizador_id = u.id
                JOIN animais a ON a.id = p.animal_id
                JOIN especies e ON e.id = a.especie_id
                WHERE p.id = :id
                """
            ),
            {"id": publicacao_id},
        ).first()
        return dict(linha._mapping) if linha else None

    def listar_avistamentos_do_animal(self, animal_id: int) -> list[dict]:
        """Todos os avistamentos de um animal, por ordem cronológica (o seu caminho)."""
        linhas = self.sessao.execute(
            text(
                f"""
                SELECT p.id, p.titulo, p.data_avistamento, {_LOCAL}
                FROM publicacoes p
                WHERE p.animal_id = :animal_id
                ORDER BY p.data_avistamento, p.id
                """
            ),
            {"animal_id": animal_id},
        )
        return [dict(linha._mapping) for linha in linhas]

    def animais_proximos(
        self, latitude: float, longitude: float, raio_m: int, especie_id: int | None = None
    ) -> list[dict]:
        """Animais ainda 'avistados' perto de um ponto (para evitar duplicados)."""
        extra = "AND a.especie_id = :especie_id" if especie_id is not None else ""
        params = {"lat": latitude, "lon": longitude, "raio": raio_m}
        if especie_id is not None:
            params["especie_id"] = especie_id
        linhas = self.sessao.execute(
            text(
                f"""
                WITH ponto AS (
                    SELECT CAST(ST_SetSRID(ST_MakePoint(CAST(:lon AS double precision),
                                                        CAST(:lat AS double precision)), 4326)
                                AS geography) AS g
                )
                SELECT p.animal_id, p.id AS publicacao_id, p.titulo, e.nome AS especie,
                       a.cor, a.porte::text AS porte,
                       ST_Distance(p.localizacao, ponto.g) AS distancia_m,
                       {_PRIMEIRA_FOTO}
                FROM ponto
                CROSS JOIN ultimos_avistamentos p
                JOIN animais a ON a.id = p.animal_id
                JOIN especies e ON e.id = a.especie_id
                WHERE a.estado = 'avistado'
                  AND ST_DWithin(p.localizacao, ponto.g, :raio)
                  {extra}
                ORDER BY distancia_m
                LIMIT 10
                """
            ),
            params,
        )
        return [dict(linha._mapping) for linha in linhas]

    def criar(self, publicacao: Publicacao) -> int:
        if publicacao.animal_id is None:
            raise ValueError("A publicação precisa de um animal_id antes de ser gravada.")
        return self.sessao.execute(
            text(
                """
                INSERT INTO publicacoes (utilizador_id, animal_id, titulo, descricao,
                                         localizacao, data_avistamento)
                VALUES (:utilizador_id, :animal_id, :titulo, :descricao,
                        CAST(ST_SetSRID(ST_MakePoint(CAST(:lon AS double precision),
                                                     CAST(:lat AS double precision)), 4326)
                             AS geography),
                        :data)
                RETURNING id
                """
            ),
            {
                "utilizador_id": publicacao.utilizador_id,
                "animal_id": publicacao.animal_id,
                "titulo": publicacao.titulo,
                "descricao": publicacao.descricao,
                "lat": publicacao.latitude,
                "lon": publicacao.longitude,
                "data": publicacao.data_avistamento,
            },
        ).scalar_one()

    def atualizar(self, publicacao_id: int, utilizador_id: int, dados: dict) -> bool:
        resultado = self.sessao.execute(
            text(
                """
                UPDATE publicacoes
                SET titulo = :titulo, descricao = :descricao, localizacao =
                    CAST(ST_SetSRID(ST_MakePoint(:lon, :lat), 4326) AS geography),
                    data_avistamento = :data, atualizado_em = now()
                WHERE id = :id AND utilizador_id = :uid
                """
            ),
            {"id": publicacao_id, "uid": utilizador_id, **dados},
        )
        return resultado.rowcount == 1

    def apagar(self, publicacao_id: int) -> bool:
        resultado = self.sessao.execute(
            text("DELETE FROM publicacoes WHERE id = :id"), {"id": publicacao_id}
        )
        return resultado.rowcount == 1

    def autoriza(self, publicacao_id: int, utilizador_id: int) -> bool:
        return self.sessao.execute(
            text("SELECT 1 FROM publicacoes WHERE id = :id AND utilizador_id = :uid"),
            {"id": publicacao_id, "uid": utilizador_id},
        ).first() is not None
