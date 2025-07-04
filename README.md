# Demo IA - Análisis de Comentarios de redes sociales

Esta demo analiza comentarios de redes sociales usando Modelos de inteligencia artificial y los clasifica por sentimiento y tema.

## Estructura

- `.streamlit/secrets.toml`: configuracion de ApiKey para el uso de los modelos, agregar en tu proyecto para correcto funcionamiento
- `main.py`: interfaz Streamlit para carga y visualización.
- `utils/procesamiento.py`: análisis usando modelo local y nube.
- `data/comentarios_ejemplo.csv`: datos simulados.
- `requirements.txt`: dependencias.

## Requisitos

- Tener [Ollama](https://ollama.com) instalado y corriendo.
- Cargar el modelo `llama3`:
- Tener una cuenta en Gemini
