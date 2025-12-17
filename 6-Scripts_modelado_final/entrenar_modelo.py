# entrenar_modelo.py
import pandas as pd
from statsmodels.tsa.statespace.varmax import VARMAX
import joblib
import warnings

warnings.filterwarnings("ignore")

def entrenar_y_guardar():
    print("🚀 Cargando datos estacionarios...")
    # Cargamos los datos que ya tienen Box-Cox y Diferenciación aplicada
    df = pd.read_csv('datos_temperaturas_estacionarios.csv', index_col='Fecha', parse_dates=True)
    
    # Entrenamos el modelo VARMAX(2, 1) sin estacionalidad (según decidimos por Ockham)
    print("🧠 Entrenando modelo VARMAX de producción (esto puede tardar un poco)...")
    modelo = VARMAX(df, order=(2, 1))
    resultado = modelo.fit(disp=False)
    
    # Guardamos el modelo entrenado en un archivo .pkl
    joblib.dump(resultado, 'modelo_final.pkl')
    print("✅ Modelo guardado exitosamente como 'modelo_final.pkl'")

if __name__ == "__main__":
    entrenar_y_guardar()