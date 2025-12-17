# clima_utils.py
import pandas as pd
import numpy as np
import json
import joblib
import requests
from datetime import datetime

with open('6-Scripts_modelado_final/parametros_reversion.json', 'r') as f:
    PARAMS = json.load(f)

def reverse_transform(diff_forecast):
    l_max = PARAMS['boxcox_lambda']['maxima']
    l_min = PARAMS['boxcox_lambda']['minima']
    last_bc_max = PARAMS['ultimo_valor_boxcox']['maxima']
    last_bc_min = PARAMS['ultimo_valor_boxcox']['minima']
    
    # Invertir Diferenciación
    bc_max_pred = last_bc_max + np.cumsum(diff_forecast['Diff_BoxCox_Max'])
    bc_min_pred = last_bc_min + np.cumsum(diff_forecast['Diff_BoxCox_Min'])
    
    # Invertir Box-Cox
    temp_max = np.power((l_max * bc_max_pred) + 1, 1/l_max)
    temp_min = np.power((l_min * bc_min_pred) + 1, 1/l_min)
    
    return temp_max, temp_min

def fetch_api_real_data(days=7):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 22.4167,
        "longitude": -83.6961,
        "past_days": days,
        "forecast_days": 1,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "America/Havana"
    }
    r = requests.get(url, params=params)
    data = r.json()
    df = pd.DataFrame({
        "Fecha": pd.to_datetime(data['daily']['time']),
        "Max_Real": data['daily']['temperature_2m_max'],
        "Min_Real": data['daily']['temperature_2m_min']
    }).set_index("Fecha")
    return df.iloc[:-1] # Solo días pasados completos