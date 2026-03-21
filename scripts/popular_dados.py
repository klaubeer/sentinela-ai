"""Script de seed — popula o banco com dados fake realistas para demo.

Uso:
    python scripts/popular_dados.py
    # ou via Docker:
    make seed
"""

from __future__ import annotations

import asyncio
import random
import uuid
from datetime import datetime, timedelta

import httpx

SERVIDOR_URL = "http://localhost:8000"

# ── Dados de exemplo ──────────────────────────────────────────────────────────

_PROJETOS = ["vertice-ai", "postador"]

_PERGUNTAS_VERTICE = [
    "Qual o prazo de entrega para São Paulo?",
    "Como faço para rastrear meu pedido?",
    "Vocês entregam aos sábados?",
    "Qual a política de devolução?",
    "O produto tem garantia?",
    "Como cancelar um pedido?",
    "Quais são as formas de pagamento?",
    "Tem frete grátis?",
    "Como trocar um produto com defeito?",
    "Qual o horário de atendimento?",
]

_RESPOSTAS_VERTICE = [
    "O prazo de entrega para São Paulo é de 2 a 3 dias úteis.",
    "Você pode rastrear seu pedido pelo site, na seção 'Meus Pedidos'.",
    "Sim, realizamos entregas aos sábados em capitais e regiões metropolitanas.",
    "Aceitamos devoluções em até 7 dias após o recebimento, sem custo adicional.",
    "Todos os produtos têm garantia mínima de 90 dias conforme o CDC.",
    "Para cancelar, acesse 'Meus Pedidos' e clique em 'Cancelar' em até 24h após a compra.",
    "Aceitamos cartão de crédito, boleto, Pix e parcelamento em até 12x.",
    "Frete grátis para compras acima de R$ 199 para todo o Brasil.",
    "Entre em contato pelo chat ou telefone 0800 com nota fiscal em mãos.",
    "Atendemos de segunda a sexta das 8h às 20h e sábados das 9h às 15h.",
]

_CONTEXTOS_VERTICE = [
    "Prazo padrão SP: 2-3 dias úteis. Interior: 4-5 dias úteis.",
    "Rastreamento disponível no site em 'Meus Pedidos' com código de rastreio.",
    "Entrega sábado: disponível em capitais e regiões metropolitanas.",
    "Política de devolução: até 7 dias corridos, frete de devolução gratuito.",
    "Garantia legal: 90 dias para produtos não duráveis, 1 ano para duráveis.",
    "Cancelamento: disponível em até 24h após aprovação do pagamento.",
    "Formas de pagamento: crédito, débito, boleto, Pix, parcelamento até 12x sem juros.",
    "Frete grátis: compras acima de R$ 199,00 para todo o Brasil.",
    "Troca por defeito: acionar em até 30 dias com nota fiscal.",
    "Horário: Seg-Sex 8h-20h, Sáb 9h-15h.",
]

_BRIEFINGS_POSTADOR = [
    "Lançamento da nova linha de produtos sustentáveis",
    "Resultado do Q3: crescimento de 40% em receita",
    "Contratando engenheiros de ML — venha trabalhar conosco",
    "Parceria estratégica com empresa líder do setor",
    "5 anos de empresa: obrigado a todos os clientes",
]

_POSTS_GERADOS = [
    "🌱 Sustentabilidade não é tendência, é responsabilidade. Hoje lançamos nossa nova linha de produtos 100% sustentáveis. Cada compra planta uma árvore. #Sustentabilidade #Inovação",
    "📈 Q3 encerrado com chave de ouro! Crescimento de 40% em receita, impulsionado pela nossa nova estratégia de produto. Gratidão à equipe incrível que tornou isso possível.",
    "🚀 Estamos contratando! Buscamos Engenheiros de ML apaixonados por resolver problemas reais com IA. Stack: Python, PyTorch, AWS. Mande seu LinkedIn nos comentários!",
    "🤝 Grande notícia: firmamos parceria estratégica com [Empresa Líder]. Juntos, vamos revolucionar a experiência do cliente no setor. Detalhes em breve!",
    "🎂 5 anos! O que começou na garagem de casa hoje impacta milhares de clientes. Obrigado a cada um que confiou em nós nessa jornada. O melhor ainda está por vir.",
]


# ── Geração de traces ─────────────────────────────────────────────────────────

def _gerar_trace_vertice(i: int, dias_atras: int) -> dict:
    """Gera um trace realista do projeto Vértice AI."""
    idx = i % len(_PERGUNTAS_VERTICE)
    # Simula degradação nos últimos 2 dias (para demo de drift)
    score_ruido = random.gauss(0, 0.05) if dias_atras > 2 else random.gauss(-0.15, 0.08)

    return {
        "id": str(uuid.uuid4()),
        "projeto": "vertice-ai",
        "nome": "responder-cliente",
        "input": _PERGUNTAS_VERTICE[idx],
        "output": _RESPOSTAS_VERTICE[idx],
        "contexto": _CONTEXTOS_VERTICE[idx],
        "modelo": "gemini-1.5-flash",
        "tokens_entrada": random.randint(120, 300),
        "tokens_saida": random.randint(40, 120),
        "latencia_ms": round(random.gauss(820, 150), 2),
        "custo_usd": round(random.uniform(0.0001, 0.0008), 6),
        "criado_em": (datetime.utcnow() - timedelta(
            days=dias_atras,
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )).isoformat(),
        "metadata": {},
    }


def _gerar_trace_postador(i: int, dias_atras: int) -> dict:
    """Gera um trace realista do projeto Postador."""
    idx = i % len(_BRIEFINGS_POSTADOR)
    return {
        "id": str(uuid.uuid4()),
        "projeto": "postador",
        "nome": "gerar-post",
        "input": _BRIEFINGS_POSTADOR[idx],
        "output": _POSTS_GERADOS[idx],
        "modelo": "gpt-4o-mini",
        "tokens_entrada": random.randint(80, 200),
        "tokens_saida": random.randint(60, 180),
        "latencia_ms": round(random.gauss(1200, 200), 2),
        "custo_usd": round(random.uniform(0.00005, 0.0003), 6),
        "criado_em": (datetime.utcnow() - timedelta(
            days=dias_atras,
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )).isoformat(),
        "metadata": {},
    }


async def enviar_trace(cliente: httpx.AsyncClient, trace: dict) -> bool:
    try:
        r = await cliente.post("/traces", json=trace)
        return r.status_code == 201
    except Exception as e:
        print(f"  ✗ Erro: {e}")
        return False


async def criar_dataset_golden(cliente: httpx.AsyncClient) -> None:
    print("\n📋 Criando dataset golden (vertice-ai)...")
    payload = {
        "nome": "vertice-ai-golden-v1",
        "descricao": "50 perguntas de atendimento com respostas esperadas",
        "projeto": "vertice-ai",
        "itens": [
            {
                "input": _PERGUNTAS_VERTICE[i % len(_PERGUNTAS_VERTICE)],
                "output_esperado": _RESPOSTAS_VERTICE[i % len(_RESPOSTAS_VERTICE)],
                "contexto": _CONTEXTOS_VERTICE[i % len(_CONTEXTOS_VERTICE)],
            }
            for i in range(20)
        ],
    }
    r = await cliente.post("/datasets", json=payload)
    if r.status_code == 201:
        print("  ✓ Dataset criado")
    else:
        print(f"  ✗ Falha: {r.text}")


async def criar_regra_alerta(cliente: httpx.AsyncClient) -> None:
    print("\n🔔 Criando regra de alerta de exemplo...")
    payload = {
        "nome": "Faithfulness crítico — Vértice AI",
        "projeto": "vertice-ai",
        "avaliador": "faithfulness",
        "threshold": 0.75,
        "janela_minutos": 60,
        "canal": "slack",
        "webhook_url": "https://hooks.slack.com/services/EXEMPLO",
    }
    r = await cliente.post("/alertas/regras", json=payload)
    if r.status_code == 201:
        print("  ✓ Regra criada")
    else:
        print(f"  ✗ Falha: {r.text}")


async def main() -> None:
    print("🌱 Populando Sentinela AI com dados de demo...\n")

    async with httpx.AsyncClient(base_url=SERVIDOR_URL, timeout=30) as cliente:
        # Verifica conexão
        try:
            r = await cliente.get("/saude")
            r.raise_for_status()
        except Exception:
            print("✗ Servidor não está rodando. Execute 'make dev' primeiro.")
            return

        # Gera traces dos últimos 7 dias
        total = 0
        for dias_atras in range(7, -1, -1):
            qtd_vertice = random.randint(8, 15)
            qtd_postador = random.randint(3, 8)
            traces = (
                [_gerar_trace_vertice(i, dias_atras) for i in range(qtd_vertice)]
                + [_gerar_trace_postador(i, dias_atras) for i in range(qtd_postador)]
            )
            random.shuffle(traces)

            dia_str = (datetime.utcnow() - timedelta(days=dias_atras)).strftime("%d/%m")
            print(f"📅 {dia_str}: enviando {len(traces)} traces...", end=" ")

            resultados = await asyncio.gather(*[enviar_trace(cliente, t) for t in traces])
            ok = sum(resultados)
            total += ok
            print(f"✓ {ok}/{len(traces)}")

        await criar_dataset_golden(cliente)
        await criar_regra_alerta(cliente)

    print(f"\n✅ Seed completo: {total} traces enviados.")
    print("   Dashboard: http://localhost:8501")
    print("   API Docs:  http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(main())
