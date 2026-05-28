import requests

url = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/consultas_historicas"
api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsYmN6Zmx5Z296ZnZ3eWlsaGVzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5NDM0NTAsImV4cCI6MjA5NDUxOTQ1MH0.EiNp2HRocIqW4yStNxBoHgDN-EfFZvPv_Uc5ETo0wYg"

headers = {
    "apikey": api_key,
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

datos = [
    {"fecha": "2026-05-01", "zona": "Norte", "consultas": 120, "tipo": "general"},
    {"fecha": "2026-05-02", "zona": "Sur", "consultas": 85, "tipo": "pediatria"},
    {"fecha": "2026-05-03", "zona": "Norte", "consultas": 135, "tipo": "general"},
    {"fecha": "2026-05-04", "zona": "Sur", "consultas": 92, "tipo": "pediatria"}
]

for dato in datos:
    response = requests.post(url, headers=headers, json=dato)
    if response.status_code == 201:
        print(f"✅ Insertado: {dato['fecha']} - {dato['zona']}")
    else:
        print(f"❌ Error: {response.status_code}")

print("✅ Datos guardados en Supabase")
