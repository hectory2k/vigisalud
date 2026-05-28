import requests

# 1. Bajar datos reales del World Bank (camas de hospital en Argentina)
url = "https://api.worldbank.org/v2/country/ARG/indicator/SH.MED.BEDS.ZS?format=json&per_page=50"
response = requests.get(url)
data = response.json()

registros = data[1]

# 2. Preparar datos para Supabase
url_supabase = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/consultas_historicas"
api_key = "TU_API_KEY"

headers = {
    "apikey": api_key,
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

contador = 0
limite = 50

for r in registros:
    if contador >= limite:
        break
    if r["value"] is not None:
        anio = r["date"]
        camas = float(r["value"])
        consultas = int(camas * 100)
        
        # Una zona por año
        zona = "Norte" if int(anio) % 2 == 0 else "Sur"
        
        dato = {
            "fecha": f"{anio}-06-15",
            "zona": zona,
            "consultas": consultas,
            "tipo": "general"
        }
        
        resp = requests.post(url_supabase, headers=headers, json=dato)
        if resp.status_code == 201:
            contador += 1
            print(f"✅ {contador}/50: {anio} - {zona} - {consultas} consultas")

print(f"✅ {contador} datos reales guardados en Supabase")
