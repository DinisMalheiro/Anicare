"""Exceções próprias da aplicação."""


class ErroDominio(ValueError):
    """Dados que violam as regras do modelo de domínio (ex.: latitude inválida)."""


class ErroNegocio(Exception):
    """Pedido que viola uma regra de negócio.

    A mensagem é escrita para o utilizador e pode ser mostrada no ecrã.
    """
