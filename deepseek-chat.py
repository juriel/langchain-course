from langchain.agents import tool
from langchain.agents import AgentType, initialize_agent
from langchain_community.llms import Ollama
from langchain.memory import ConversationBufferMemory

def calcular_aportes(num_meses: int, salario: float) -> float:
    """
    Calcula los aportes totales basados en número de meses y salario mensual
    """
    tasa_aporte = 0.10  # Ejemplo: 10% de aporte
    return num_meses * salario * tasa_aporte

@tool
def calcular_aportes_tool(data: str) -> str:
    """
    Calcula los aportes totales a partir de una entrada formateada como una cadena.
    
    Args:
        data (str): Una cadena que contiene el número de meses y el salario mensual .
    
    Returns:
        str: Aporte total formateado como cadena.
    """
    try:
        num_meses, salario = data.split(",")
        meses = int(num_meses.strip())
        salario_num = float(salario.strip())
        resultado = calcular_aportes(meses, salario_num)
        return f"Aportes totales: {resultado:.2f}"
    except ValueError:
        return "Error: Entrada inválida. Usa el formato 'meses,salario' (e.g., '12,5000')"

# Configuración de Ollama con Deepseek
llm = Ollama(model="deepseek-r1",base_url="http://192.168.39.136:11434/")  # Asegúrate de tener el modelo descargado
tools = [calcular_aportes_tool]
memory = ConversationBufferMemory(memory_key="chat_history")

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
    handle_parsing_errors=True,

)

# Ciclo de conversación mejorado
print("🌟 Sistema de Cálculo de Aportes con Deepseek 🌟")
print("Escribe 'salir' para terminar la conversación\n")

historial = []
contexto = []

while True:
    try:
        user_input = input("👤 Tú: ")
        
        if user_input.lower() in ['salir', 'exit']:
            break
            
        # Ejecutar la cadena con el contexto acumulado
        respuesta = agent.invoke({
            "input": user_input,
            "chat_history": contexto
        })

        
        # Actualizar contexto
        contexto.append(f"Usuario: {user_input}")
        contexto.append(f"Asistente: {respuesta}")
        
        # Mantener solo los últimos 4 mensajes en contexto
        contexto = contexto[-4:]
        
        # Almacenar en historial
        historial.append(f"👤 Tú: {user_input}")
        historial.append(f"🤖 Deepseek: {respuesta}")
        
        # Mostrar respuesta
        print(f"\n🤖 Deepseek: {respuesta}")
        print("-" * 50 + "\n")
        
    except Exception as e:
        print(f"⚠️ Error: {str(e)}")
        continue

print("\n💬 Historial completo de la conversación:")
for mensaje in historial:
    print(mensaje)