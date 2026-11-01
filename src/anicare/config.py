"""Configuração da aplicação, lida do ficheiro .env na raiz do projeto."""

import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[2]  # a pasta anicare/
load_dotenv(RAIZ / ".env")


def _obrigatoria(nome: str) -> str:
    valor = os.environ.get(nome)
    if not valor:
        raise RuntimeError(f"Falta a variável {nome} no ficheiro .env (vê o .env.example).")
    return valor


DATABASE_URL = _obrigatoria("DATABASE_URL")
SECRET_KEY = _obrigatoria("SECRET_KEY")
DEBUG = os.environ.get("DEBUG", "0") == "1"
