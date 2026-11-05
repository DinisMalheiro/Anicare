"""Regras dos votos. TODO (próximo passo).

Regras a implementar:
  - só utilizadores com sessão iniciada e conta ativa podem votar;
  - não se pode votar no próprio conteúdo;
  - um voto por pessoa em cada publicação/comentário (a BD já garante);
  - mudar o voto atualiza-o; votar o mesmo valor outra vez retira-o.
"""

from anicare.domain.voto import Voto
from anicare.erros import ErroNegocio


class VotoService:
    def __init__(self, votos):
        self.votos = votos

    def votar_publicacao(self, utilizador_id: int, publicacao_id: int, valor: int) -> None:
        if not self.votos.pode_votar_publicacao(utilizador_id, publicacao_id):
            raise ErroNegocio("Não podes votar na tua própria publicação.")
        self._votar("publicacao", utilizador_id, publicacao_id, valor)

    def votar_comentario(self, utilizador_id: int, comentario_id: int, valor: int) -> None:
        self._votar("comentario", utilizador_id, comentario_id, valor)

    def _votar(self, tipo, utilizador_id, conteudo_id, valor):
        try:
            Voto(utilizador_id=utilizador_id, valor=valor)
        except ValueError as erro:
            raise ErroNegocio(str(erro)) from None
        atual = self.votos.obter(tipo, utilizador_id, conteudo_id)
        if atual == valor:
            getattr(self.votos, f"retirar_voto_{tipo}")(utilizador_id, conteudo_id)
        else:
            getattr(self.votos, f"votar_{tipo}")(utilizador_id, conteudo_id, valor)
