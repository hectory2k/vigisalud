import requests
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("SUPABASE_KEY")

# Cargar datos
url = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/consultas_historicas?select=*&order=fecha.asc"
headers = {"apikey": api_key, "Authorization": f"Bearer {api_key}"}

response = requests.get(url, headers=headers)

# --- Validación de la respuesta ---
if response.status_code != 200:
    raise ConnectionError(f"Error al conectar con Supabase: {response.status_code} - {response.text}")

data = response.json()

if not data:
    raise ValueError("La API devolvió una lista vacía. Verifica la tabla y los permisos en Supabase.")

df = pd.json_normalize(data)

print(f"✅ Datos cargados: {df.shape[0]} filas, columnas: {list(df.columns)}")

# --- Verificar que existe la columna 'fecha' ---
if 'fecha' not in df.columns:
    raise KeyError(
        f"La columna 'fecha' no existe. Columnas disponibles: {list(df.columns)}\n"
        "Revisa el nombre exacto del campo en tu tabla de Supabase."
    )

df['fecha'] = pd.to_datetime(df['fecha'])
df = df[df['fecha'] >= '2023-01-01'].copy()

if df.empty:
    raise ValueError("No hay datos desde 2023-01-01. Ajusta el filtro de fecha.")

# --- Feature engineering ---
fecha_min = df['fecha'].min()
df['dia'] = (df['fecha'] - fecha_min).dt.days
df['mes'] = df['fecha'].dt.month
df['dia_semana'] = df['fecha'].dt.weekday

for lag in [1, 7, 14]:
    df[f'lag_{lag}'] = df.groupby('zona')['consultas'].shift(lag)
df['ma7'] = df.groupby('zona')['consultas'].transform(
    lambda x: x.rolling(7, min_periods=3).mean()
)
df = df.bfill()

# Features y target
features = ['dia', 'mes', 'dia_semana', 'lag_1', 'lag_7', 'lag_14', 'ma7']
X = pd.get_dummies(df[features + ['zona']], columns=['zona'])
y = df['consultas']

# Validación temporal
tscv = TimeSeriesSplit(n_splits=3)

# Ridge
ridge = Pipeline([('scaler', StandardScaler()), ('model', Ridge(alpha=1.0))])
mae_ridge = []
for train, val in tscv.split(X):
    ridge.fit(X.iloc[train], y.iloc[train])
    mae_ridge.append(mean_absolute_error(y.iloc[val], ridge.predict(X.iloc[val])))
print(f"📈 Ridge MAE: {np.mean(mae_ridge):.1f}")

# Random Forest
rf = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
mae_rf = []
for train, val in tscv.split(X):
    rf.fit(X.iloc[train], y.iloc[train])
    mae_rf.append(mean_absolute_error(y.iloc[val], rf.predict(X.iloc[val])))
print(f"🌲 Random Forest MAE: {np.mean(mae_rf):.1f}")

# Coeficientes de Ridge (interpretabilidad)
ridge.fit(X, y)
coefs = pd.DataFrame({'feature': X.columns, 'coef': ridge.named_steps['model'].coef_})
coefs['abs'] = coefs['coef'].abs()
print("\n🔝 Features más importantes (Ridge):")
print(coefs.sort_values('abs', ascending=False).head(10))

# Features con coeficiente cercano a 0
bajas = coefs[coefs['abs'] < 0.5]
if len(bajas) > 0:
    print(f"\n🪶 Features con poco peso (coef < 0.5): {len(bajas)}")
    print(bajas[['feature', 'coef']])
    