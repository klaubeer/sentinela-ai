# sentinela-ai SDK

SDK Python para observabilidade e avaliação de LLMs em produção.

## Instalação

```bash
pip install sentinela-ai
pip install sentinela-ai[langchain]  # com suporte a LangChain
```

## Uso básico

```python
from sentinela import Sentinela

sentinela = Sentinela(api_key="sk-...", projeto="meu-projeto")

@sentinela.observe()
def minha_funcao(pergunta):
    ...
```

## Integração com LangChain

```python
from sentinela.integracoes.langchain import SentinelaCallbackHandler

handler = SentinelaCallbackHandler(projeto="meu-projeto", nome="meu-agente")
chain.invoke(input, config={"callbacks": [handler]})
```
