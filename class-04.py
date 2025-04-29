from typing import Optional, Literal, List
from pydantic import BaseModel, Field
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
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



load_dotenv()

def click_link_by_partial_text(driver, partial_text, timeout=10):
    try:
        # Esperar a que el enlace exista
        link = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, f"//a[contains(translate(normalize-space(text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{partial_text.lower()}')]"))
        )
        link.click()
        print(f"Clic exitoso en enlace que contiene '{partial_text}'")
    except Exception as e:
        print(f"No se encontró el enlace que contiene '{partial_text}': {e}")

# Configurar navegador
options = webdriver.ChromeOptions()
#options.add_argument("--headless")
options.add_argument("--window-size=1200,800")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)


driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    })
    """
})

# Modelo de acción del navegador
class BrowserAction(BaseModel):
    action: Literal["open_url", "fill_field", "click_link", "press_enter", "screenshot", "finish"] = Field(
        ..., description="Acción: open_url, fill_field o click_link, finish (si se logro el objetivo), screenshot (si se quiere guardar la página actual)"
    )
    selector_css: Optional[str] = Field(
        None, description="selector CSS para fill_field, selector del enlace para click_link. El selector debe ser lo s suficientemente específico para encontrar el elemento deseado." 
    )
    url: Optional[str] = Field(None, description="URL a abrir, solo necesario para open_url")

    value: Optional[str] = Field(
        None, description="Valor a diligenciar, solo necesario para fill_field"
    )
    description: str = Field(..., description="Descripción detallada de la acción realizada",)


# Función para ejecutar una acción
def execute_browser_action(action: BrowserAction)->str:
    if action.action == "open_url" and action.url:
        print(f"Abriendo URL: {action.url}")
        driver.get(action.url)
        return "Abriendo URL: {action.url}"
    elif action.action == "open_google_again" :
        print(f"Abriendo Google nuevamente")
        driver.get("https://www.google.com/")
        return "Ingreso a Google nuevamente" 
    elif action.action == "fill_field" and action.selector_css and action.value:
        try:
            print(f"Diligenciando campo '{action.selector_css}' con valor '{action.value}'")
            element = driver.find_element(By.CSS_SELECTOR, action.selector_css)
            element.clear()
            element.send_keys(action.value)
            return "Diligenció campo '{action.selector_css}' con valor '{action.value}' satisfactoriamente"
        except Exception as e:
            return f"Falló diligenciando el campo. No se encontró el campo '{action.selector_css}'"

    elif action.action == "click_link" and action.selector_css:
            try:
                print(f"Haciendo clic en enlace que contiene: '{action.selector_css}'")
                link = driver.find_element(By.CSS_SELECTOR, action.selector_css)
                #click_link_by_partial_text(driver, action.target)
                #link = driver.find_element(By.PARTIAL_LINK_TEXT, action.target)
                link.click()
                return "Hizo clic en el enlace"
            except Exception as e:
                return f"No se encontró el enlace que contiene '{action.selector_css}': {e}"
    elif action.action == "press_enter" :
        print(f"Presionando ENTER")
        element = driver.switch_to.active_element
        element.send_keys("\n")
        return "Presionó ENTER"
    elif action.action == "screenshot":
        driver.save_screenshot("data/screenshot.png")
        return "Captura de pantalla guardada como screenshot.png"
    else:
        raise ValueError(f"Acción inválida o falta información: {action}")

# Ejemplo: Obtener HTML actual
driver.get("https://www.google.com/")

# Inicializar modelo Gemini
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
structured_llm = llm.with_structured_output(BrowserAction)
#objetivo = "Buscar tarifas de CDTs de los bancos en Colombia. Visitar las diferentes páginas de los bancos y extraer la información relevante. Si no se encuentra la información, volver a Google y buscar otra opción."
objetivo = "Busca pinterest imágenes de gatos. y haz una captura de pantalla cuando los encuentres"

acciones_realizadas = []
finish = False
while not finish:
    html_content = driver.page_source

    current_url = driver.current_url
    
    acciones_realizadas_str = "\n".join(acciones_realizadas)
    prompt = f"""


    Eres un asistente virtual que ayuda a los usuarios a navegar por la web y realizar acciones específicas.
    *OBJETIVO*: {objetivo}
    

    Estas en la URL {current_url} y el HTML de la página es el siguiente: {html_content}.
    Analiza el siguiente HTML y determina la acción que debería realizarse para lograr el objetivo.
    Ayuda:  No debes quedarte en Google. Debes ingresar a las páginas para lograr el objetivo.
    Si te falla un click en un enlace intenta con otro selector CSS o abre la URL directamente.

    Debes responder estrictamente usando el modelo BrowserAction.

    Ya has realizado las siguientes acciones:

{acciones_realizadas_str}
    """
    
    time.sleep(1)

    # Llamar al modelo para decidir la acción
    try:
        browser_action = structured_llm.invoke(prompt)
        print("--------------------------------------")
        print(f"Acción recomendada: {browser_action}")
        if browser_action.action == "finish":
            finish = True
            print("Proceso terminado.")
            break
        result = execute_browser_action(browser_action)
        acciones_realizadas.append(browser_action.description)
        acciones_realizadas.append(result)
        time.sleep(1)

    except Exception as e:
        acciones_realizadas.append("La anterior acción no se pudo ejecutar {e}")
        
        print(f"Error al procesar o ejecutar la acción: {e}")

    # Cerrar el navegador al final
    #driver.quit()
