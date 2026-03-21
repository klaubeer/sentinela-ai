"""Integração genérica com LangChain via CallbackHandler.

Funciona com qualquer chain, agent ou LLM do LangChain.
Não é necessário usar @observe() — o handler captura tudo automaticamente.
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from sentinela import Sentinela
from sentinela.integracoes.langchain import SentinelaCallbackHandler

# Configura o Sentinela
sentinela = Sentinela(api_key="sk-...", projeto="langchain-demo")
handler = SentinelaCallbackHandler()

# Sua chain normal — sem mudanças
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente prestativo."),
    ("human", "{pergunta}"),
])
chain = prompt | llm | StrOutputParser()

# Apenas adiciona o handler no invoke — 1 linha
resposta = chain.invoke(
    {"pergunta": "O que é RAG?"},
    config={"callbacks": [handler]},   # <-- única mudança
)

print(resposta)
# O trace já está no Sentinela Dashboard em http://localhost:8501
