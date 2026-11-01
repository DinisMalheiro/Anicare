"""Testes do modelo de domínio. Não precisam de base de dados nem de .env."""

from datetime import datetime, timedelta, timezone

import pytest

from anicare.domain.animal import Animal, Porte
from anicare.domain.publicacao import Publicacao
from anicare.erros import ErroDominio


def _publicacao(**alteracoes):
    dados = dict(
        utilizador_id=1, animal_id=1, titulo="Cão castanho", latitude=38.72,
        longitude=-9.14, data_avistamento=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    dados.update(alteracoes)
    return Publicacao(**dados)


def test_publicacao_valida():
    assert _publicacao().titulo == "Cão castanho"


@pytest.mark.parametrize("lat, lon", [(91, 0), (-91, 0), (0, 181), (0, -181), (float("nan"), 0)])
def test_coordenadas_invalidas(lat, lon):
    with pytest.raises(ErroDominio):
        _publicacao(latitude=lat, longitude=lon)


def test_titulo_obrigatorio():
    with pytest.raises(ErroDominio):
        _publicacao(titulo="   ")


def test_data_no_futuro_recusada():
    with pytest.raises(ErroDominio):
        _publicacao(data_avistamento=datetime.now(timezone.utc) + timedelta(days=1))


def test_data_sem_fuso_horario_e_aceite():
    p = _publicacao(data_avistamento=datetime.now() - timedelta(hours=2))
    assert p.data_avistamento.tzinfo is not None


def test_animal_exige_cor_e_porte_valido():
    with pytest.raises(ErroDominio):
        Animal(especie_id=1, cor="", porte="grande")
    with pytest.raises(ErroDominio):
        Animal(especie_id=1, cor="preto", porte="gigante")
    assert Animal(especie_id=1, cor="preto", porte="grande").porte is Porte.GRANDE
