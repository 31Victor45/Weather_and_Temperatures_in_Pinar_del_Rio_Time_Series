import pandas as pd
import requests

# 1. Definir los parámetros de la API Open-Meteo, usando Pinar del Río
LATITUD = 22.4167       # Latitud de Pinar del Río, Cuba
LONGITUD = -83.6961     # Longitud de Pinar del Río, Cuba
FECHA_INICIO = "2024-01-01"
FECHA_FIN = "2025-11-01"
VARIABLES = "temperature_2m_max,temperature_2m_min"
ZONA_HORARIA = "America/Havana"
URL_BASE = "https://archive-api.open-meteo.com/v1/archive"

# 2. Construir la URL completa para la solicitud
parametros = {
    "latitude": LATITUD,
    "longitude": LONGITUD,
    "start_date": FECHA_INICIO,
    "end_date": FECHA_FIN,
    "daily": VARIABLES,
    "timezone": ZONA_HORARIA,
}

# 3. Realizar la solicitud HTTP y obtener la respuesta JSON
try:
    respuesta = requests.get(URL_BASE, params=parametros)
    respuesta.raise_for_status()  # Lanza un error si la solicitud no fue exitosa
    datos = respuesta.json()

    # 4. Procesar los datos y crear un DataFrame de Pandas
    if 'daily' in datos:
        # Extraer las series de tiempo del JSON
        fechas = datos['daily']['time']
        temp_max = datos['daily']['temperature_2m_max']
        temp_min = datos['daily']['temperature_2m_min']

        # Crear el DataFrame
        df_clima_pr = pd.DataFrame({
            'Fecha': fechas,
            'Temp_Maxima_C': temp_max,
            'Temp_Minima_C': temp_min
        })

        # Convertir la columna de Fecha al formato datetime
        df_clima_pr['Fecha'] = pd.to_datetime(df_clima_pr['Fecha'])
        df_clima_pr = df_clima_pr.set_index('Fecha')

        # 5. Exportar el DataFrame a un archivo CSV
        nombre_archivo = "pinar_del_rio_temperaturas_2024_2025.csv"
        df_clima_pr.to_csv(nombre_archivo)

        print("✅ Extracción y guardado exitoso.")
        print(f"Los datos de Pinar del Río se han guardado en: {nombre_archivo}")
        print("\nPrimeras 5 filas del DataFrame:")
        print(df_clima_pr.head())
    else:
        print("❌ Error: La respuesta de la API no contiene el bloque 'daily'.")

except requests.exceptions.RequestException as e:
    print(f"❌ Error al conectar con la API: {e}")