# coding: utf-8
import requests
import numpy as np
from datetime import datetime, timedelta

SUPABASE_URL = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/consultas_historicas"
API_KEY = "TU_API_KEY"

headers = {
    "apikey": API_KEY,
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# Generar 3 años de datos (2023, 2024, 2025)
zonas = ["Norte", "Sur", "Centro"]
tipos = ["general", "pediatria", "traumatologia"]
base_consultas = {"Norte": 120, "Sur": 95, "Centro": 110}

print("Generando datos simulados con estacionalidad...")
contador = 0

for anio in [2023, 2024, 2025]:
    for mes in range(1, 13):
        for dia in [5, 15, 25]:  # 3 registros por mes por zona = más variedad
            for zona in zonas:
                # Efecto estacional: más consultas en invierno (jun-ago), menos en verano (dic-feb)
                if mes in [6, 7, 8]:
                    factor_estacional = np.random.normal(1.3, 0.1)
                elif mes in [12, 1, 2]:
                    factor_estacional = np.random.normal(0.8, 0.1)
                else:
                    factor_estacional = np.random.normal(1.0, 0.1)

                # Tendencia creciente leve año a año
                tendencia = 1 + (anio - 2023) * 0.05

                # Efecto día de semana (simulado)
                fecha = datetime(anio, mes, dia)
                if fecha.weekday() == 0:  # Lunes: más consultas
                    factor_dia = 1.2
                elif fecha.weekday() in [5, 6]:  # Fin de semana: menos
                    factor_dia = 0.7
                else:
                    factor_dia = 1.0

                consultas = int(base_consultas[zona] * factor_estacional * tendencia * factor_dia)
                consultas += int(np.random.normal(0, 10))  # Ruido aleatorio
                consultas = max(10, consultas)

                dato = {
                    "fecha": f"{anio}-{mes:02d}-{dia:02d}",
                    "zona": zona,
                    "consultas": consultas,
                    "tipo": tipos[contador % 3]
                }

                resp = requests.post(SUPABASE_URL, headers=headers, json=dato)
                if resp.status_code == 201:
                    contador += 1
                    if contador % 50 == 0:
                        print(f"✅ {contador} registros insertados...")

print(f"\n🎉 {contador} registros nuevos insertados en Supabase")
