import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
import base64

class ImageDescription(BaseModel):
    animal: str = Field(description="Animal en la imagen")
    count: int = Field(description="cuántos animales hay")
    location: str = Field(description="Ubicación del animal")

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# Estructura de salida esperada
animal_llm = llm.with_structured_output(ImageDescription)

# Leer y codificar la imagen a base64
with open("data/imagen-04.jpg", "rb") as f:
    image_bytes = f.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

# Crear mensaje multimodal
human_message = HumanMessage(content=[
    {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpg;base64,{image_b64}"
        }
    },
    {
        "type": "text",
        "text": "Analiza la imagen y describe el animal, la cantidad y la ubicación."
    }
])

# Invocar el modelo (nota: lista con un solo mensaje)
resp = animal_llm.invoke([human_message])

print(type(resp))
print(resp)
