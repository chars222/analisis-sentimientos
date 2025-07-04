import re
import json
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import time
import requests
import streamlit as st
load_dotenv()


#API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct"
# Cambia temporalmente esta línea en tu código
API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"

def analizar_comentario(comentario: str):
    prompt = f"""
Analiza el siguiente comentario y responde en formato JSON. Coemntario: "{comentario}"

Devuelve:
{{
  "sentimiento": "positivo | negativo | neutro",
  "tema": "elogio | crítica | queja | propuesta | otro"
}}
 . Solo devolver un sentimiento y un tema pora el comentario el que sea el mas apropiado"""
    try:

        genai.configure(api_key=st.secrets["HF_TOKEN"])
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(f"{prompt}")
        content = response.text
        # Busca el bloque JSON dentro de la respuesta del modelo
        json_match = re.search(r'\{.*?\}', content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("sentimiento", "desconocido"), data.get("tema", "otro")
        else:
            print("⚠️ No se pudo extraer un bloque JSON de la respuesta.")
            return "error", "error"
    except Exception as e:
        print(f"Error: {e}")
        return "error", "error"

def get_analysis_from_gemini(comment):
    try:
        prompt = f"""
        Analiza el siguiente comentario de un cliente y proporciona una respuesta en formato JSON.

        Comentario: "{comment}"

        Basándote en el contenido del comentario, realiza dos tareas:
        1. Clasifícalo en UNA de las siguientes categorías temáticas: 'Producto / Calidad', 'Servicio al Cliente', 'Precio / Valor', 'Logística / Entrega', 'Experiencia de Usuario (App/Web)', 'General / Otro'.
        2. Determina el sentimiento principal expresado, eligiendo UNA de las siguientes opciones: 'Alegría / Satisfacción', 'Enojo / Frustración', 'Tristeza / Decepción', 'Sorpresa', 'Confusión', 'Sugerencia / Interés', 'Neutral'.

        Responde únicamente con un objeto JSON válido que contenga las claves "tema" y "sentimiento". No incluyas explicaciones adicionales, solo el JSON.
        """
        import json

        genai.configure(api_key=st.secrets["HF_TOKEN"])
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(f"{prompt}")
        cleaned_text = response.text.replace('```json', '').replace('```', '')
        cleaned_text = cleaned_text.strip()
        print(cleaned_text)
        result = json.loads(cleaned_text)
        return result['tema'], result['sentimiento']
    except Exception as e:
        print(f"Error: {e}")
        return "error", "Couta excedida"

def crear_prompt_bloque_gemini(bloque_comentarios: list) -> str:
    
    comentarios_enumerados = ""
    for i, comentario in enumerate(bloque_comentarios):
        comentarios_enumerados += f'comment_id: {i}, texto: "{comentario}"\n'
    
    prompt = f"""
    Analiza la siguiente lista de comentarios de clientes. Tu única tarea es devolver un array JSON válido.
    Cada objeto en el array debe corresponder a un comentario de la lista y contener las claves "id", "tema" y "sentimiento".
    El "id" debe ser el número de 'comment_id' del comentario correspondiente.

    COMENTARIOS A ANALIZAR:
    {comentarios_enumerados}

    CATEGORÍAS DE TEMA: 'Producto / Calidad', 'Servicio al Cliente', 'Precio / Valor', 'Logística / Entrega', 'Experiencia de Usuario (App/Web)', 'General / Otro'.
    CATEGORÍAS DE SENTIMIENTO: 'Alegría / Satisfacción', 'Enojo / Frustración', 'Tristeza / Decepción', 'Sugerencia / Interés', 'Neutral'.

    Responde únicamente con el array JSON, sin texto adicional ni marcadores de markdown.
    """
    return prompt

def analizar_bloque_con_gemini(bloque_comentarios: list) -> list:
    """
    Envía un bloque de comentarios a Gemini Flash y devuelve los resultados.
    """
    try:
        # Configura el modelo a usar
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        prompt = crear_prompt_bloque_gemini(bloque_comentarios)
        
        # Llama a la API
        response = model.generate_content(prompt)
        
        # Limpia la respuesta para asegurar que sea un JSON válido
        cleaned_response = response.text.replace('```json', '').replace('```', '').strip()
        
        return json.loads(cleaned_response)

    except Exception as e:
        print(f"Ocurrió un error al procesar el bloque con Gemini: {e}")
        # Si falla, devuelve una lista de errores del mismo tamaño que el bloque
        # para no romper el ensamblaje del DataFrame final.
        return [{"id": i, "tema": "Error de API", "sentimiento": str(e)} for i in range(len(bloque_comentarios))]

    except requests.exceptions.HTTPError as http_err:
        # Manejo específico para el error de modelo pausado
        if response.status_code == 400 and "paused" in response.text:
            st.error("El modelo en la API está pausado. Visita la página del modelo en Hugging Face para activarlo y espera unos minutos antes de reintentar.")
        else:
            print(f"Error HTTP: {http_err}, Respuesta: {response.text}")
        return [{"id": i, "tema": "Error de API", "sentimiento": str(http_err)} for i in range(len(bloque_comentarios))]

    except Exception as e:
        print(f"Ocurrió un error inesperado al procesar el bloque: {e}")
        return [{"id": i, "tema": "Error de Procesamiento", "sentimiento": str(e)} for i in range(len(bloque_comentarios))]

def procesar_dataframe_con_gemini(df: pd.DataFrame, tamano_bloque: int = 10) -> pd.DataFrame:
    """
    Divide el DataFrame en bloques y los procesa con Gemini Flash.
    """
    # Configura la API Key desde los secrets al inicio del procesamiento
    try:
        genai.configure(api_key=st.secrets["HF_TOKEN"])
    except Exception as e:
        st.error(f"Error al configurar la API Key de Gemini. Revisa tus secrets. Error: {e}")
        return df

    lista_comentarios = df['comentario'].tolist()
    resultados_totales = []
    
    numero_de_bloques = (len(lista_comentarios) + tamano_bloque - 1) // tamano_bloque
    
    for i in range(0, len(lista_comentarios), tamano_bloque):
        bloque_actual = lista_comentarios[i:i + tamano_bloque]
        st.info(f"Procesando bloque {i//tamano_bloque + 1} de {numero_de_bloques}...")
        
        resultados_bloque = analizar_bloque_con_gemini(bloque_actual)
        resultados_totales.extend(resultados_bloque)
        time.sleep(1) # Pausa para no exceder los límites de la API

    df_resultados = pd.DataFrame(resultados_totales)
    
    # Une el DataFrame original con los resultados
    df_final = df.join(df_resultados.set_index(df.index, drop=False))
    
    return df_final