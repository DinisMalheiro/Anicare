"""Confirma que o Python consegue falar com o PostgreSQL (precisa do .env e do docs/schema.sql)."""

from sqlalchemy import text

from anicare.database import engine


def test_ligacao_bd():
    with engine.connect() as ligacao:
        total = ligacao.execute(text("SELECT count(*) FROM publicacoes")).scalar()
    assert total >= 0


def test_postgis_instalado():
    with engine.connect() as ligacao:
        versao = ligacao.execute(text("SELECT PostGIS_Version()")).scalar()
    assert versao
