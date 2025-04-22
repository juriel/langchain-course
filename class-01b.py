from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage,SystemMessage
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

load_dotenv()


html_text = extraer_texto_desde_url("https://www.marca.com")

llm  = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

history = []
history.append(SystemMessage(content=f"""Eres un analista de noticias deportivas. Y tienes los siguientes datos
de la página de MARCA el diario deportivo.
    {html_text}
No menciones que estás sacando la información de la página de MARCA. """))

while True:
    try:
        user_input = input("👤 Tú: ")
        
        if user_input.lower() in ['salir', 'exit']:
            break
        history.append(HumanMessage(content=user_input))
        response = llm.invoke(history)
        
        print("Bot 🤖:",response.content)
        history.append(AIMessage(content=response.content))


    except Exception as e:
        print(f"Error: {str(e)}")
        
