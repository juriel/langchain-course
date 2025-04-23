import os
import time
import base64
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import Image

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager



# ------------- SETUP -------------
load_dotenv()

DATA_PATH = "data/falabella.jpg"

# ------------- SELENIUM: OPEN AND CAPTURE PAGE -------------

options = webdriver.ChromeOptions()
options.add_argument("--headless")
#options.add_argument("--window-size=1200,800")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get("https://www.homecenter.com.co/homecenter-co/")

# Esperar un poco a que cargue el contenido
time.sleep(5)  # podrías usar WebDriverWait para algo más elegante

# Obtener tamaño completo de la página
total_width = driver.execute_script("return document.body.scrollWidth")
total_height = driver.execute_script("return document.body.scrollHeight")

# Redimensionar ventana
driver.set_window_size(total_width, total_height)
time.sleep(2)  # Permitir que se renderice

# Capturar pantalla
driver.save_screenshot(DATA_PATH)
driver.quit()

print(f"[✓] Captura guardada en {DATA_PATH}")

# ------------- PROCESAR IMAGEN Y ANALIZAR -------------

# Modelo de salida estructurada
class ImageDescription(BaseModel):
    banner_product: str = Field(description="Que productos está promocionando el banner superior. Separados por coma. Incluya la marca")
    tecnologia: str = Field(description="Cuales productos están en la sección de tecnología, Separados por coma. Incluya la marca")
    promociones_flash: str = Field(description="Que promociones tienen que terminen en poco tiempo.. Incluya la marca, producto y descuento")

# Inicializar Gemini
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
person_llm = llm.with_structured_output(ImageDescription)

# Leer imagen y codificar
with open(DATA_PATH, "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("utf-8")

# Crear mensaje multimodal
human_message = HumanMessage(content=[
    {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{image_b64}"
        }
    },
    {
        "type": "text",
        "text": "Analiza esta imagen que es la captura de un navegador en una tienda online"
    }
])

# Invocar modelo
resp = person_llm.invoke([human_message])
print(resp)
