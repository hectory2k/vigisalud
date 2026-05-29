# 📋 Changelog — VigiSalud

## v3.5 — Mayo 2026 🚀
- Modelo Random Forest con 14 features
- MAE 7.5 consultas/día
- Backtesting 13.4 sobre 30 días reales
- Alertas por Telegram con umbrales por zona
- Parte clínico automático con NVIDIA Llama 3.3
- Ollama + phi3:mini para demos sin internet
- Dashboard Chart.js + GitHub Pages
- Configuración centralizada en `config.py`
- Badges: Python, MAE, MIT, Moto G56, NVIDIA

## v2.1 — Mayo 2026 📈
- 378 registros de entrenamiento (+324)
- Features: lags (1, 7, 14), media móvil, feriados, fin de semana
- MAE 41.3 → 7.5 con Ridge y Random Forest
- GitHub Actions automatizado (6 AM)

## v2.0 — Mayo 2026 ⚡
- Integración con Supabase
- Pipeline robusto: SimpleImputer + OneHotEncoder
- TimeSeriesSplit + MAE/RMSE
- Logs de métricas en `logs_metricas`

## v1.0 — Mayo 2026 🛠️
- MVP funcional: ingesta, modelo base, dashboard
- 54 registros iniciales
- MAE 55 (baseline)
- Stack: Termux + Azure + Supabase
