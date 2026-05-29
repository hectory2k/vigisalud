import os
import sys
import requests
from dotenv import load_dotenv
load_dotenv()

DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Obtener predicciones de Supabase
url = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/predicciones?select=*&order=fecha.asc&limit=21"
headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
predicciones = requests.get(url, headers=headers).json()

zonas = {}
for p in predicciones:
    if p["zona"] not in zonas:
        zonas[p["zona"]] = []
    zonas[p["zona"]].append(p)

resumen = ""
for zona, preds in zonas.items():
    max_pred = max(preds, key=lambda x: x["consultas_predichas"])
    umbral = "130" if zona == "Norte" else "110" if zona == "Centro" else "90"
    resumen += f"- {zona}: pico de {max_pred['consultas_predichas']} consultas el {max_pred['fecha']} (umbral: {umbral}).\n"

# Llamar a DeepSeek
deepseek_url = "https://api.deepseek.com/chat/completions"
deepseek_headers = {
    "Authorization": f"Bearer {DEEPSEEK_KEY}",
    "Content-Type": "application/json"
}

prompt = f"""Sos un médico especialista en gestión hospitalaria y ortopedia.
Predicciones de VigiSalud para los próximos 7 días:
{resumen}
Redactá un parte clínico de 5 líneas para el jefe de guardia. Incluí zonas en alerta, acciones recomendadas, y firmá como VigiSalud v3.5 + DeepSeek."""

data = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 300
}

response = requests.post(deepseek_url, headers=deepseek_headers, json=data)
parte = response.json()["choices"][0]["message"]["content"]
print("✅ Parte clínico con DeepSeek:")
print(parte)
