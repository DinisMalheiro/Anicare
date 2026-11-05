from sqlalchemy import text
from sqlalchemy.orm import Session
from anicare.domain.bloqueio import Bloqueio


class BloqueioRepository:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def procurar_ativo(self, ip: str | None, utilizador_id: int | None) -> str | None:
        """Devolve o motivo do bloqueio ativo desta conta ou deste IP (ou None).

        Um bloqueio está ativo se não expirou. O operador  ip >>= x  significa
        "o IP/intervalo bloqueado contém este IP".
        """
        condicoes, params = [], {}
        if ip:
            condicoes.append("ip >>= CAST(:ip AS inet)")
            params["ip"] = ip
        if utilizador_id is not None:
            condicoes.append("utilizador_id = :uid")
            params["uid"] = utilizador_id
        if not condicoes:
            return None
        return self.sessao.execute(
            text(
                f"""
                SELECT ban_motivo FROM bloqueios
                WHERE (expira_em IS NULL OR expira_em > now())
                  AND ({' OR '.join(condicoes)})
                ORDER BY criado_em DESC
                LIMIT 1
                """
            ),
            params,
        ).scalar()

    def criar(self, bloqueio: Bloqueio) -> int:
        return self.sessao.execute(
            text(
                """
                INSERT INTO bloqueios (utilizador_id, ip, ban_motivo, criado_por, expira_em)
                VALUES (:uid, CAST(:ip AS inet), :motivo, :criado_por, :expira)
                RETURNING id
                """
            ),
            {"uid": bloqueio.utilizador_id, "ip": bloqueio.ip, "motivo": bloqueio.ban_motivo,
             "criado_por": bloqueio.criado_por, "expira": bloqueio.expira_em},
        ).scalar_one()
