import os
import sys
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Claves
NVIDIA_KEY = os.getenv("NVIDIA_API_KEY")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not NVIDIA_KEY:
    print("❌ ERROR: No se encontró NVIDIA_API_KEY en el .env")
    sys.exit(1)

# Obtener predicciones de Supabase
url = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/predicciones?select=*&order=fecha.asc&limit=21"
headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
predicciones = requests.get(url, headers=headers).json()

# Agrupar por zona
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

# Cliente NVIDIA
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_KEY
)

MODEL = "meta/llama-3.3-70b-instruct"

prompt = f"""Sos un médico especialista en gestión hospitalaria y ortopedia.
Predicciones de VigiSalud para los próximos 7 días:
{resumen}
Redactá un parte clínico de 5 líneas para el jefe de guardia. Incluí:
1. Zonas en alerta con números exactos
2. Acción recomendada (reforzar guardia, preparar quirófano)
3. No inventes nombres. Firmá como VigiSalud v3.5 + NVIDIA Llama 3.3."""

print(f"🤖 Modelo: {MODEL}")
print(f"📊 Predicciones procesadas: {len(predicciones)}")
print("-" * 50)

try:
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        top_p=0.95,
        max_tokens=2048,
        stream=True
    )

    for chunk in completion:
        if not getattr(chunk, "choices", None):
            continue
        delta = chunk.choices[0].delta
        if delta and delta.content is not None:
            print(delta.content, end="", flush=True)

    print("\n" + "-" * 50)
    print("✅ Parte clínico generado con NVIDIA Llama 3.3")

except Exception as e:
    print(f"\n❌ Error: {e}")
