"""Testes do modelo de domínio e do serviço. Não precisam de base de dados nem de .env.
pytest 
"C:\Users\Dinis\AppData\Local\Programs\Python\Python314\python.exe" -m pytest tests\test_pin_domain.py -v
"""

import pytest

from anicare.domain.pin import Pin
from anicare.erros import ErroDominio, ErroNegocio
from anicare.services.pin_service import PinService


def _pin(**alteracoes):
    dados = dict(titulo="Cão castanho", especie="cão", latitude=38.72, longitude=-9.14)
    dados.update(alteracoes)
    return Pin(**dados)


def test_pin_valido():
    assert _pin().titulo == "Cão castanho"


@pytest.mark.parametrize("lat, lon", [(91, 0), (-91, 0), (0, 181), (0, -181), (float("nan"), 0), ("x", 0), (None, 0)])
def test_coordenadas_invalidas(lat, lon):
    with pytest.raises(ErroDominio):
        _pin(latitude=lat, longitude=lon)


def test_titulo_obrigatorio():
    with pytest.raises(ErroDominio):
        _pin(titulo="   ")


def test_especie_tem_de_ser_conhecida():
    with pytest.raises(ErroDominio):
        _pin(especie="dragão")


class PinsFalso:
    def __init__(self):
        self.criados = []

    def criar(self, pin):
        self.criados.append(pin)
        from datetime import datetime
        return dict(id=1, titulo=pin.titulo, descricao=pin.descricao, especie=pin.especie,
                    latitude=pin.latitude, longitude=pin.longitude, criado_em=datetime.now())


def test_servico_cria_pin_valido():
    servico = PinService(PinsFalso())
    feature = servico.criar(dict(titulo="Gato", especie="gato", latitude=38.7, longitude=-9.1))
    assert feature["geometry"]["coordinates"] == [-9.1, 38.7]


def test_servico_recusa_dados_invalidos_sem_tocar_na_bd():
    pins = PinsFalso()
    with pytest.raises(ErroNegocio):
        PinService(pins).criar(dict(titulo="", especie="gato", latitude=38.7, longitude=-9.1))
    assert pins.criados == []
