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
- Pipeline robusto: SimpleImputer + OneHotEncoder + RandomForest
- Automatización diaria con GitHub Actions (6 AM)
- Seguridad: Row Level Security activado en Supabase
- Asistente IA de Supabase configurado
- Diagrama de arquitectura (Mermaid)
- Vista SQL corregida (`vw_promedio_consultas_predichas_por_zona_mes`)

## 🔜 Fase 3: Próximos pasos
- Dashboard avanzado con Looker Studio
- Rotación automática de datos viejos
- Ingesta diaria automatizada
- Incorporar variables externas (clima, contaminación)
- Gradient Boosting como alternativa a Random Forest
- Regresión Logística para clasificación de riesgo (alto/bajo)

## 🫀 Fase 4: VigiSalud Vascular
- Dataset cardiovascular real (infarto/ACV)
- Variables clínicas: edad, sexo, presión arterial
- Variables ambientales: temperatura, humedad, contaminación
- Modelo de clasificación de riesgo a 48-72 horas
- Validación médica profesional
- Dashboard con semáforo de riesgo por zona

## 🧠 Algoritmos en pipeline
| Algoritmo | Estado | Uso |
|-----------|--------|-----|
| Regresión Lineal (numpy) | ✅ En producción | Baseline |
| Random Forest (scikit-learn) | ✅ En producción | Modelo principal |
| Gradient Boosting | 🔜 Planeado | Mejora de precisión |
| Regresión Logística | 🔜 Planeado | Clasificación de riesgo |

## ⚙️ Hiperparámetros y criterios de entrenamiento
| Parámetro | Valor actual | Criterio |
|-----------|-------------|----------|
| `n_estimators` | 10 | Bajo para ejecución rápida (6 AM diario) |
| `random_state` | 42 | Resultados reproducibles |
| Imputación numérica | Mediana | Robusto a outliers |
| Codificación categórica | OneHotEncoder | Soporta nuevas zonas sin error |
| Validación | Manual (MVP) | Próximo: train/test split + métricas |

### Próximos ajustes planeados
- Aumentar `n_estimators` a 50-100 cuando haya más datos
- Agregar `max_depth` para evitar overfitting
- Implementar validación cruzada para medir estabilidad
