from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage,SystemMessage
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import fitz  # PyMuPDF
import operator
import os

from pydantic import BaseModel, Field
from typing import Literal

def approximate_pdf_layout_to_string(pdf_path):
    """
    Extrae texto de un PDF intentando preservar la disposición espacial
    basándose en las coordenadas del texto y devuelve el resultado como un string.

    Args:
        pdf_path (str): Ruta al archivo PDF de entrada.

    Returns:
        str: Una cadena de texto que intenta simular el diseño del PDF,
             o None si ocurre un error al abrir el PDF.
        list: Una lista de diccionarios, donde cada diccionario contiene
              el texto y su bounding box (x0, y0, x1, y1) para cada palabra.
              Retorna una lista vacía si no se encuentra texto o hay un error.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error al abrir el PDF '{pdf_path}': {e}")
        return None, [] # Devuelve None para el string y lista vacía para las coordenadas

    full_text_layout = ""
    all_word_data = [] # Lista para guardar texto y coordenadas

    # --- Parámetros ajustables ---
    # Estimación del ancho promedio de carácter en píxeles.
    # Esto es crucial para calcular los espacios. Ajústalo si el espaciado es incorrecto.
    # Puedes intentar calcularlo dinámicamente, pero una estimación suele funcionar.
    avg_char_width_approx = 6

    # Multiplicador para el umbral de altura de línea.
    # Una palabra se considera en una nueva línea si su 'y0' está más abajo que
    # la 'y0' de la línea anterior más (altura_línea_estimada * multiplicador / 2).
    # Un valor mayor a 1 permite cierta flexibilidad vertical en una línea.
    line_height_threshold_multiplier = 1.2

    # Mínimo de espacios a insertar entre palabras si el cálculo da <= 0.
    min_spaces_between_words = 1
    # ---------------------------

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # Extraer palabras con sus coordenadas: (x0, y0, x1, y1, "palabra", block_no, line_no, word_no)
        words = page.get_text("words", sort=True) # sort=True ordena por y0, x0

        if not words:
            #full_text_layout += f"--- Page {page_num + 1} (No text found) ---\n\n"
            continue

        full_text_layout += f"--- Page {page_num + 1} ---\n"

        current_line_y0 = -1 # Coordenada Y superior de la línea actual
        last_word_x1 = 0     # Coordenada X derecha de la última palabra añadida
        estimated_line_height = 10 # Estimación inicial, se actualizará

        page_word_data = [] # Datos de palabras para esta página

        for i, w in enumerate(words):
            x0, y0, x1, y1, text, block_no, line_no, word_no = w
            text = text.strip()
            if not text: continue # Ignorar palabras vacías/espacios extraídos como palabras

            # Guardar datos de la palabra actual (texto y coords)
            page_word_data.append({"text": text, "bbox": (x0, y0, x1, y1)})

            # Estimar la altura de la línea basada en la palabra actual
            current_word_height = y1 - y0
            if current_word_height > 5: # Ignorar alturas muy pequeñas
                 # Usar un promedio móvil o simplemente la altura de la palabra actual podría ser una opción
                 estimated_line_height = current_word_height


            # --- Detección de Nueva Línea ---
            # Es una nueva línea si:
            # 1. Es la primera palabra de la página (current_line_y0 == -1)
            # 2. Su 'y0' es significativamente mayor que la 'y0' de la línea actual.
            #    Usamos un umbral basado en la altura estimada de la línea.
            #    Comparamos y0 > current_line_y0 + umbral
            #    El umbral es flexible (estimated_line_height * multiplier / 2)
            is_new_line = (current_line_y0 == -1 or
                           y0 > current_line_y0 + (estimated_line_height * line_height_threshold_multiplier / 2))

            if is_new_line:
                # Si había texto en la línea anterior (no es la primera línea), añadir un salto de línea
                if current_line_y0 != -1:
                    full_text_layout += "\n"

                # Iniciar la nueva línea
                current_line_y0 = y0 # Actualizar la referencia Y de la línea
                # Calcular indentación basada en x0
                # Asegurarse de que avg_char_width_approx no sea cero
                indent_spaces = int(x0 / avg_char_width_approx) if avg_char_width_approx else 0
                full_text_layout += " " * indent_spaces + text
                last_word_x1 = x1
            else:
                # --- Misma Línea ---
                # Calcular espacios necesarios basados en la separación horizontal
                horizontal_gap = x0 - last_word_x1
                # Asegurarse de que avg_char_width_approx no sea cero
                spaces_needed = int(horizontal_gap / avg_char_width_approx) if avg_char_width_approx else 0

                # Añadir espacios + texto
                # Asegurarse de que haya al menos un espacio si las palabras no se tocan
                if horizontal_gap > 0:
                    full_text_layout += " " * max(min_spaces_between_words, spaces_needed) + text
                else:
                     # Si se solapan o tocan (gap <= 0), añadir solo el texto (o un espacio mínimo si se prefiere)
                     # A menudo, la extracción ya incluye un espacio implícito o son parte de la misma "palabra" visual.
                     # Podríamos añadir siempre un espacio aquí, pero puede crear dobles espacios.
                     # Se decide no añadir espacio por defecto si horizontal_gap <= 0.
                     full_text_layout += text # Considerar añadir " " + text si se pierden espacios

                last_word_x1 = x1 # Actualizar la posición final de la última palabra

        # Añadir un salto de línea al final de la última línea de la página
        if words: # Solo si hubo palabras en la página
            full_text_layout += "\n"

        full_text_layout += "\n" # Espacio extra entre páginas
        all_word_data.extend(page_word_data) # Agregar datos de palabras de la página a la lista general

    doc.close()

    return full_text_layout, all_word_data

def extraer_texto_desde_pdf(filename:str):
    text = ""
    try:
        with open(filename, "rb") as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text += " "+page.extract_text() or ""
    except Exception as e:
        print(f"Error al leer el PDF: {e}")
    return text

#---------------------------- MAIN -------------------

class DocumentPDF(BaseModel):
    type: Literal["FORMULARIO_IMPUESTOS", "COTIZACION", "CURRICULUM_VITAE", "VIAJE", "FACTURA", "CONTRATO", "LIBRO", "CERTIFICADO_CAMARA_COMERCIO", "OTROS"] = Field(
        description="""
    FORMULARIO_IMPUESTOS: Formulario de impuestos Colombianos o declaración fiscal de la DIAN o Secretaria de Hacienda. Los formularios de impuesto suelen tener un número 001 RUT , 350 IVA, 110 RENTA, 300 Retencion en la fuente, 490 o 491 recuado
    COTIZACION: Documento que presenta una oferta de precios y condiciones para un producto o servicio. Suele tener una carta de presentacion y un detalle de los productos o servicios cotizados.
    VIAJE: Cualquier documento relacionado con un viaje, como itinerarios, tiqutes, reservas o confirmaciones.
    FACTURA: Cualquier documento que tenga una factura, ya sea de venta o de compra. Suelen decir FActura de Venta o Factura de Compra.
    LIBRO: Documento que contiene información o contenido literario, científico o técnico.
    CURRICULUM_VITAE: Documento que presenta la trayectoria profesional y académica de una persona.
    CERTIFICADO_CAMARA_COMERCIO: CERTIFICADO  DE  EXISTENCIA  Y  REPRESENTACION  LEGAL. Documento que certifica la existencia legal de una empresa o entidad en la Cámara de Comercio.
    CONTRATO: Documento que establece un acuerdo legal entre partes.
    RECIBO_PAGO:  Documento que confirma el pago de un servicio o producto. Tambien puede aparecer como una transferencia bancaria
    OTROS: Cualquier otro tipo de documento que no encaje en las categorías anteriores.
 """    
    )

class Libro(BaseModel):
    titulo: str = Field(description="Titulo del libro")
    autor: str = Field(description="Autor del libro")
        

load_dotenv()

ollama_url = "http://192.168.39.136:11434"
#llm = ChatOllama(model="llama3.2", base_url=ollama_url)
llm  = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17")
#llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

doc_llm   = llm.with_structured_output(DocumentPDF)
libro_llm = llm.with_structured_output(Libro)

for f in os.listdir("/home/juriel/PDF2"):
    try:
        if f.lower().endswith(".pdf"):
            path = os.path.join("/home/juriel/PDF2", f)
            texto , all_word_data= approximate_pdf_layout_to_string("/home/juriel/PDF2/"+f) 
            txt_file = f.replace(".pdf", ".txt")
            
            if len(texto) == 0:
                continue
            with open("/home/juriel/PDF2/txt/"+txt_file, "w") as file:
                print(f"{f}")
                texto_corto =texto[0:4000]
                str_instruct =  """Analiza el siguiente texto extraido de un PDF y clasifica el documento.
                     El texto es :\n"""+texto_corto
                #print(str_instruct)
                resp = doc_llm.invoke(str_instruct)
                print(resp)
                if resp.type == "LIBRO":
                    resp = libro_llm.invoke("""Extrae la siguiente informacion del libro: Titulo y Autor. El texto es:\n"""+texto_corto)
                    print(resp) 
                file.write(texto) 
        print("\n---------------------------------\n")        
    except Exception as e:
        print(f"Error al procesar el archivo {f}: {e}")    




        
