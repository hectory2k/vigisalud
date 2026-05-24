# 🏥 VigiSalud - MVP

App de prediccion de consultas para salud publica. Desarrollado como proyecto para Humai desde un Moto G65.

## 🎯 Objetivo
Anticipar picos de consultas por zona con 1-2 semanas de anticipacion.

## 🛠️ Tecnologias
- 🐍 Python 3 + numpy + requests
- 🐘 Supabase (PostgreSQL)
- 📱 Termux (Moto G65)
- ☁️ Azure App Service

## 📂 Scripts
- 🟢 ingesta.py - Datos simulados
- 🌐 datos_reales.py - World Bank API
- 📊 datos_extra.py - Datos estacionales
- 🔬 modelo.py - Regresion lineal v1
- ⭐ promedio.py - Modelo estacional v2

## 🚀 Ejecucion
python ingesta.py
python datos_reales.py
python datos_extra.py
python promedio.py

## 📈 Dashboard
Grafico en Supabase Table Editor con predicciones por zona.

## 🧠 Arquitectura del Pipeline

```mermaid
flowchart TD
    A[📊 Fuentes de Datos] --> B[🐍 Scripts de Ingesta]
    B --> C[🐘 Supabase PostgreSQL]
    C --> D[🧠 Modelo Predictivo]
    D --> E[📈 Predicciones]
    E --> F[📊 Dashboard]
    
    subgraph Fuentes
        A1[🌐 World Bank API]
        A2[📋 Datos Estacionales]
        A3[🏥 Datos Cardiovasculares]
    end
    
    subgraph Ingesta
        B1[datos_reales.py]
        B2[datos_extra.py]
        B3[ingesta.py]
    end
    
    subgraph Modelos
        D1[promedio.py - numpy]
        D2[modelo_scikit.py - Random Forest]
        D3[GitHub Actions - 6 AM]
    end
    
    subgraph Dashboard
        F1[Supabase Charts]
        F2[Looker Studio]
    end
    
    A1 --> B1
    A2 --> B2
    A3 --> B3
    B1 --> C
    B2 --> C
    B3 --> C
    C --> D1
    C --> D2
    D2 --> D3
    D1 --> E
    D2 --> E
    E --> F1
    E --> F2
```

## 👤 Autor
Hector | github.com/hectory2k
