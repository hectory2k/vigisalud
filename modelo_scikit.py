import requests
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

url = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/consultas_historicas"
api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsYmN6Zmx5Z296ZnZ3eWlsaGVzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5NDM0NTAsImV4cCI6MjA5NDUxOTQ1MH0.EiNp2HRocIqW4yStNxBoHgDN-EfFZvPv_Uc5ETo0wYg"

headers = {
    "apikey": api_key,
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 1. Leer datos
response = requests.get(url + "?select=*", headers=headers)
datos = response.json()
print(f"Datos leidos: {len(datos)} registros")

# 2. Preparar datos
fechas_str = [d["fecha"] for d in datos]
consultas = [d["consultas"] for d in datos]
zonas = [d["zona"] for d in datos]

fechas = [datetime.strptime(f, "%Y-%m-%d") for f in fechas_str]
fecha_min = min(fechas)
dias = [(f - fecha_min).days for f in fechas]
meses = [f.month for f in fechas]

# 3. Armar matriz de features
X = np.array([[dias[i], meses[i], zonas[i]] for i in range(len(datos))], dtype=object)
y = np.array(consultas)

# 4. Pipeline de preprocesamiento
preprocessor = ColumnTransformer(
    transformers=[
        ('num', SimpleImputer(strategy='median'), [0, 1]),
        ('cat', OneHotEncoder(handle_unknown='ignore'), [2])
    ]
)

# 5. Pipeline completo
modelo = Pipeline([
    ('preprocessor', preprocessor),
    ('model', RandomForestRegressor(n_estimators=10, random_state=42))
])

modelo.fit(X, y)
print("Modelo entrenado con pipeline robusto")

# 6. Predecir próximos 14 días
predicciones = []
ultimo_dia = max(dias)

for offset in range(1, 15):
    dia_pred = ultimo_dia + offset
    fecha_pred = fecha_min + timedelta(days=int(dia_pred))
    mes_pred = fecha_pred.month
    
    for zona in list(set(zonas)):
        X_pred = np.array([[dia_pred, mes_pred, zona]], dtype=object)
        consultas_pred = int(modelo.predict(X_pred)[0])
        
        predicciones.append({
            "fecha": fecha_pred.strftime("%Y-%m-%d"),
            "zona": zona,
            "consultas_predichas": max(0, consultas_pred)
        })
        print(f"Zona {zona} | {fecha_pred.strftime('%Y-%m-%d')} | {max(0, consultas_pred)} consultas")

# 7. Guardar en Supabase
url_pred = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/predicciones"
headers_pred = {
    "apikey": api_key,
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

requests.delete(url_pred + "?id=gt.0", headers=headers_pred)
for pred in predicciones:
    requests.post(url_pred, headers=headers_pred, json=pred)

print(f"✅ {len(predicciones)} predicciones guardadas con pipeline robusto")
