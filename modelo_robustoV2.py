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

print("🚀 VigiSalud - Modelo Robusto v2.1")

# ==================== CONFIG ====================
SUPABASE_URL = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/consultas_historicas"
API_KEY = "TU_API_KEY"

headers = {"apikey": API_KEY, "Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

COORDENADAS = {"Norte": (-38.95, -68.06), "Centro": (-38.95, -68.06), "Sur": (-39.10, -67.80)}

# ==================== FUNCIONES CLIMA (mismo que antes) ====================
def get_historical_weather(lat, lon, start_date, end_date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {"latitude": lat, "longitude": lon, "start_date": start_date, "end_date": end_date,
              "daily": "temperature_2m_mean", "timezone": "America/Argentina/Buenos_Aires"}
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
    params = {"latitude": lat, "longitude": lon, "daily": "temperature_2m_mean",
              "timezone": "America/Argentina/Buenos_Aires", "forecast_days": days}
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

# ==================== 3. MODELO ====================
features_num = ['dia', 'mes', 'dia_semana', 'consultas_lag_1', 'consultas_lag_7',
                'consultas_lag_14', 'consultas_ma7', 'es_feriado', 'temperatura_media']

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

# Modelo final
modelo = Pipeline([
    ('preprocessor', ColumnTransformer([
        ('num', SimpleImputer(strategy='median'), features_num),
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['zona'])
    ])),
    ('model', RandomForestRegressor(n_estimators=120, max_depth=8, random_state=42))
])
modelo.fit(X, y)

# Feature Importance
fi = pd.DataFrame({
    'feature': features_num + list(modelo.named_steps['preprocessor'].named_transformers_['cat'].get_feature_names_out()),
    'importance': modelo.named_steps['model'].feature_importances_
})
print("\n🔝 Feature Importance Top 10:")
print(fi.sort_values('importance', ascending=False).head(12))

# ==================== 4. PREDICCIONES ====================
print("\n" + "="*75)
print("📅 PREDICCIONES PRÓXIMOS 14 DÍAS")
print("="*75)

ultimo_dia = int(df['dia'].max())
fecha_min = df['fecha'].min()
zonas = sorted(df['zona'].unique())

forecast_clima = {zona: get_forecast_weather(*COORDENADAS[zona]) for zona in zonas if zona in COORDENADAS}

for offset in range(1, 15):
    fecha_pred = fecha_min + timedelta(days=ultimo_dia + offset)
    print(f"\n📍 {fecha_pred.strftime('%Y-%m-%d')} ({fecha_pred.strftime('%A')})")

    for zona in zonas:
        df_zona = df[df['zona'] == zona].tail(20)
        temp_pred = 15.0
        if zona in forecast_clima:
            fc = forecast_clima[zona]
            match = fc[fc['fecha'].dt.date == fecha_pred.date()]
            if not match.empty:
                temp_pred = float(match['temperatura_media'].iloc[0])

        X_pred = pd.DataFrame([{
            'dia': ultimo_dia + offset,
            'mes': fecha_pred.month,
            'dia_semana': fecha_pred.weekday(),
            'consultas_lag_1': float(df_zona['consultas'].iloc[-1]),
            'consultas_lag_7': float(df_zona['consultas'].iloc[-7] if len(df_zona)>=7 else 100),
            'consultas_lag_14': float(df_zona['consultas'].iloc[-14] if len(df_zona)>=14 else 100),
            'consultas_ma7': float(df_zona['consultas'].tail(7).mean()),
            'es_feriado': 0,
            'temperatura_media': temp_pred,
            'zona': zona
        }])

        pred = int(round(modelo.predict(X_pred)[0]))
        print(f"   → {zona:8} : {pred:3d} consultas   (Temp: {temp_pred:.1f}°C)")

print("\n🎉 ¡Modelo Robusto completado exitosamente!")
