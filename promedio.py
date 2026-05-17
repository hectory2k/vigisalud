import requests
import numpy as np
from datetime import datetime, timedelta

url = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/consultas_historicas"
api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsYmN6Zmx5Z296ZnZ3eWlsaGVzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5NDM0NTAsImV4cCI6MjA5NDUxOTQ1MH0.EiNp2HRocIqW4yStNxBoHgDN-EfFZvPv_Uc5ETo0wYg"

headers = {
    "apikey": api_key,
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = requests.get(url + "?select=*", headers=headers)
datos = response.json()
print(f"Datos leidos: {len(datos)} registros")

# Promedio por zona y mes
from collections import defaultdict
promedios = defaultdict(lambda: defaultdict(list))

for d in datos:
    fecha = datetime.strptime(d["fecha"], "%Y-%m-%d")
    mes = fecha.month
    zona = d["zona"]
    promedios[zona][mes].append(d["consultas"])

promedio_final = {}
for zona, meses in promedios.items():
    promedio_final[zona] = {}
    for mes, valores in meses.items():
        promedio_final[zona][mes] = int(np.mean(valores))
    print(f"Zona {zona}: {promedio_final[zona]}")

# Predecir 2 semanas
predicciones = []
fecha_actual = datetime(2026, 5, 16)

for dia_offset in range(1, 15):
    fecha_pred = fecha_actual + timedelta(days=dia_offset)
    mes_pred = fecha_pred.month
    
    for zona in promedio_final:
        if mes_pred in promedio_final[zona]:
            consultas = promedio_final[zona][mes_pred]
        else:
            consultas = int(np.mean(list(promedio_final[zona].values())))
        
        predicciones.append({
            "fecha": fecha_pred.strftime("%Y-%m-%d"),
            "zona": zona,
            "consultas_predichas": consultas
        })
        print(f"Zona {zona} | {fecha_pred.strftime('%Y-%m-%d')} | {consultas} consultas")

# Guardar
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

print(f"✅ {len(predicciones)} predicciones guardadas en Supabase")
