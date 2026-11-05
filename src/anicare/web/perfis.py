"""Perfis de utilizador. TODO: página pública /perfis/<username> e edição do próprio perfil.

Usa a tabela perfis (nome_exibicao, bio, avatar_caminho). O avatar deve passar pelo
ImagemService, como as outras fotografias.
"""

from flask import Blueprint

bp = Blueprint("perfis", __name__, url_prefix="/perfis")
