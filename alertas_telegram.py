# alertas_telegram.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

UMBRAL_ZONA = {
    "Norte": 130,
    "Centro": 110,
    "Sur": 90
}

def enviar_alerta(zona, prediccion, dia=None):
    umbral = UMBRAL_ZONA.get(zona, 100)
    
    if prediccion > umbral:
        exceso = prediccion - umbral
        porcentaje = (exceso / umbral) * 100
        
        fechaTexto = f" para el {dia}" if dia else ""
        
        mensaje = f"""
⚠️ **ALERTA VigiSalud v3.5**

📍 Zona: **{zona}**{fechaTexto}
📊 Predicción: **{prediccion}** consultas
🎯 Umbral: {umbral} consultas
📈 Exceso: **+{exceso} consultas** ({porcentaje:.0f}% sobre normal)
🕐 Anticipación: 1-2 semanas

🩺 **Acciones recomendadas:**
✅ Reforzar guardia traumatológica
✅ Coordinar cirujanos adicionales
✅ Preparar {max(1, exceso//10)} box(es) extra de urgencias
✅ Verificar stock de insumos ortopédicos

📅 *Generado automaticamente por VigiSalud v3.5*
"""
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": mensaje,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                print(f"✅ Alerta enviada a {zona}: {prediccion} consultas")
                return True
            else:
                print(f"❌ Error enviando alerta: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Excepcion al enviar alerta: {e}")
            return False
    else:
        print(f"ℹ️ {zona}: {prediccion} consultas (dentro del umbral {umbral})")
        return True
