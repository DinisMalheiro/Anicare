"""Configuração da aplicação, lida do ficheiro .env na raiz do projeto."""

import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[2]  # a pasta anicare/
load_dotenv(RAIZ / ".env")


def _obrigatoria(nome: str) -> str:
    valor = os.environ.get(nome)
    if not valor:
        raise RuntimeError(
            f"Falta a variável {nome} no ficheiro .env (vê o .env.example)."
        )
    return valor


def _ativa(nome: str) -> bool:
    return os.environ.get(nome, "0") == "1"


DATABASE_URL = _obrigatoria("DATABASE_URL")
SECRET_KEY = _obrigatoria("SECRET_KEY")

DEBUG = _ativa("DEBUG")
CONFIAR_PROXY = _ativa("CONFIAR_PROXY")  # 1 quando está atrás do Caddy/Nginx
COOKIES_SEGUROS = _ativa("COOKIES_SEGUROS")  # 1 quando o site usa HTTPS

PASTA_UPLOADS = Path(os.environ.get("PASTA_UPLOADS") or RAIZ / "data" / "uploads")
TAMANHO_MAXIMO_UPLOAD = 10 * 1024 * 1024  # 10 MB
