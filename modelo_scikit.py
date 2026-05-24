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

# 2. Preparar datos
fechas_str = [d["fecha"] for d in datos]
consultas = [d["consultas"] for d in datos]
zonas = [d["zona"] for d in datos]

fechas = [datetime.strptime(f, "%Y-%m-%d") for f in fechas_str]
fecha_min = min(fechas)
dias = [(f - fecha_min).days for f in fechas]
meses = [f.month for f in fechas]

X = np.array([[dias[i], meses[i], zonas[i]] for i in range(len(datos))], dtype=object)
y = np.array(consultas)

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

# 5. Predecir proximos 14 dias
predicciones = []
ultimo_dia = max(dias)
zonas_unicas = list(set(zonas))

for offset in range(1, 15):
    dia_pred = ultimo_dia + offset
    fecha_pred = fecha_min + timedelta(days=int(dia_pred))
    mes_pred = fecha_pred.month
    
    for zona in zonas_unicas:
        X_pred = np.array([[dia_pred, mes_pred, zona]], dtype=object)
        consultas_pred = int(modelo.predict(X_pred)[0])
        
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
