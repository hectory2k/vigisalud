import requests
import numpy as np
from datetime import datetime, timedelta

url = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/consultas_historicas"
api_key = "TU_API_KEY"

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

# 3. Entrenar por zona
zonas_unicas = list(set(zonas))
predicciones = []

for zona in zonas_unicas:
    idx = [i for i, z in enumerate(zonas) if z == zona]
    X = np.array([dias[i] for i in idx]).reshape(-1, 1)
    y = np.array([consultas[i] for i in idx])
    
    coef = np.polyfit(X.flatten(), y, 1)
    a, b = coef
    
    ultimo_dia = max(X.flatten())
    for dia_futuro in range(1, 8):
        dia_pred = int(ultimo_dia + dia_futuro)
        consultas_pred = int(a * dia_pred + b)
        fecha_pred = fecha_min + timedelta(days=dia_pred)
        
        predicciones.append({
            "fecha": fecha_pred.strftime("%Y-%m-%d"),
            "zona": zona,
            "consultas_predichas": max(0, consultas_pred)
        })
        print(f"Zona {zona} | {fecha_pred.strftime('%Y-%m-%d')} | {max(0, consultas_pred)} consultas")

# 4. Guardar predicciones
url_pred = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/predicciones"
headers_pred = {
    "apikey": api_key,
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

for pred in predicciones:
    requests.post(url_pred, headers=headers_pred, json=pred)

print(f"✅ {len(predicciones)} predicciones guardadas en Supabase")
