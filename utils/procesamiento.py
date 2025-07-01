import re
import json
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

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
