from langchain.agents import tool
from langchain.agents import AgentType, initialize_agent
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import json

@tool
def registrar_interes_usuario_tool(data: str) -> str:
    """
    Cuando tengas todos los datos del usuario registra los intereses de un usuario a partir de un JSON.
    Formato esperado: {
        "nombre_tienda": str,
        "nombre_persona": str,
        "interes": str
    }
    
    Ejemplo de entrada: 
    '{"nombre_tienda": "Mi Tienda", "nombre_persona": "Juan", "interes": "tecnología"}'
    
    Devuelve confirmación con los datos recibidos.
    """
    try:
        datos_usuario = json.loads(data)
        campos_requeridos = ["nombre_tienda", "nombre_persona", "interes"]
        for campo in campos_requeridos:
            if campo not in datos_usuario:
                return f"Error: Falta el campo requerido '{campo}' en el JSON"
        
        return (
            f"Registro exitoso:\n"
            f"🏪 Tienda: {datos_usuario['nombre_tienda']}\n"
            f"👤 Cliente: {datos_usuario['nombre_persona']}\n"
            f"🎯 Interés: {datos_usuario['interes']}"
        )
        
    except json.JSONDecodeError:
        return "Error: Formato JSON inválido. Ejemplo correcto: {'nombre_tienda': '...', 'nombre_persona': '...', 'interes': '...'}"

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0
)

tools = [registrar_interes_usuario_tool]

# Configuración mejorada de la memoria
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    input_key="input"
)

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.OPENAI_MULTI_FUNCTIONS,  # Tipo de agente corregido
    verbose=True,
    memory=memory,
    handle_parsing_errors=True,
    agent_kwargs={
        "system_message": SystemMessage(content=(
            "Eres Daniela de servicio al cliente de Tomapedidos. "
            "Un usuario se acaba de inscribir en la aplicación. "
            "1. Pregunta si desean que un agente los contacte\n"
            "2. Si aceptan, solicita: nombre de tienda, nombre y interés\n"
            "3. Valida y formatea los datos en JSON\n"
            "4. Usa la herramienta de registro\n"
            "Formato JSON requerido: {\"nombre_tienda\": \"...\", \"nombre_persona\": \"...\", \"interes\": \"...\"}"
        ))
    }
)

print("Escribe 'salir' para terminar la conversación\n")

historial = []

while True:
    try:
        user_input = input("👤 Tú: ")
        
        if user_input.lower() in ['salir', 'exit']:
            break
            
        # Ejecutar el agente con historial completo
        respuesta = agent({
            "input": user_input,
            "chat_history": memory.chat_memory.messages
        })
        
        # Actualizar memoria manualmente
        memory.chat_memory.add_user_message(user_input)
        memory.chat_memory.add_ai_message(respuesta['output'])
        
        # Almacenar en historial
        historial.append(f"👤 Tú: {user_input}")
        historial.append(f"🤖 Asistente: {respuesta['output']}")
        
        print(f"\n🤖 Asistente: {respuesta['output']}")
        print("-" * 50 + "\n")
        
    except Exception as e:
        print(f"⚠️ Error: {str(e)}")
        continue

print("\n💬 Historial completo de la conversación:")
for mensaje in historial:
    print(mensaje)