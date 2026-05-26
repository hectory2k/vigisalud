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

print("🚀 VigiSalud - Modelo Robusto v2 + Backtesting")

# ==================== CONFIG ====================
SUPABASE_URL = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/consultas_historicas"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsYmN6Zmx5Z296ZnZ3eWlsaGVzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5NDM0NTAsImV4cCI6MjA5NDUxOTQ1MH0.EiNp2HRocIqW4yStNxBoHgDN-EfFZvPv_Uc5ETo0wYg"

headers = {"apikey": API_KEY, "Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
COORDENADAS = {"Norte": (-38.95, -68.06), "Centro": (-38.95, -68.06), "Sur": (-39.10, -67.80)}

# ==================== FUNCIONES CLIMA ====================
def get_historical_weather(lat, lon, start_date, end_date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {"latitude": lat, "longitude": lon, "start_date": start_date, "end_date": end_date, "daily": "temperature_2m_mean", "timezone": "America/Argentina/Buenos_Aires"}
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        df_clima = pd.DataFrame({'fecha': data['daily']['time'], 'temperatura_media': data['daily']['temperature_2m_mean']})
        df_clima['fecha'] = pd.to_datetime(df_clima['fecha'])
        return df_clima
    except:
        return pd.DataFrame()

def get_forecast_weather(lat, lon, days=14):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": lat, "longitude": lon, "daily": "temperature_2m_mean", "timezone": "America/Argentina/Buenos_Aires", "forecast_days": days}
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        df_clima = pd.DataFrame({'fecha': data['daily']['time'], 'temperatura_media': data['daily']['temperature_2m_mean']})
        df_clima['fecha'] = pd.to_datetime(df_clima['fecha'])
        return df_clima
    except:
        return pd.DataFrame()

# ==================== 1. CARGAR DATOS ====================
response = requests.get(SUPABASE_URL + "?select=*&order=fecha.asc", headers=headers)
df = pd.DataFrame(response.json())
df['fecha'] = pd.to_datetime(df['fecha'])
print(f"📊 Datos: {len(df)} registros | {df['fecha'].min().date()} → {df['fecha'].max().date()}")

# ==================== 2. FEATURE ENGINEERING ====================
fecha_min = df['fecha'].min()
df = df.sort_values(['zona', 'fecha']).reset_index(drop=True)
df['dia'] = (df['fecha'] - fecha_min).dt.days
df['mes'] = df['fecha'].dt.month
df['dia_semana'] = df['fecha'].dt.weekday
df['es_fin_de_semana'] = df['dia_semana'].apply(lambda x: 1 if x >= 5 else 0)

for lag in [1, 7, 14]:
    df[f'consultas_lag_{lag}'] = df.groupby('zona')['consultas'].shift(lag)
df['consultas_ma7'] = df.groupby('zona')['consultas'].transform(lambda x: x.rolling(7, min_periods=3).mean())

# Feriados
feriados_2026 = {5: [1, 25], 6: [20], 7: [9]}
df['es_feriado'] = 0
for mes, dias in feriados_2026.items():
    for dia in dias:
        mask = (df['fecha'].dt.month == mes) & (df['fecha'].dt.day == dia)
        df.loc[mask, 'es_feriado'] = 1

# Temperatura
print("🌡️ Obteniendo temperatura...")
for zona in df['zona'].unique():
    if zona in COORDENADAS:
        lat, lon = COORDENADAS[zona]
        clima = get_historical_weather(lat, lon, df['fecha'].min().strftime("%Y-%m-%d"), df['fecha'].max().strftime("%Y-%m-%d"))
        if not clima.empty:
            clima['zona'] = zona
            df = df.merge(clima, on=['fecha', 'zona'], how='left')

df['temperatura_media'] = df.groupby('zona')['temperatura_media'].transform(lambda x: x.fillna(x.mean()))
df = df.bfill()

features_num = ['dia', 'mes', 'dia_semana', 'consultas_lag_1', 'consultas_lag_7', 'consultas_lag_14', 'consultas_ma7', 'es_feriado', 'temperatura_media', 'es_fin_de_semana']
print(f"✅ Features: {len(features_num)}")

# ==================== 3. VALIDACIÓN ====================
X = df[features_num + ['zona']]
y = df['consultas'].values

tscv = TimeSeriesSplit(n_splits=4)
maes = []
for train_idx, val_idx in tscv.split(X):
    pipe = Pipeline([
        ('preprocessor', ColumnTransformer([
            ('num', SimpleImputer(strategy='median'), features_num),
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['zona'])
        ])),
        ('model', RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42))
    ])
    pipe.fit(X.iloc[train_idx], y[train_idx])
    maes.append(mean_absolute_error(y[val_idx], pipe.predict(X.iloc[val_idx])))
print(f"📈 MAE Validación: {np.mean(maes):.1f}")

# ==================== BACKTESTING (Últimos 30 días) ====================
print("\n📊 Backtesting (últimos 30 días)...")
n_test = 30
X_train = X.iloc[:-n_test]
y_train = y[:-n_test]
X_test = X.iloc[-n_test:]
y_test = y[-n_test:]

modelo_bt = Pipeline([
    ('preprocessor', ColumnTransformer([
        ('num', SimpleImputer(strategy='median'), features_num),
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['zona'])
    ])),
    ('model', RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42))
])
modelo_bt.fit(X_train, y_train)
y_pred = modelo_bt.predict(X_test)
mae_bt = mean_absolute_error(y_test, y_pred)
print(f"📉 MAE Backtesting: {mae_bt:.1f} consultas")

comparacion = pd.DataFrame({
    'fecha': df['fecha'].iloc[-n_test:].values,
    'zona': df['zona'].iloc[-n_test:].values,
    'real': y_test,
    'predicho': y_pred.round(0)
})
print("\nÚltimos 5 comparaciones:")
print(comparacion.tail(15))
