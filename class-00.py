from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_gemini import ChatGemini

#ollama_url = "http://192.168.39.136:11434"
ollama_url = "http://localhost:11434"
model_name = "phi3.5"
#model_name = "deepseek-r1"

chat = ChatOllama(model=model_name,base_url=ollama_url)

response = chat.invoke("¿Compara la ciuda de Londres con Milan en temas de población y calidade vida?")
print(type(response))
print(response.content)