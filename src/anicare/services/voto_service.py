"""Regras dos votos. TODO (próximo passo).

Regras a implementar:
  - só utilizadores com sessão iniciada e conta ativa podem votar;
  - não se pode votar no próprio conteúdo;
  - um voto por pessoa em cada publicação/comentário (a BD já garante);
  - mudar o voto atualiza-o; votar o mesmo valor outra vez retira-o.
"""

from anicare.domain.voto import Voto


class VotoService:
    def __init__(self, votos):
        self.votos = votos

    def votar_publicacao(self, utilizador_id: int, publicacao_id: int, valor: int) -> None:
        Voto(utilizador_id=utilizador_id, valor=valor)  # valida o valor (+1 / -1)
        raise NotImplementedError("Por implementar.")
