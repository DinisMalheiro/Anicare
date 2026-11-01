"""Exceções próprias da aplicação."""


class ErroDominio(ValueError):
    """Dados que violam as regras do modelo (ex.: latitude inválida)."""


class ErroNegocio(Exception):
    """Pedido recusado. A mensagem é escrita para o utilizador."""
