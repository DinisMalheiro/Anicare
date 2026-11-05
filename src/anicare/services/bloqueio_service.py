from anicare.domain.bloqueio import normalizar_ip
from anicare.repositories.bloqueio_repository import BloqueioRepository


class BloqueioService:
    def __init__(self, bloqueios):
        self.bloqueios = bloqueios

    @classmethod
    def com_sessao(cls, sessao):
        return cls(BloqueioRepository(sessao))

    def verificar(self, ip: str | None, utilizador_id: int | None) -> str | None:
        """Devolve o motivo se esta conta ou este IP estiver bloqueado, senão None.

        Corre em cada pedido (ver web/__init__.py). Se ficar lento, guardar o
        resultado em memória durante alguns segundos.
        """
        return self.bloqueios.procurar_ativo(normalizar_ip(ip), utilizador_id)
