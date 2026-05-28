# coding: utf-8
import requests
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error

print("🚀 VigiSalud - Modelo Ligero v2.7 | Optimizado Termux + Tabla Clara")

# ==================== CONFIG ====================
SUPABASE_URL = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/consultas_historicas"
API_KEY = "TU_API_KEY"

headers = {"apikey": API_KEY, "Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
COORDENADAS = {"Norte": (-38.95, -68.06), "Centro": (-38.95, -68.06), "Sur": (-39.10, -67.80)}

# ==================== FERIADOS 2026 ====================
feriados_nacionales = [
    "2026-01-01", "2026-02-16", "2026-02-17", "2026-03-23", "2026-03-24", "2026-04-02", "2026-04-03",
    "2026-05-01", "2026-05-25", "2026-06-17", "2026-06-20", "2026-07-09", "2026-08-17", "2026-10-12",
    "2026-11-23", "2026-12-08", "2026-12-25"
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
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        df_clima = pd.DataFrame({'fecha': data['daily']['time'], 'temperatura_media': data['daily']['temperature_2m_mean']})
        df_clima['fecha'] = pd.to_datetime(df_clima['fecha'])
        return df_clima
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
for zona in df['zona'].unique():
    if zona in COORDENADAS:
        lat, lon = COORDENADAS[zona]
        clima = get_historical_weather(lat, lon, df['fecha'].min().strftime("%Y-%m-%d"), df['fecha'].max().strftime("%Y-%m-%d"))
        if not clima.empty:
            clima['zona'] = zona
            df = df.merge(clima, on=['fecha', 'zona'], how='left')

df['temperatura_media'] = df.groupby('zona')['temperatura_media'].transform(lambda x: x.fillna(x.mean()))
df = df.bfill()

# ==================== FEATURES ====================
features_num = [
    'dia_desde_inicio', 'mes', 'dia_semana', 'mes_sin', 'dia_semana_sin',
    'consultas_lag_1', 'consultas_lag_7', 'consultas_lag_14',
    'consultas_ma7',
    'es_fin_de_semana', 'es_feriado', 'es_vacaciones', 'es_no_laboral',
    'temperatura_media'
]

print(f"✅ Features: {len(features_num)}")

# ==================== MODELADO ====================
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
        ('model', RandomForestRegressor(
            n_estimators=80, max_depth=7, min_samples_leaf=2,
            random_state=42, n_jobs=1
        ))
    ])
    pipe.fit(X.iloc[train_idx], y[train_idx])
    maes.append(mean_absolute_error(y[val_idx], pipe.predict(X.iloc[val_idx])))

print(f"📈 MAE Validación: {np.mean(maes):.1f} ± {np.std(maes):.1f}")

# ==================== BACKTESTING ====================
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
        n_estimators=80, max_depth=7, min_samples_leaf=2,
        random_state=42, n_jobs=1
    ))
])

modelo_final.fit(X_train, y_train)
y_pred = modelo_final.predict(X_test)
mae_bt = mean_absolute_error(y_test, y_pred)

print(f"📉 MAE Backtesting: {mae_bt:.1f} consultas\n")

# ==================== TABLA LIMPIA ====================
comparacion = pd.DataFrame({
    'fecha': df['fecha'].iloc[-n_test:].dt.strftime('%Y-%m-%d'),
    'zona': df['zona'].iloc[-n_test:],
    'real': y_test,
    'predicho': y_pred.round(0).astype(int),
    'no_laboral': df['es_no_laboral'].iloc[-n_test:],
    'feriado': df['es_feriado'].iloc[-n_test:],
    'fin_de_semana': df['es_fin_de_semana'].iloc[-n_test:]
})

print("Últimos 15 días (Backtesting):")
print(comparacion.tail(15).to_string(index=False))