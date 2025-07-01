import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.procesamiento import analizar_comentario

st.set_page_config(page_title="Análisis de Comentarios", layout="wide")
st.title("🔍 Demo IA: Análisis de Comentarios")

uploaded_file = st.file_uploader("📤 Sube un archivo CSV con comentarios", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, delimiter=';', quotechar='"')
    if "comentario" not in df.columns:
        st.error("❌ El archivo debe tener una columna llamada 'comentario'")
    else:
        st.info("⏳ Analizando comentarios...")
        resultados = []
        df = df[df["comentario"].notna() & (df["comentario"].str.strip() != "")]
        for comentario in df["comentario"]:
            print(F"comentario: {comentario}")
            sentimiento, tema = analizar_comentario(comentario)
            resultados.append({
                "comentario": comentario,
                "sentimiento": sentimiento,
                "tema": tema
            })

        df_resultado = pd.DataFrame(resultados)
        conteo_sentimientos = df_resultado["sentimiento"].value_counts()
        conteo_temas = df_resultado["tema"].value_counts()
        colores = {
            "positivo": "#4CAF50",
            "negativo": "#F44336",
            "neutro": "#FFC107"
        }
        colores_tema = {
            "elogio": "#81C784",      # Verde claro
            "crítica": "#E57373",     # Rojo claro
            "queja": "#BA68C8",       # Violeta
            "propuesta": "#64B5F6",   # Celeste
            "otro": "#FFD54F"         # Amarillo suave
        }

        colors = [colores.get(sent, "#2196F3") for sent in conteo_sentimientos.index]
        
        st.subheader("📊 Resultados del análisis")
        st.dataframe(df_resultado, use_container_width=True)

        st.subheader("📈 Sentimientos")
        #fig1, ax1 = plt.subplots(figsize=(4, 2.5))  # Compacto
        #ax1.bar(conteo_sentimientos.index, conteo_sentimientos.values, color=colors)
        #ax1.set_ylabel("Cantidad", fontsize=8)
        #ax1.set_title("Comentarios por sentimiento", fontsize=10)
        #ax1.tick_params(axis='x', labelsize=8)
        #ax1.tick_params(axis='y', labelsize=8)
        #plt.tight_layout()
        #st.pyplot(fig1)

        fig, ax = plt.subplots(figsize=(4, 2.5))
        ax.pie(conteo_sentimientos, labels=conteo_sentimientos.index, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")  # Circulo perfecto
        st.pyplot(fig)

        st.subheader("📘 Temas más mencionados")
        conteo_temas = df_resultado["tema"].value_counts()
        colors_tema = [colores_tema.get(t, "#B0BEC5") for t in conteo_temas.index]

        # Gráfico más pequeño
        fig2, ax2 = plt.subplots(figsize=(4, 2.5))  # Tamaño reducido
        ax2.bar(conteo_temas.index, conteo_temas.values, color=colors_tema)
        ax2.set_ylabel("Cantidad")
        ax2.set_title("Distribución de temas")
        ax2.tick_params(axis='x', labelsize=8)
        ax2.tick_params(axis='y', labelsize=8)
        plt.tight_layout()
        st.pyplot(fig2)

        negativos = df_resultado[df_resultado["sentimiento"] == "negativo"]
        total = len(df_resultado)
        if total > 0 and len(negativos) / total >= 0.3:
            st.error("⚠️ ALERTA: Hay una alta proporción de comentarios negativos.")
        
        st.download_button("📥 Descargar resultados CSV", df_resultado.to_csv(index=False), file_name="resultados.csv")
