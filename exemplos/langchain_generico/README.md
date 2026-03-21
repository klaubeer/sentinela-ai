# Integração — LangChain (genérica)

Funciona com qualquer chain, agent ou LLM do LangChain sem precisar do `@observe()`.

## Uso

```python
from sentinela.integracoes.langchain import SentinelaCallbackHandler

handler = SentinelaCallbackHandler()

# Adiciona no invoke de qualquer chain
chain.invoke(input, config={"callbacks": [handler]})
```

## Instalação

```bash
pip install sentinela-ai[langchain]
```
