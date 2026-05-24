
# 🏥 VigiSalud - MVP

Predicción de picos de consultas ortopédicas con datos abiertos y modelos estacionales.  
Desarrollado como proyecto para **Humai** desde un Moto G65.

## 🎯 Objetivo
Anticipar picos de consultas por zona con 1-2 semanas de anticipación para priorizar operativos y recursos en traumatología.

## 📦 Instalación
git clone https://github.com/hectory2k/vigisalud.git
cd vigisalud
pip install -r requirements.txt

## ▶️ Uso rápido
python ingesta.py
python datos_reales.py
python datos_extra.py
python promedio.py

## 🧠 Modelos
promedio.py: Media estacional (numpy) - Manual
modelo_scikit.py: Random Forest + TimeSeriesSplit - Automático (6 AM)

## 📊 Resultados
MAE: 55 consultas
RMSE: 73 consultas
Registros entrenamiento: 54
Zonas: Norte, Sur, Centro

## 🩺 Impacto clínico
El modelo anticipa variaciones de hasta 70 consultas extra en una zona. El hospital puede reforzar la guardia traumatológica y redistribuir recursos antes del pico.

## 🔄 Arquitectura
