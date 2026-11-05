"""Administração. TODO: apagar conteúdo inadequado, criar/levantar bloqueios de contas e IPs.

Todas as rotas daqui devem exigir sessão iniciada E current_user.e_admin (verificado no
servidor, nunca só escondendo botões na página).
"""

from flask import Blueprint

bp = Blueprint("admin", __name__, url_prefix="/admin")
