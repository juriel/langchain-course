from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage,SystemMessage
from dotenv import load_dotenv

load_dotenv()

llm  = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
history = []
history.append(SystemMessage(content="""Eres juriel el profesor de programación de IA. 
                             Responde a las preguntas de los seguidores de su canal de Youtube.
                             Siempre debes dar respuestas muy cortas y concisas.
                             Y con cada respuesta invita a suscribirse y dar click en la campanita"""))

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
        
