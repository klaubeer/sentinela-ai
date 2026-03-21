"""Testes do decorator @observe()."""

import pytest
import respx
import httpx
from sentinela import Sentinela, observe


BASE_URL = "http://localhost:8000"


@pytest.fixture
def sentinela():
    return Sentinela(api_key="sk-teste", projeto="projeto-teste", base_url=BASE_URL)


@respx.mock
@pytest.mark.asyncio
async def test_observe_captura_output(sentinela):
    """Decorator deve capturar o output e enviar o trace."""
    rota = respx.post(f"{BASE_URL}/traces").mock(return_value=httpx.Response(201))

    @sentinela.observe(nome="funcao-teste")
    async def funcao(x: str) -> str:
        return f"resposta: {x}"

    resultado = await funcao("oi")

    assert resultado == "resposta: oi"
    assert rota.called


@respx.mock
@pytest.mark.asyncio
async def test_observe_captura_erro(sentinela):
    """Decorator deve registrar erros sem suprimi-los."""
    respx.post(f"{BASE_URL}/traces").mock(return_value=httpx.Response(201))

    @sentinela.observe()
    async def funcao_com_erro():
        raise ValueError("erro de teste")

    with pytest.raises(ValueError, match="erro de teste"):
        await funcao_com_erro()


@respx.mock
@pytest.mark.asyncio
async def test_observe_falha_servidor_nao_propaga(sentinela):
    """Falha no servidor Sentinela não deve afetar a função instrumentada."""
    respx.post(f"{BASE_URL}/traces").mock(return_value=httpx.Response(500))

    @sentinela.observe()
    async def funcao() -> str:
        return "ok"

    resultado = await funcao()
    assert resultado == "ok"
