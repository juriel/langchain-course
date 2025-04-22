import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage,SystemMessage
from pydantic import BaseModel, Field
from typing_extensions import Annotated, TypedDict


class Person(BaseModel):
    name: str  = Field(description="Nombre de la persona")
    age:  int   = Field(description="Edad de la persona")
    email: str = Field(description="Email de la persona")


class PersonaDict(TypedDict):
    """Datos de una persona   """
    name: Annotated[str,"None","Nombre de la persona"]
    age: Annotated[int,-1,"Edad de la persona"] 
    email: Annotated[str,"None","Email de la persona"]

load_dotenv()

#ollama_url = "http://192.168.39.136:11434"
#llm = ChatOllama(model="llama3.2", base_url=ollama_url)
llm  = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17")

person_llm = llm.with_structured_output(Person)
resp = person_llm.invoke("Analiza la siguiente frase y extree la persona:  Me llamo Jaime Uriel Torres y me falta un año para llegar a los cincuenta . Mi email es juriel@fake.com")

print(type(resp))
print(resp)

