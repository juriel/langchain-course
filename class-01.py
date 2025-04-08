from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage,AIMessage


ollama_url = "http://192.168.39.136:11434"
#model_name = "phi3.5"
model_name = "deepseek-r1"

chat  = ChatOllama(model=model_name,base_url=ollama_url)
history = [] 
while True:
    try:
        user_input = input("👤 Tú: ")
        
        if user_input.lower() in ['salir', 'exit']:
            break
        history.append(HumanMessage(content=user_input))
        response = chat.invoke(history)
        
        
        text_after_think = response.content.split("</think>")[-1].strip()

        
        print("Bot 🤖:",text_after_think)
        history.append(AIMessage(content=text_after_think))


    except Exception as e:
        print(f"Error: {str(e)}")
        


