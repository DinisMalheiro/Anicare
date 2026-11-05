"""Mensagens privadas entre utilizadores.

TODO (funcionalidade futura): implementar com SQL como nos outros repositórios.

    enviar(mensagem: Mensagem) -> id
    listar_conversa(utilizador_a, utilizador_b)   (ordenada por criado_em)
    contar_por_ler(utilizador_id)                 (lida_em IS NULL)
    marcar_como_lida(mensagem_id)
"""

from sqlalchemy.orm import Session


class MensagemRepository:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def enviar(self, mensagem) -> int:
        raise NotImplementedError("Por implementar.")
