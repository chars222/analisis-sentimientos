import re
import json
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.1-8B-Instruct"

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

        genai.configure(api_key=os.getenv("MODEL_API_KEY"))
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
    # (Aquí va tu código para inicializar el modelo de Gemini)
    # model = ...

    # ¡Este es el prompt clave!
    prompt = f"""
    Analiza el siguiente comentario de un cliente y proporciona una respuesta en formato JSON.

    Comentario: "{comment}"

    Basándote en el contenido del comentario, realiza dos tareas:
    1. Clasifícalo en UNA de las siguientes categorías temáticas: 'Producto / Calidad', 'Servicio al Cliente', 'Precio / Valor', 'Logística / Entrega', 'Experiencia de Usuario (App/Web)', 'General / Otro'.
    2. Determina el sentimiento principal expresado, eligiendo UNA de las siguientes opciones: 'Alegría / Satisfacción', 'Enojo / Frustración', 'Tristeza / Decepción', 'Sorpresa', 'Confusión', 'Sugerencia / Interés', 'Neutral'.

    Responde únicamente con un objeto JSON válido que contenga las claves "tema" y "sentimiento". No incluyas explicaciones adicionales, solo el JSON.
    """
    
    # response = model.generate_content(prompt_template)
    # import json
    # result = json.loads(response.text)
    # return result['tema'], result['sentimiento']

    # --- PARA PRUEBAS SIN API ---
    # Esto es solo para que el código funcione sin llamar a la API real.
    # Debes reemplazarlo con tu llamada real a Gemini.
    import json

    genai.configure(api_key=os.getenv("MODEL_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content(f"{prompt}")
    cleaned_text = response.text.replace('```json', '').replace('```', '')
    cleaned_text = cleaned_text.strip()
    print(cleaned_text)
    result = json.loads(cleaned_text)
    return result['tema'], result['sentimiento']
