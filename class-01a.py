from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

from langchain_core.messages import AIMessage, HumanMessage,SystemMessage
from dotenv import load_dotenv

## Cargar variables de ambiente con las API Keys de la IA
load_dotenv()

#Crear el LLM de Google Gemini
llm  = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
#llm = ChatOllama(model="phi3.5")


history = []
history.append(SystemMessage(content="""Eres juriel el profesor de programación de IA. 
                             Responde a las preguntas de los seguidores de su canal de Youtube. 
                             Y con cada respuesta invita a suscribirse y dar click en la campanita"""))

history.append(HumanMessage(content="Cuál es la diferencia entre una lista y un diccionario en Python? Dame una respuesta muy corta"))
history.append(AIMessage(content="¡Excelente pregunta! En Python, una **lista** es una colección ordenada de elementos, mientras que un **diccionario** es una colección de pares clave-valor"))
history.append(HumanMessage(content="Dame un ejemplo de ciclo con cada una de ellas"))

response = llm.invoke(history)
print(response.content)

