# 🏥 VigiSalud - Roadmap

## ✅ Fase 1: MVP Funcional
- Pipeline de ingesta (`ingesta.py`)
- Datos reales del World Bank API (`datos_reales.py`)
- Datos estacionales simulados (`datos_extra.py`)
- Base de datos PostgreSQL en Supabase
- Modelo v1: promedio estacional con numpy (`promedio.py`)
- Dashboard en Supabase Charts
- Infraestructura: Azure App Service + Termux (Moto G65)
- Repositorio público en GitHub

## ✅ Fase 2: Motor Avanzado
- Modelo v2: Random Forest con scikit-learn (`modelo_scikit.py`)
- Automatización diaria con GitHub Actions (6 AM)
- Seguridad: Row Level Security activado en Supabase
- Asistente IA de Supabase configurado

## 🔜 Fase 3: Próximos pasos
- Dashboard avanzado con Looker Studio
- Rotación automática de datos viejos
- Ingesta diaria automatizada
- Incorporar variables externas (clima, contaminación)

## 🫀 Fase 4: VigiSalud Vascular
- Dataset cardiovascular real (infarto/ACV)
- Variables clínicas: edad, sexo, presión arterial
- Variables ambientales: temperatura, humedad, contaminación
- Modelo de clasificación de riesgo a 48-72 horas
- Validación médica profesional
- Dashboard con semáforo de riesgo por zona
