"""Mensagens privadas. TODO (funcionalidade futura): caixa de entrada, conversa e envio."""

from flask import Blueprint

bp = Blueprint("mensagens", __name__, url_prefix="/mensagens")
