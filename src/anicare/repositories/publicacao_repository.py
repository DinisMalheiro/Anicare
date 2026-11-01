from sqlalchemy import text
from sqlalchemy.orm import Session

from anicare.domain.publicacao import Publicacao

_LOCAL = "ST_Y(p.localizacao::geometry) AS latitude, ST_X(p.localizacao::geometry) AS longitude"


class PublicacaoRepository:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar_pins(self) -> list[dict]:
        """Todas as publicações (um pin por avistamento)."""
        linhas = self.sessao.execute(
            text(
                f"""
                SELECT p.id, p.animal_id, p.titulo, p.data_avistamento, {_LOCAL},
                       e.nome AS especie, a.cor, a.porte::text AS porte
                FROM publicacoes p
                JOIN animais a ON a.id = p.animal_id
                JOIN especies e ON e.id = a.especie_id
                ORDER BY p.data_avistamento DESC
                """
            )
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
                SELECT p.id, p.utilizador_id, u.username::text AS autor, p.animal_id,
                       p.titulo, p.descricao, p.data_avistamento, p.criado_em, {_LOCAL},
                       e.nome AS especie, a.nome AS animal_nome, a.cor,
                       a.porte::text AS porte, a.sexo::text AS sexo,
                       a.idade_aproximada, a.estado_saude
                FROM publicacoes p
                JOIN utilizadores u ON u.id = p.utilizador_id
                JOIN animais a ON a.id = p.animal_id
                JOIN especies e ON e.id = a.especie_id
                WHERE p.id = :id
                """
            ),
            {"id": publicacao_id},
        ).first()
        return dict(linha._mapping) if linha else None

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
