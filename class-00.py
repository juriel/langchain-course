from langchain_ollama import ChatOllama


ollama_url = "http://192.168.39.136:11434"
#model_name = "phi3.5"
model_name = "deepseek-r1"

chat = ChatOllama(model=model_name,base_url=ollama_url)

response = chat.invoke("¿Compara la ciuda de Londres con Milan en temas de población y calidade vida?")
print(type(response))
print(response.content)