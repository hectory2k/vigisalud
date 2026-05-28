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
from sklearn.metrics import mean_absolute_error

print("🚀 VigiSalud - Modelo Final v3.5 | 7 días + Logs MAE")

# ==================== CONFIG ====================
SUPABASE_URL = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/consultas_historicas"
API_KEY = "TU_API_KEY"

headers = {
    "apikey": API_KEY,
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

COORDENADAS = {"Norte": (-38.95, -68.06), "Centro": (-38.95, -68.06), "Sur": (-39.10, -67.80)}

# ==================== FERIADOS ====================
feriados_nacionales = [
    "2026-01-01","2026-02-16","2026-02-17","2026-03-23","2026-03-24","2026-04-02","2026-04-03",
    "2026-05-01","2026-05-25","2026-06-17","2026-06-20","2026-07-09","2026-08-17","2026-10-12",
    "2026-11-23","2026-12-08","2026-12-25"
]

def es_vacaciones(fecha):
    mes = fecha.month
    dia = fecha.day
    if mes in [1, 2] or (mes == 12 and dia >= 15) or mes == 7:
        return 1
    return 0

# ==================== CLIMA ====================
def get_historical_weather(lat, lon, start_date, end_date):
    try:
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {"latitude": lat, "longitude": lon, "start_date": start_date, "end_date": end_date,
                  "daily": "temperature_2m_mean", "timezone": "America/Argentina/Buenos_Aires"}
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        return pd.DataFrame({
            'fecha': pd.to_datetime(data['daily']['time']),
            'temperatura_media': data['daily']['temperature_2m_mean']
        })
    except:
        return pd.DataFrame()

# ==================== CARGAR DATOS ====================
response = requests.get(SUPABASE_URL + "?select=*&order=fecha.asc", headers=headers)
df = pd.DataFrame(response.json())
df['fecha'] = pd.to_datetime(df['fecha'])
df = df[df['fecha'] >= '2023-01-01'].copy()

print(f"📊 Datos: {len(df)} registros | {df['fecha'].min().date()} → {df['fecha'].max().date()}")

# ==================== FEATURE ENGINEERING ====================
df = df.sort_values(['zona', 'fecha']).reset_index(drop=True)

df['dia_desde_inicio'] = (df['fecha'] - df['fecha'].min()).dt.days
df['mes'] = df['fecha'].dt.month
df['dia_semana'] = df['fecha'].dt.weekday
df['es_fin_de_semana'] = (df['dia_semana'] >= 5).astype(int)

df['es_feriado'] = df['fecha'].dt.strftime('%Y-%m-%d').isin(feriados_nacionales).astype(int)
df['es_vacaciones'] = df['fecha'].apply(es_vacaciones)
df['es_no_laboral'] = (df['es_fin_de_semana'] | df['es_feriado'] | df['es_vacaciones']).astype(int)

df['mes_sin'] = np.sin(2 * np.pi * df['mes'] / 12)
df['dia_semana_sin'] = np.sin(2 * np.pi * df['dia_semana'] / 7)

for lag in [1, 7, 14]:
    df[f'consultas_lag_{lag}'] = df.groupby('zona')['consultas'].shift(lag)

df['consultas_ma7'] = df.groupby('zona')['consultas'].transform(lambda x: x.rolling(7, min_periods=3).mean())

# Temperatura
print("🌡️ Obteniendo temperatura...")
clima_total = pd.DataFrame()
for zona in df['zona'].unique():
    if zona in COORDENADAS:
        lat, lon = COORDENADAS[zona]
        clima = get_historical_weather(lat, lon, df['fecha'].min().strftime("%Y-%m-%d"), df['fecha'].max().strftime("%Y-%m-%d"))
        if not clima.empty:
            clima['zona'] = zona
            clima_total = pd.concat([clima_total, clima])

if not clima_total.empty:
    df = df.merge(clima_total, on=['fecha', 'zona'], how='left')

df['temperatura_media'] = df.groupby('zona')['temperatura_media'].transform(lambda x: x.fillna(x.mean()))
df = df.bfill()

# ==================== MODELO ====================
features_num = ['dia_desde_inicio', 'mes', 'dia_semana', 'mes_sin', 'dia_semana_sin',
                'consultas_lag_1', 'consultas_lag_7', 'consultas_lag_14', 'consultas_ma7',
                'es_fin_de_semana', 'es_feriado', 'es_vacaciones', 'es_no_laboral', 'temperatura_media']

X = df[features_num + ['zona']]
y = df['consultas'].values

modelo = Pipeline([
    ('preprocessor', ColumnTransformer([
        ('num', SimpleImputer(strategy='median'), features_num),
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['zona'])
    ])),
    ('model', RandomForestRegressor(n_estimators=100, max_depth=8, min_samples_leaf=2, random_state=42, n_jobs=1))
])
modelo.fit(X, y)

mae_bt = mean_absolute_error(y[-30:], modelo.predict(X.iloc[-30:]))
print(f"📉 MAE Backtesting: {mae_bt:.1f} consultas\n")

# ==================== PREDICCIÓN 7 DÍAS ====================
print("🔮 Generando predicciones (próximos 7 días)...")

fecha_max = df['fecha'].max()
fechas_fut = [fecha_max + timedelta(days=i) for i in range(1, 8)]

predicciones = []

for zona in ['Norte', 'Centro', 'Sur']:
    futuro = pd.DataFrame({'fecha': fechas_fut, 'zona': zona})
    
    futuro['dia_desde_inicio'] = (futuro['fecha'] - df['fecha'].min()).dt.days
    futuro['mes'] = futuro['fecha'].dt.month
    futuro['dia_semana'] = futuro['fecha'].dt.weekday
    futuro['es_fin_de_semana'] = (futuro['dia_semana'] >= 5).astype(int)
    futuro['es_feriado'] = futuro['fecha'].dt.strftime('%Y-%m-%d').isin(feriados_nacionales).astype(int)
    futuro['es_vacaciones'] = futuro['fecha'].apply(es_vacaciones)
    futuro['es_no_laboral'] = (futuro['es_fin_de_semana'] | futuro['es_feriado'] | futuro['es_vacaciones']).astype(int)
    
    futuro['mes_sin'] = np.sin(2 * np.pi * futuro['mes'] / 12)
    futuro['dia_semana_sin'] = np.sin(2 * np.pi * futuro['dia_semana'] / 7)

    last = df[df['zona'] == zona].iloc[-1]
    for col in ['consultas_lag_1', 'consultas_lag_7', 'consultas_lag_14', 'consultas_ma7']:
        futuro[col] = last[col]
    futuro['temperatura_media'] = last.get('temperatura_media', 15.0)

    pred = modelo.predict(futuro[features_num + ['zona']])
    
    for i in range(len(fechas_fut)):
        predicciones.append({
            'fecha': fechas_fut[i].strftime('%Y-%m-%d'),
            'zona': zona,
            'consultas_predichas': int(round(pred[i]))
        })

df_pred = pd.DataFrame(predicciones)
df_pred.to_csv('predicciones_7_dias.csv', index=False)
print(f"💾 CSV guardado: {len(df_pred)} registros")

# ==================== SUBIR PREDICCIONES ====================
print("\n📤 Subiendo predicciones...")
for _, row in df_pred.iterrows():
    data = {
        'fecha': row['fecha'],
        'zona': row['zona'],
        'consultas_predichas': row['consultas_predichas']
    }
    requests.post("https://qlbczflygozfvwyilhes.supabase.co/rest/v1/predicciones", headers=headers, json=data)
    print(f"✅ {row['fecha']} | {row['zona']:8} → {row['consultas_predichas']}")

# ==================== GUARDAR MAE ====================
print("\n📊 Guardando métrica...")
log_data = {
    'fecha_ejecucion': datetime.now().strftime('%Y-%m-%d'),
    'mae': float(mae_bt),
    'n_reg': len(df)
}
requests.post("https://qlbczflygozfvwyilhes.supabase.co/rest/v1/logs_metricas", headers=headers, json=log_data)
print(f"📈 MAE del día guardado: {mae_bt:.1f}")

print("\n🎉 ¡Proceso completado correctamente!")