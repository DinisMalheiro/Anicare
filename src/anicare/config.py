"""Configuração, lida do ficheiro .env na raiz do projeto."""

import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[2]
load_dotenv(RAIZ / ".env")

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Falta a variável DATABASE_URL no ficheiro .env (vê o .env.example).")

DEBUG = os.environ.get("DEBUG", "0") == "1"
