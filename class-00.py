from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv



load_dotenv()
# Google require GOOGLE_API_KEY creala en .env.  ai studio google
llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.0-flash")


#ollama_url = "http://192.168.39.136:11434"
ollama_url = "http://localhost:11434"
model_name = "phi3.5"
#model_name = "deepseek-r1"
llm_ollama = ChatOllama(model="phi3.5",base_url=ollama_url)

#Cargar OPENAI_API_KEY  en .env
llm_openai = ChatOpenAI(model="gpt-4o-mini", temperature=0)

print("----------------- [ GEMINI ] -------------------")
response = llm_gemini.invoke("tan solo traduce al español: 'I like learning to program with Professor Juriel.'")
print(response.content)

print("----------------- [ OpenAI ] -------------------")
response = llm_openai.invoke("tan solo traduce al español: 'I like learning to program with Professor Juriel.'")

print(response.content)
print(response)

print("----------------- [ Ollama ] -------------------")
response = llm_ollama.invoke("tan solo traduce al español: 'I like learning to program with Professor Juriel.'")

print(response.content)