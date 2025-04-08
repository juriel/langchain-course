import os
import getpass
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class save_customer_info(BaseModel):
    """Salva la informacion del cliente en la base de datos"""
    customer_name: str = Field(..., description="Nombre completo del usuario")
    business_name: str = Field(..., description="Nombre del negocio o distribuidora")
    interest: str = Field(..., description="Interés del usuario")
    conversation_summary: str = Field(..., description="Resumen de la conversación")

llm = ChatOpenAI(model="gpt-4o-mini")

llm_with_tools = llm.bind_tools([save_customer_info],strict=True)

messages = [
    SystemMessage(
"""Eres daniela asistente de mercadeo de Tomapedidos. Un usuario llamado Juan Perez se ha registrado en la aplicación. 
Saludalo e invitalo a conocer más sobre la plataforma. Pregúntale si está interesado que un agente de ventas le explique la aplicación.
Solo necesitamos que nos confirme el nombre, el de la empresa o distribuidora y por qué está interesado en Tomapedidos. 
Cuando tengas esta información salva la información del cliente y despidete de él.
Haz una sóla pregunta a la vez. Primero pregunta si está intersado. Y luego sus datos.
"""),
    
]

print("Escribe 'salir' para terminar la conversación\n")


while True:
    try:
        user_input = input("👤 Tú: ")
        
        if user_input.lower() in ['salir', 'exit']:
            break
        messages.append(HumanMessage(user_input))
        
        resp = llm_with_tools.invoke(messages)
        print("----------------------------")
        print(resp)
        print("---------------------------")
        if resp.additional_kwargs and "tool_calls" in resp.additional_kwargs:
            
            tool_calls = resp.additional_kwargs["tool_calls"]
            for tool_call in tool_calls:
                if tool_call["tool_name"] == "save_customer_info":
                    print("Guardando información del cliente")
                    print(f"Tool call: {tool_call}")
                    print("Guardando información del cliente")  
                print(f"Tool call: {tool_call}")
            print(resp.content)
            messages.append(resp)
        else:
            print(resp.content)
            messages.append(resp)
    except Exception as e:
        print(f"Error: {str(e)}")
        continue