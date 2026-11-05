"""Ligação à base de dados PostgreSQL (SQLAlchemy)."""

from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from anicare import config

engine = create_engine(config.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def sessao():
    """Abre uma sessão: faz commit no fim e rollback se houver erro.

    Uso:
        with sessao() as s:
            PublicacaoRepository(s).listar_pins()
    """
    s = SessionLocal()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()


def verificar_ligacao() -> None:
    """Confirma no arranque que a BD responde e que o PostGIS está instalado.

    Falha logo, com uma mensagem clara, em vez de dar erros estranhos mais tarde.
    """
    try:
        with engine.connect() as ligacao:
            ligacao.execute(text("SELECT PostGIS_Version()"))
            ligacao.execute(text("SELECT 1 FROM ultimos_avistamentos LIMIT 1"))
    except SQLAlchemyError as erro:
        raise RuntimeError(
            "Não foi possível usar a base de dados. Confirma que:\n"
            "  1. o PostgreSQL está a correr e o DATABASE_URL do .env está certo;\n"
            "  2. a extensão PostGIS está instalada;\n"
            "  3. correste o docs/schema.sql nessa base de dados.\n"
            f"Detalhe: {erro.__cause__ or erro}"
        ) from erro
