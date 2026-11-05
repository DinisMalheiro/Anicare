from sqlalchemy import text
from sqlalchemy.orm import Session

from anicare.domain.animal import Animal


class AnimalRepository:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def listar_especies(self) -> list[dict]:
        linhas = self.sessao.execute(text("SELECT id, nome FROM especies ORDER BY nome"))
        return [dict(linha._mapping) for linha in linhas]

    def obter_por_id(self, animal_id: int) -> dict | None:
        linha = self.sessao.execute(
            text(
                """
                SELECT a.id, a.especie_id, a.nome, a.cor, a.porte::text AS porte,
                       a.sexo::text AS sexo, a.estado::text AS estado
                FROM animais a WHERE a.id = :id
                """
            ),
            {"id": animal_id},
        ).first()
        return dict(linha._mapping) if linha else None

    def criar(self, animal: Animal) -> int:
        return self.sessao.execute(
            text(
                """
                INSERT INTO animais (especie_id, nome, cor, porte, sexo,
                                     idade_aproximada, estado_saude, estado)
                VALUES (:especie_id, :nome, :cor,
                        CAST(:porte AS porte_animal), CAST(:sexo AS sexo_animal),
                        :idade, :saude, CAST(:estado AS estado_animal))
                RETURNING id
                """
            ),
            {
                "especie_id": animal.especie_id,
                "nome": animal.nome,
                "cor": animal.cor,
                "porte": animal.porte.value,
                "sexo": animal.sexo.value,
                "idade": animal.idade_aproximada,
                "saude": animal.estado_saude,
                "estado": animal.estado.value,
            },
        ).scalar_one()

    def atualizar_estado(self, animal_id: int, estado: str) -> None:
        self.sessao.execute(
            text("UPDATE animais SET estado = CAST(:estado AS estado_animal) WHERE id = :id"),
            {"id": animal_id, "estado": estado},
        )
