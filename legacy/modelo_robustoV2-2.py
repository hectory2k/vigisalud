# coding: utf-8
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error

print("🚀 VigiSalud - Modelo Robusto v2.3 | Feriados + Findes Optimizados")

# ==================== CONFIG ====================
SUPABASE_URL = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/consultas_historicas"
API_KEY = "TU_API_KEY"

headers = {"apikey": API_KEY, "Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
COORDENADAS = {"Norte": (-38.95, -68.06), "Centro": (-38.95, -68.06), "Sur": (-39.10, -67.80)}

# ==================== FERIADOS Y VACACIONES (Actualizado 2026) ====================
feriados_nacionales = [
    "2023-01-01","2023-02-20","2023-02-21","2023-03-24","2023-04-02","2023-04-06","2023-04-07","2023-05-01",
    "2023-05-25","2023-06-17","2023-06-19","2023-06-20","2023-07-09","2023-08-21","2023-10-09","2023-10-16",
    "2023-11-20","2023-12-08","2023-12-25",
    "2024-01-01","2024-02-12","2024-02-13","2024-03-24","2024-03-28","2024-03-29","2024-04-02","2024-05-01",
    "2024-05-25","2024-06-17","2024-06-20","2024-06-21","2024-07-09","2024-08-19","2024-10-11","2024-10-14",
    "2024-11-18","2024-12-08","2024-12-25",
    "2025-01-01","2025-03-24","2025-04-02","2025-04-18","2025-05-01","2025-05-25","2025-06-17","2025-06-20",
    "2025-06-21","2025-07-09","2025-08-18","2025-10-13","2025-11-24","2025-12-08","2025-12-25",
    "2026-01-01","2026-05-01","2026-05-25","2026-06-20","2026-07-09","2026-08-17","2026-10-12","2026-11-23","2026-12-08","2026-12-25"
]

def es_vacaciones(fecha):
    mes = fecha.month
    dia = fecha.day
    # Vacaciones de verano + julio
    if mes in [1, 2] or (mes == 12 and dia >= 15) or mes == 7:
        return 1
    return 0

# ==================== FUNCIONES CLIMA ====================
def get_historical_weather(lat, lon, start_date, end_date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat, "longitude": lon, 
        "start_date": start_date, "end_date": end_date, 
        "daily": "temperature_2m_mean", 
        "timezone": "America/Argentina/Buenos_Aires"
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        df_clima = pd.DataFrame({
            'fecha': data['daily']['time'], 
            'temperatura_media': data['daily']['temperature_2m_mean']
        })
        df_clima['fecha'] = pd.to_datetime(df_clima['fecha'])
        return df_clima
    except:
        return pd.DataFrame()

# ==================== 1. CARGAR DATOS ====================
response = requests.get(SUPABASE_URL + "?select=*&order=fecha.asc", headers=headers)
df = pd.DataFrame(response.json())
df['fecha'] = pd.to_datetime(df['fecha'])
print(f"📊 Datos: {len(df)} registros | {df['fecha'].min().date()} → {df['fecha'].max().date()}")

# ==================== 2. FEATURE ENGINEERING MEJORADO ====================
df = df.sort_values(['zona', 'fecha']).reset_index(drop=True)

fecha_min = df['fecha'].min()
df['dia'] = (df['fecha'] - fecha_min).dt.days
df['mes'] = df['fecha'].dt.month
df['dia_semana'] = df['fecha'].dt.weekday
df['es_fin_de_semana'] = (df['dia_semana'] >= 5).astype(int)

# Feriados y vacaciones
df['es_feriado'] = df['fecha'].dt.strftime('%Y-%m-%d').isin(feriados_nacionales).astype(int)
df['es_vacaciones'] = df['fecha'].apply(es_vacaciones)

# Feature combinada muy útil
df['es_no_laboral'] = ((df['es_fin_de_semana'] == 1) | 
                       (df['es_feriado'] == 1) | 
                       (df['es_vacaciones'] == 1)).astype(int)

# Lags y medias móviles
for lag in [1, 7, 14]:
    df[f'consultas_lag_{lag}'] = df.groupby('zona')['consultas'].shift(lag)

df['consultas_ma7'] = df.groupby('zona')['consultas'].transform(
    lambda x: x.rolling(7, min_periods=3).mean()
)
df['consultas_ma14'] = df.groupby('zona')['consultas'].transform(
    lambda x: x.rolling(14, min_periods=7).mean()
)

# Temperatura
print("🌡️ Obteniendo temperatura...")
for zona in df['zona'].unique():
    if zona in COORDENADAS:
        lat, lon = COORDENADAS[zona]
        clima = get_h
            lat, lon, 
            df['fecha'].min().strftime("%Y-%m-%d"), 
            df['fecha'].max().strftime("%Y-%m-%d")
        )
        if not clima.empty:
            clima['zona'] = zona
            df = df.merge(clima, on=['fecha', 'zona'], how='left')

df['temperatura_media'] = df.groupby('zona')['temperatura_media'].transform(lambda x: x.fillna(x.mean()))
df = df.bfill()

# ==================== FEATURES FINALES ====================
features_num = [
    'dia', 'mes', 'dia_semana', 
    'consultas_lag_1', 'consultas_lag_7', 'consultas_lag_14',
    'consultas_ma7', 'consultas_ma14',
    'es_fin_de_semana', 'es_feriado', 'es_vacaciones', 'es_no_laboral',
    'temperatura_media'
]

print(f"✅ Features: {len(features_num)} (Feriados y Findes optimizados)")

# ==================== 3. VALIDACIÓN ====================
X = df[features_num + ['zona']]
y = df['consultas'].values

tscv = TimeSeriesSplit(n_splits=5)  # Más splits
maes = []
for train_idx, val_idx in tscv.split(X):
    pipe = Pipeline([
        ('preprocessor', ColumnTransformer([
            ('num', SimpleImputer(strategy='median'), features_num),
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['zona'])
        ])),
        ('model', RandomForestRegressor(
            n_estimators=200, 
            max_depth=10, 
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        ))
    ])
    pipe.fit(X.iloc[train_idx], y[train_idx])
    maes.append(mean_absolute_error(y[val_idx], pipe.predict(X.iloc[val_idx])))

print(f"📈 MAE Validación (CV): {np.mean(maes):.1f} ± {np.std(maes):.1f}")

# ==================== BACKTESTING (Últimos 30 días) ====================
print("\n📊 Backtesting (últimos 30 días)...")
n_test = 30
X_train = X.iloc[:-n_test]
y_train = y[:-n_test]
X_test = X.iloc[-n_test:]
y_test = y[-n_test:]

modelo_final = Pipeline([
    ('preprocessor', ColumnTransformer([
        ('num', SimpleImputer(strategy='median'), features_num),
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['zona'])
    ])),
    ('model', RandomForestRegressor(
        n_estimators=200, 
        max_depth=10, 
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    ))
])

modelo_final.fit(X_train, y_train)
y_pred = modelo_final.predict(X_test)
mae_bt = mean_absolute_error(y_test, y_pred)

print(f"📉 MAE Backtesting: {mae_bt:.1f} consultas")

comparacion = pd.DataFrame({
    'fecha': df['fecha'].iloc[-n_test:].values,
    'zona': df['zona'].iloc[-n_test:].values,
    'real': y_test,
    'predicho': y_pred.round(0),
    'es_fin_de_semana': df['es_fin_de_semana'].iloc[-n_test:].values,
    'es_feriado': df['es_feriado'].iloc[-n_test:].values,
    'es_vacaciones': df['es_vacaciones'].iloc[-n_test:].values
})

print("\nÚltimos 15 registros (con info feriados/findes):")
print(comparacion.tail(15))