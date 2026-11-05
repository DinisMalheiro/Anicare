"""Regras das mensagens privadas. TODO (funcionalidade futura).

Regras a implementar:
  - o destinatário tem de existir e estar ativo;
  - utilizadores bloqueados não podem enviar mensagens;
  - limitar o número de mensagens por minuto (contra spam);
  - o administrador não lê mensagens privadas, a não ser numa denúncia.
"""

from anicare.domain.mensagem import Mensagem
from anicare.erros import ErroNegocio


class MensagemService:
    def __init__(self, mensagens):
        self.mensagens = mensagens

    def enviar(self, remetente_id: int, destinatario_id: int, texto: str) -> int:
        if not self.mensagens.utilizador_ativo(destinatario_id):
            raise ErroNegocio("O destinatário não existe ou está inativo.")
        try:
            mensagem = Mensagem(
                remetente_id=remetente_id, destinatario_id=destinatario_id, texto=texto
            )
        except ValueError as erro:
            raise ErroNegocio(str(erro)) from None
        return self.mensagens.enviar(mensagem)
