#from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain.agents import initialize_agent, AgentType
from newsapi import NewsApiClient
from dotenv import load_dotenv
import os

load_dotenv()
# Inicializar cliente de NewsAPI usando la variable de entorno
newsapi = NewsApiClient(api_key=os.environ.get("NEWSAPI_KEY"))

# --- Definición de Tools ---

@tool
def get_headlines(source: str) -> str:
    """Obtiene los titulares principales de una fuente de noticias específica.
    """
    headlines = newsapi.get_top_headlines(sources=source)
    results = []
    for article in headlines["articles"]:
        results.append(f"{article['title']} - {article['source']['name']}")
    return "\n".join(results) if results else f"No hay titulares disponibles para {source}."

@tool
def search_news(query: str) -> str:
    """Busca titulares de noticias relacionadas con el término dado."""
    everything = newsapi.get_everything(q=query, language="es", sort_by="publishedAt")
    results = []
    for article in everything["articles"][:5]:
        results.append(f"{article['title']} - source: {article['source']['name']} \n description: {article['description'] }")
        #print(article)
    return "\n".join(results) if results else f"No se encontraron noticias sobre {query}."

# --- Configuración del LLM y el agente ---

#llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm  = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
tools = [get_headlines, search_news]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True

)



# --- Ejemplos de consultas al agente ---
#print("\n=== Preguntando por titulares de la BBC ===")
#agent.invoke("Dame los titulares principales de la fuente bbc-news")

#print("\n=== Preguntando por titulares de CNN ===")
#agent.invoke("Dame los titulares principales de la fuente cnn")

print("\n=== Buscando noticias de Millonarios ===")
agent.invoke({"input":"Muéstrame las últimas noticias sobre Millonarios"})
    