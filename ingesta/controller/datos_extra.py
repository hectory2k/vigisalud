import requests

url_supabase = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/consultas_historicas"
api_key = "TU_API_KEY"

headers = {
    "apikey": api_key,
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# Datos simulados con patrón estacional (más consultas en invierno)
zonas = ["Norte", "Sur", "Centro"]
tipos = ["general", "pediatria", "cardiologia"]
base_consultas = {"Norte": 300, "Sur": 250, "Centro": 280}

contador = 0
limite = 35  # Para llegar a 50 total

for anio in [2023, 2024, 2025]:
    for mes in range(1, 13):
        if contador >= limite:
            break
        for zona in zonas:
            if contador >= limite:
                break
            # Más consultas en meses fríos (mayo-agosto)
            factor_invierno = 1.3 if mes in [5,6,7,8] else 1.0
            consultas = int(base_consultas[zona] * factor_invierno + (anio - 2022) * 10)
            
            dato = {
                "fecha": f"{anio}-{mes:02d}-15",
                "zona": zona,
                "consultas": consultas,
                "tipo": tipos[contador % 3]
            }
            
            resp = requests.post(url_supabase, headers=headers, json=dato)
            if resp.status_code == 201:
                contador += 1
                print(f"✅ {contador}/35: {dato['fecha']} - {zona} - {consultas} consultas ({dato['tipo']})")

print(f"✅ {contador} datos extra guardados")
