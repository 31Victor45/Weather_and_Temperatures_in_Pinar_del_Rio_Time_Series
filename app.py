# app.py
import streamlit as st
import pandas as pd
import joblib
import numpy as np
from datetime import datetime
from clima_utils import reverse_transform, fetch_api_real_data, PARAMS

st.set_page_config(page_title="Predicción Climática Pinar del Río", layout="wide")

st.title("🌦️ Sistema de Predicción de Temperaturas")
st.write("Modelo VARMAX (2,1) optimizado para Pinar del Río")

@st.cache_resource
def load_model():
    return joblib.load('6-Scripts_modelado_final/modelo_final.pkl')

modelo = load_model()


st.sidebar.header("📅 Consulta a Futuro")
fecha_objetivo = st.sidebar.date_input(
    "Selecciona una fecha (Hasta 2050):",
    min_value=datetime.today(),
    max_value=datetime(2050, 12, 31)
)


# --- BARRA LATERAL: CONSULTA PUNTUAL ---
# 📸 AGREGAR IMAGEN EN LA BARRA LATERAL
# Puedes usar una URL de una imagen de clima o una local 'clima.jpg'
#st.sidebar.image("7-Img_app/img1.png", 
#                 caption="Pronóstico Pinar del Río", use_container_width=True)


if st.sidebar.button("Predecir Fecha"):
    ultima_fecha_hist = datetime.strptime(PARAMS['ultima_fecha_historica'], '%Y-%m-%d').date()
    pasos = (fecha_objetivo - ultima_fecha_hist).days
    
    if pasos <= 0:
        st.sidebar.error("Selecciona una fecha posterior a Noviembre 2025.")
    else:
        fcast = modelo.get_forecast(steps=pasos).predicted_mean
        t_max, t_min = reverse_transform(fcast)
        
        st.sidebar.success(f"Resultados para {fecha_objetivo}:")
        st.sidebar.metric("🌡️ Máxima", f"{round(t_max.iloc[-1], 1)} ºC")
        st.sidebar.metric("🧊 Mínima", f"{round(t_min.iloc[-1], 1)} ºC")

# --- CUERPO PRINCIPAL: SELECCIÓN Y COMPARATIVA ---
st.header("📊 Comparativa Real vs. Modelo")

tipo_var = st.selectbox(
    "¿Qué variable deseas analizar?",
    ["Temperaturas Máximas", "Temperaturas Mínimas"]
)

if 'datos_comparativos' not in st.session_state:
    st.session_state.datos_comparativos = None

if st.button("🔄 Cargar/Actualizar Datos de la API"):
    with st.spinner("Conectando con Open-Meteo..."):
        df_real = fetch_api_real_data(days=8)
        ultima_fecha_hist = datetime.strptime(PARAMS['ultima_fecha_historica'], '%Y-%m-%d').date()
        dias_desde_historia = (datetime.today().date() - ultima_fecha_hist).days
        
        fcast_recent = modelo.get_forecast(steps=dias_desde_historia).predicted_mean
        p_max, p_min = reverse_transform(fcast_recent)
        
        df_comp = df_real.copy()
        df_comp['Max_Pred'] = p_max.iloc[-len(df_real):].values
        df_comp['Min_Pred'] = p_min.iloc[-len(df_real):].values
        st.session_state.datos_comparativos = df_comp

# --- VISUALIZACIÓN Y CONCLUSIONES ---
if st.session_state.datos_comparativos is not None:
    df = st.session_state.datos_comparativos
    col1, col2 = st.columns([1, 2])
    
    if tipo_var == "Temperaturas Máximas":
        with col1:
            st.write("📋 **Tabla: Máximas (ºC)**")
            st.dataframe(df[['Max_Real', 'Max_Pred']].style.format("{:.1f}"))
        with col2:
            st.write("🔥 **Gráfico: Máximas (Real vs Predicho)**")
            st.scatter_chart(df[['Max_Real', 'Max_Pred']], color=["#0000FF", "#FF0000"])
        
        # 📝 CONCLUSIONES PARA USUARIO PROMEDIO (MÁXIMAS)
        error_avg = np.mean(np.abs(df['Max_Real'] - df['Max_Pred']))
        st.subheader("🧐 ¿Por qué hay diferencias?")
        st.info(f"""
        **Análisis sencillo:** Notarás que la diferencia promedio es de apenas **{error_avg:.1f} ºC**. 
        
        **Justificación científica:** El modelo es muy bueno detectando la tendencia general del calor en Pinar del Río. Sin embargo, factores locales como una nube pasajera, una brisa repentina o el asfalto caliente pueden variar la temperatura real en 1 o 2 grados. El modelo matemático predice el "comportamiento esperado", pero el clima siempre tiene un pequeño componente de sorpresa que lo hace único cada día.
        """)

    else:
        with col1:
            st.write("📋 **Tabla: Mínimas (ºC)**")
            st.dataframe(df[['Min_Real', 'Min_Pred']].style.format("{:.1f}"))
        with col2:
            st.write("🍧 **Gráfico: Mínimas (Real vs Predicho)**")
            st.scatter_chart(df[['Min_Real', 'Min_Pred']], color=["#228B22", "#FF8C00"])
            
        # 📝 CONCLUSIONES PARA USUARIO PROMEDIO (MÍNIMAS)
        error_avg = np.mean(np.abs(df['Min_Real'] - df['Min_Pred']))
        st.subheader("🧐 ¿Por qué hay diferencias?")
        st.info(f"""
        **Análisis sencillo:** La diferencia promedio en las madrugadas es de **{error_avg:.1f} ºC**.
        
        **Justificación científica:** Las temperaturas mínimas son influenciadas por la humedad y el enfriamiento del suelo durante la noche. Nuestro modelo utiliza la "inercia térmica" (lo que pasó ayer) para decirnos qué pasará hoy. Una diferencia pequeña es normal y esperada, ya que indica que el modelo está capturando correctamente el ciclo natural del clima sin dejarse engañar por cambios bruscos irrelevantes.
        """)
else:
    st.info("Haz clic en el botón superior para cargar la comparativa de los últimos 7 días.")