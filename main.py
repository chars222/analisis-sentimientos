import streamlit as st
import pandas as pd
import plotly.express as px
from utils.procesamiento import procesar_dataframe_con_gemini

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Análisis de Sentimientos y Temas",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard de Análisis de Comentarios")
st.markdown("App para clasificar comentarios por sentimiento y tema usando Inteligencia Artificial")

# --- SIMULACIÓN DE LA LLAMADA A GEMINI (REEMPLAZAR CON TU CÓDIGO REAL) ---
# Esta función simula la respuesta de Gemini para no gastar cuota de API en pruebas.


# --- CARGA Y PROCESAMIENTO DE DATOS ---
uploaded_file = st.file_uploader("Carga tu archivo CSV con los comentarios", type="csv")

if uploaded_file is not None:
    df_completo  = pd.read_csv(uploaded_file, delimiter=';', quotechar='"')
    if len(df_completo ) > 100:
        st.warning(f"El archivo cargado contiene {len(df_completo )} comentarios. Solo se procesarán los primeros 100.")
    df_limitado = df_completo .head(15)
    if 'comentario' in df_limitado.columns:
        # Procesar los comentarios si aún no han sido analizados
        if 'tema' not in df_limitado.columns or 'sentimiento' not in df_limitado.columns:
            with st.spinner('Analizando comentarios con Gemini... Por favor, espera.'):
                #analysis_results = df['comentario'].apply(lambda x: pd.Series(get_analysis_from_gemini(x)))
                #analysis_results.columns = ['tema', 'sentimiento']
                df_analizado = procesar_dataframe_con_gemini(df_limitado, tamano_bloque=10)

        st.success("¡Análisis completado!")

        # --- MOSTRAR EL DASHBOARD CON GRÁFICOS ---
        
        # 1. Métricas Clave (KPIs)
        st.header("Resumen General")
        total_comments = len(df_analizado)
        most_common_sentiment = df_analizado['sentimiento'].mode()[0]
        most_common_topic = df_analizado['tema'].mode()[0]

        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Comentarios", f"{total_comments}")
        col2.metric("Sentimiento Principal", most_common_sentiment)
        col3.metric("Tema Más Frecuente", most_common_topic)
        
        st.markdown("---")

        # 2. Gráficos
        st.header("Visualización de Datos")
        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de Barras Moderno: Distribución de Sentimientos
            st.subheader("Distribución de Sentimientos")
            sentiment_counts = df_analizado['sentimiento'].value_counts()
            fig_bar = px.bar(
                sentiment_counts,
                x=sentiment_counts.index,
                y=sentiment_counts.values,
                title="Conteo de Comentarios por Sentimiento",
                labels={'x': 'Sentimiento', 'y': 'Número de Comentarios'},
                color=sentiment_counts.index,
                text_auto=True
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            # Gráfico de Anillo Moderno: Distribución de Temas
            st.subheader("Distribución de Temas")
            topic_counts = df_analizado['tema'].value_counts()
            fig_pie = px.pie(
                topic_counts,
                values=topic_counts.values,
                names=topic_counts.index,
                title="Proporción de Comentarios por Tema",
                hole=0.4,  # Esto crea el efecto de "anillo"
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)

        # 3. Gráfico Avanzado: Sentimientos por Tema
        st.header("Análisis Detallado")
        st.subheader("Sentimientos dentro de cada Tema")
        sentiment_by_topic = df_analizado.groupby(['tema', 'sentimiento']).size().reset_index(name='conteo')
        fig_stacked_bar = px.bar(
            sentiment_by_topic,
            x='tema',
            y='conteo',
            color='sentimiento',
            title='Desglose de Sentimientos por Tema',
            labels={'tema': 'Tema', 'conteo': 'Número de Comentarios', 'sentimiento': 'Sentimiento'}
        )
        st.plotly_chart(fig_stacked_bar, use_container_width=True)


        # 4. Tabla de Resultados
        st.header("Datos Analizados")
        st.dataframe(df_analizado)
    else:
        st.error("El archivo CSV debe contener una columna llamada 'comentario'.")