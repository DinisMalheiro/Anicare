"""Persistência das mensagens privadas."""
from sqlalchemy import text
from sqlalchemy.orm import Session


class MensagemRepository:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def enviar(self, mensagem) -> int:
        return self.sessao.execute(
            text(
                """
                INSERT INTO mensagens (remetente_id, destinatario_id, texto)
                VALUES (:remetente, :destinatario, :texto) RETURNING id
                """
            ),
            {"remetente": mensagem.remetente_id, "destinatario": mensagem.destinatario_id,
             "texto": mensagem.texto},
        ).scalar_one()

    def utilizador_ativo(self, utilizador_id: int) -> bool:
        return self.sessao.execute(
            text("SELECT 1 FROM utilizadores WHERE id = :id AND ativo"), {"id": utilizador_id}
        ).first() is not None

    def obter_utilizador(self, utilizador_id: int) -> dict | None:
        linha = self.sessao.execute(
            text(
                """
                SELECT u.id, COALESCE(p.nome_exibicao, u.username) AS nome_exibicao,
                       u.username
                FROM utilizadores u LEFT JOIN perfis p ON p.utilizador_id = u.id
                WHERE u.id = :id AND u.ativo
                """
            ),
            {"id": utilizador_id},
        ).first()
        return dict(linha._mapping) if linha else None

    def conversa(self, utilizador_id: int, outro_id: int) -> list[dict]:
        linhas = self.sessao.execute(
            text(
                """
                SELECT m.*, ur.username AS remetente_username,
                       ud.username AS destinatario_username,
                       COALESCE(pr.nome_exibicao, ur.username) AS remetente,
                       COALESCE(pd.nome_exibicao, ud.username) AS destinatario
                FROM mensagens m
                JOIN utilizadores ur ON ur.id = m.remetente_id
                JOIN utilizadores ud ON ud.id = m.destinatario_id
                LEFT JOIN perfis pr ON pr.utilizador_id = ur.id
                LEFT JOIN perfis pd ON pd.utilizador_id = ud.id
                WHERE (m.remetente_id = :uid AND m.destinatario_id = :outro)
                   OR (m.remetente_id = :outro AND m.destinatario_id = :uid)
                ORDER BY m.criado_em
                """
            ), {"uid": utilizador_id, "outro": outro_id},
        )
        return [dict(linha._mapping) for linha in linhas]

    def conversas(self, utilizador_id: int) -> list[dict]:
        linhas = self.sessao.execute(
            text(
                """
                SELECT u.id, u.username,
                       COALESCE(p.nome_exibicao, u.username) AS nome_exibicao,
                       count(m.id) FILTER
                    (WHERE m.destinatario_id = :uid AND m.lida_em IS NULL) AS por_ler,
                    max(m.criado_em) AS ultima_mensagem
                FROM mensagens m
                JOIN utilizadores u ON u.id = CASE
                    WHEN m.remetente_id = :uid THEN m.destinatario_id
                    ELSE m.remetente_id END
                LEFT JOIN perfis p ON p.utilizador_id = u.id
                WHERE m.remetente_id = :uid OR m.destinatario_id = :uid
                GROUP BY u.id, u.username, p.nome_exibicao ORDER BY ultima_mensagem DESC
                """
            ), {"uid": utilizador_id},
        )
        return [dict(linha._mapping) for linha in linhas]

    def marcar_conversa_como_lida(self, utilizador_id: int, outro_id: int) -> None:
        self.sessao.execute(
            text(
                """
                UPDATE mensagens SET lida_em = now()
                WHERE destinatario_id = :uid AND remetente_id = :outro AND lida_em IS NULL
                """
            ), {"uid": utilizador_id, "outro": outro_id},
        )
