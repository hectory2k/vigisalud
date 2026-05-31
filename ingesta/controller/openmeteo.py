import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import os, sys, json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from prediccion.config import SUPABASE_URL, SUPABASE_KEY, COORDENADAS

OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"
BATCH_SIZE = 50
DIAS_HISTORICO = 90

def obtener_temperatura(zona: str, start: str, end: str) -> pd.DataFrame:
    lat, lon = COORDENADAS[zona]
    params = {
        "latitude": lat, "longitude": lon,
        "start_date": start, "end_date": end,
        "daily": "temperature_2m_mean",
        "timezone": "America/Argentina/Buenos_Aires"
    }
    try:
        r = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return pd.DataFrame({
            'fecha': data['daily']['time'],
            'temperatura_media': data['daily']['temperature_2m_mean']
        })
    except requests.RequestException as e:
        print(f"❌ Error Open-Meteo ({zona}): {e}")
        return pd.DataFrame()

def guardar_en_supabase(registros: List[Dict]) -> int:
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    guardados = 0
    for i in range(0, len(registros), BATCH_SIZE):
        lote = registros[i:i+BATCH_SIZE]
        r = requests.post(
            "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/clima",
            headers=headers,
            json=lote
        )
        if r.status_code in [200, 201]:
            guardados += len(lote)
        else:
            print(f"⚠️ Error lote {i}: {r.status_code} - {r.text[:100]}")
    return guardados

def main():
    print(f"🌡️ Obteniendo temperatura histórica ({DIAS_HISTORICO} días)...")
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=DIAS_HISTORICO)).strftime("%Y-%m-%d")
    total = 0

    for zona in COORDENADAS:
        df = obtener_temperatura(zona, start, end)
        if not df.empty:
            registros = [
                {"fecha": row['fecha'], "zona": zona, "temperatura_media": row['temperatura_media']}
                for _, row in df.iterrows()
            ]
            guardados = guardar_en_supabase(registros)
            total += guardados
            print(f"✅ {zona}: {guardados} registros")
        else:
            print(f"⚠️ {zona}: sin datos")

    print(f"✅ {total} registros guardados en Supabase")

if __name__ == "__main__":
    main()
