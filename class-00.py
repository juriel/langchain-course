import os
import getpass


#if not os.environ.get("OPENAI_API_KEY"):
#  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

from langchain_ollama import ChatOllama

model = ChatOllama(model="phi3.5")

response = model.invoke("Como te llamas")
print(type(response))
print(response.content)