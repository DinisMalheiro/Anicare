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
    """Abre uma sessão: commit no fim, rollback se houver erro."""
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
    """Falha logo no arranque, com uma mensagem clara, se a BD não estiver pronta."""
    try:
        with engine.connect() as ligacao:
            ligacao.execute(text("SELECT 1 FROM pins LIMIT 1"))
    except SQLAlchemyError as erro:
        raise RuntimeError(
            "Não foi possível usar a base de dados. Confirma que:\n"
            " O PostgreSQL está a correr e o DATABASE_URL do .env está certo;\n"
            f"Detalhe: {erro.__cause__ or erro}"
        ) from erro
