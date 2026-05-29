#!/bin/bash
echo "🚀 VigiSalud v3.5 — Demo en vivo"
echo "================================"
echo ""
echo "1️⃣  Ejecutando modelo predictivo..."
python modelo_v3_5.py | tail -10
echo ""
echo "2️⃣  Generando parte clínico con NVIDIA Llama 3.3..."
python parte_clinico_nvidia.py
echo ""
echo "3️⃣  Enviando alertas a Telegram..."
python -c "
from alertas_telegram import enviar_alerta
enviar_alerta('Norte', 141, dia='01/06')
enviar_alerta('Centro', 121, dia='01/06')
"
echo ""
echo "✅ Demo completada."
