import requests
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error

url = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/consultas_historicas"
api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFsYmN6Zmx5Z296ZnZ3eWlsaGVzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5NDM0NTAsImV4cCI6MjA5NDUxOTQ1MH0.EiNp2HRocIqW4yStNxBoHgDN-EfFZvPv_Uc5ETo0wYg"

headers = {
    "apikey": api_key,
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 1. Leer datos
response = requests.get(url + "?select=*&order=fecha.asc", headers=headers)
datos = response.json()
print(f"Datos leidos: {len(datos)} registros")

# 2. Preparar datos con pandas
import pandas as pd

fechas_str = [d["fecha"] for d in datos]
consultas = [d["consultas"] for d in datos]
zonas = [d["zona"] for d in datos]

fechas = [datetime.strptime(f, "%Y-%m-%d") for f in fechas_str]
fecha_min = min(fechas)

df = pd.DataFrame({
    'fecha': fechas,
    'zona': zonas,
    'consultas': consultas
})

df['dia'] = [(f - fecha_min).days for f in fechas]
df['mes'] = [f.month for f in fechas]
df['dia_semana'] = [f.weekday() for f in fechas]

# Ordenar para lags
df = df.sort_values(['zona', 'fecha'])

# Lag features
for lag in [1, 7, 14]:
    df[f'consultas_lag_{lag}'] = df.groupby('zona')['consultas'].shift(lag)

# Media móvil 7 días
df['consultas_ma7'] = df.groupby('zona')['consultas'].transform(
    lambda x: x.rolling(7, min_periods=1).mean()
)

# Rellenar NaNs
df = df.bfill()

print(f"Features creadas: dia, mes, dia_semana, lag_1, lag_7, lag_14, ma7")

# Preparar X e y
features_num = ['dia', 'mes', 'dia_semana', 'consultas_lag_1', 'consultas_lag_7', 'consultas_lag_14', 'consultas_ma7']
X = df[features_num + ['zona']].values
y = df['consultas'].values

# 3. Validacion temporal (TimeSeriesSplit)
if len(X) >= 10:
    tscv = TimeSeriesSplit(n_splits=3)
    maes = []
    rmses = []
    
    for train_idx, val_idx in tscv.split(X):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', SimpleImputer(strategy='median'), [0, 1]),
                ('cat', OneHotEncoder(handle_unknown='ignore'), [2])
            ]
        )
        
        modelo_val = Pipeline([
            ('preprocessor', preprocessor),
            ('model', RandomForestRegressor(n_estimators=10, random_state=42))
        ])
        
        modelo_val.fit(X_train, y_train)
        y_pred = modelo_val.predict(X_val)
        
        maes.append(mean_absolute_error(y_val, y_pred))
        rmses.append(np.sqrt(mean_squared_error(y_val, y_pred)))
    
    mae_promedio = np.mean(maes)
    rmse_promedio = np.mean(rmses)
    print(f"📊 Validacion temporal - MAE: {mae_promedio:.2f} | RMSE: {rmse_promedio:.2f}")
else:
    mae_promedio = 0
    rmse_promedio = 0
    print("⚠️ Pocos datos para validacion temporal")

# 4. Entrenar modelo final con todos los datos
preprocessor = ColumnTransformer(
    transformers=[
        ('num', SimpleImputer(strategy='median'), [0, 1]),
        ('cat', OneHotEncoder(handle_unknown='ignore'), [2])
    ]
)

modelo = Pipeline([
    ('preprocessor', preprocessor),
    ('model', RandomForestRegressor(n_estimators=10, random_state=42))
])

modelo.fit(X, y)
print("✅ Modelo final entrenado con todos los datos")

# Feature Importance
importances = modelo.named_steps['model'].feature_importances_
cat_features = modelo.named_steps['preprocessor'].named_transformers_['cat'].get_feature_names_out(['zona'])
feature_names = features_num + list(cat_features)

print("\n🔝 Feature Importance:")
for name, imp in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True):
    print(f"  {name}: {imp:.4f}")

# 5. Predecir proximos 14 dias

predicciones = []
ultimo_dia = max(df['dia'].values)
zonas_unicas = df['zona'].unique().tolist()

for offset in range(1, 15):
    dia_pred = ultimo_dia + offset
    fecha_pred = fecha_min + timedelta(days=int(dia_pred))
    mes_pred = fecha_pred.month
    dia_semana_pred = fecha_pred.weekday()
    
    for zona in zonas_unicas:
        # Agarrar el último valor conocido de cada lag para esta zona
        df_zona = df[df['zona'] == zona].tail(14)
        
        if len(df_zona) > 0:
            lag_1_val = df_zona['consultas'].values[-1]
            lag_7_val = df_zona['consultas'].values[-min(7, len(df_zona))]
            lag_14_val = df_zona['consultas'].values[-min(14, len(df_zona))]
            ma7_val = df_zona['consultas'].values[-7:].mean() if len(df_zona) >= 7 else df_zona['consultas'].mean()
        else:
            lag_1_val = lag_7_val = lag_14_val = ma7_val = 100
        
        X_pred = np.array([[dia_pred, mes_pred, dia_semana_pred, lag_1_val, lag_7_val, lag_14_val, ma7_val, zona]], dtype=object)
        consultas_pred = int(modelo.predict(X_pred)[0])
        
        predicciones.append({
            "fecha": fecha_pred.strftime("%Y-%m-%d"),
            "zona": zona,
            "consultas_predichas": max(0, consultas_pred)
        })
        print(f"Zona {zona} | {fecha_pred.strftime('%Y-%m-%d')} | {max(0, consultas_pred)} consultas")


        predicciones.append({
            "fecha": fecha_pred.strftime("%Y-%m-%d"),
            "zona": zona,
            "consultas_predichas": max(0, consultas_pred)
        })
        print(f"Zona {zona} | {fecha_pred.strftime('%Y-%m-%d')} | {max(0, consultas_pred)} consultas")

# 6. Guardar predicciones
url_pred = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/predicciones"
headers_pred = {
    "apikey": api_key,
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

requests.delete(url_pred + "?id=gt.0", headers=headers_pred)
for pred in predicciones:
    requests.post(url_pred, headers=headers_pred, json=pred)

print(f"✅ {len(predicciones)} predicciones guardadas")

# 7. Guardar metricas en tabla de logs
url_logs = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/logs_metricas"
requests.post(url_logs, headers=headers_pred, json={
    "fecha_ejecucion": datetime.now().strftime("%Y-%m-%d"),
    "mae": round(mae_promedio, 2),
    "rmse": round(rmse_promedio, 2),
    "n_registros": len(datos)
})
print(f"📊 Metricas guardadas en logs_metricas")
