"""Regras das mensagens privadas. TODO (funcionalidade futura).

Regras a implementar:
  - o destinatário tem de existir e estar ativo;
  - utilizadores bloqueados não podem enviar mensagens;
  - limitar o número de mensagens por minuto (contra spam);
  - o administrador não lê mensagens privadas, a não ser numa denúncia.
"""

from anicare.domain.mensagem import Mensagem


class MensagemService:
    def __init__(self, mensagens):
        self.mensagens = mensagens

    def enviar(self, remetente_id: int, destinatario_id: int, texto: str) -> int:
        Mensagem(remetente_id=remetente_id, destinatario_id=destinatario_id, texto=texto)
        raise NotImplementedError("Por implementar.")
