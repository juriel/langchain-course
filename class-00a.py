from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup



def extraer_texto_desde_url(url:str):
    response = requests.get(url) #llamando la URL
    soup = BeautifulSoup(response.content, 'html.parser')

    # Elimina scripts, estilos, navegación y pie de página
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    # Extrae solo el texto visible
    text = soup.get_text(separator='\n', strip=True)
    #print(text)
    return text

# Cargar variables de ambiente
load_dotenv()
llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
llm_ollama = ChatOllama(model="phi3.5")

url = "https://edition.cnn.com"

html_text = extraer_texto_desde_url(url)



response = llm_gemini.invoke(
    f"Este es el texto extraído de la página de CNN. Analiza y descubre si hay alguna noticia relevante que pueda afectar acciones en bolsa.\n\n{html_text}"
)
print(response.content)
