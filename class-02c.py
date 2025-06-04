import os
from typing import List, Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage,SystemMessage
from pydantic import BaseModel, Field
from typing_extensions import Annotated, TypedDict


class QuestionsAnswer(BaseModel):
    questions: List[str]  = Field(description="Lista de preguntas que se pueden responder")
    answer:  str   = Field(description="Respuesta a las preguntas")



class KnowledgeUsed(BaseModel):
    uuid: Optional[str]  = Field(description="UUID del conocimiento usado")
    matched: bool = Field(default=False, description="Indica si algun conocimiento hizo match con la respuesta")
    send_attachment: bool = Field(default=False, description="Indica si se debe enviar un archivo con la respuesta")



class PersonaDict(TypedDict):
    """Datos de una persona   """
    name: Annotated[str,"None","Nombre de la persona"]
    age: Annotated[int,-1,"Edad de la persona"] 
    email: Annotated[str,"None","Email de la persona"]

load_dotenv()

#ollama_url = "http://192.168.39.136:11434"
#llm = ChatOllama(model="llama3.2", base_url=ollama_url)
llm  = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17")

person_llm = llm.with_structured_output(QuestionsAnswer)
uuid_llm = llm.with_structured_output(KnowledgeUsed)
resp = person_llm.invoke(""" analiza el siguente texto y genera preguntas y respuesta. 
Preferiblemente genera de 3 a 5 preguntas y una respuesta, solo si aplica.                         
                         
Trata de que la respuesta sea lo más parecido a este texto: 
                         
Casilleros
locker

Son para uso de los trabajadores acorde a los turnos y las diferentes modalidades de trabajo, en las sedes en que las condiciones del espacio y del servicio lo permitan. 

Cualquier duda o inquietud puedes presentar tu solicitud en la siguiente ruta: 

""")




resp2 = uuid_llm.invoke("""
                UUID = sdada-dasdasd---dadas--dadsa
                Son un medio a través del cual los afiliados a los fondos privados pueden realizar aportes adicionales y voluntarios a pensión obligatoria con el objetivo de:

•Complementar y mejorar su pensión cuando llegue la etapa de retiro y poder contar con una mejor mesada.
• Obtener beneficios tributarios.

¡Ten en cuenta! El documento que necesitas para realizar el aporte voluntario a pensión es la certificación de afiliación de la entidad, donde se indique el valor a descontar.
                        

                        Te voy a enviar un formato que lo diligencies. 
                
                UUID = rwerw-rwrew--adasd---dadsas

                Los documentos para disminuir la retención se podrán reportar en cualquier momento y serán aplicados a partir del siguiente mes de radicación.

                UUID = 1234-1234-1234-1234                
                        
                        Si tienes hijos mayores de 18 años que se encuentren en situación de dependencia originada por factores físicos o psicológicos. Para tener derecho a este descuento debes presentar una certificación firmada por ti, en la que indiques e identifiques plenamente a tu hijo. El certificado debe incluir los siguientes datos: nombre, número de documento de identidad y edad de tu hijo, con fecha de nacimiento. Adicional debes adjuntar el registro Civil correspondiente y el certificado emitido por Medicina Legal.
                
                
               INSTRUCCIONES:         
               Cuál es el UUID del conocimiento que hace referencia a la siguente respuesta y 
                Si encuentras coincidencia matched es True de lo contrario False. Si no hacen match el UUID es None.
                

                Respuesta:
                        
                        Son un medio a través del cual los afiliados a los fondospueden hacer aportes adicionales y voluntarios a pensión obligatoria con el objetivo de:

•Complementar y mejorar su pensión cuando llegue la etapa de retiro y poder contar con una mejor mesada.
• Obtener beneficios tributarios.

 El documento que necesitas para realizar el aportes a pensiones es la certificación  de la entidad, donde se indique el valor a descontar.
                
                        Te voy a enviar un formato, para que lo diligencies y lo envíes a la entidad.
                
                """)


print(type(resp))
print(resp)



print(type(resp2))
print(resp2)

