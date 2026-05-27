# coding: utf-8
# ==================== BACKTESTING SIMPLE + FEATURE FIN DE SEMANA ====================

print("🔄 Agregando feature + Backtesting...")

# Feature nueva: Fin de semana
df['es_fin_de_semana'] = df['dia_semana'].apply(lambda x: 1 if x >= 5 else 0)

# Actualizar features
features_num = ['dia', 'mes', 'dia_semana', 'consultas_lag_1', 'consultas_lag_7',
                'consultas_lag_14', 'consultas_ma7', 'es_feriado', 
                'temperatura_media', 'es_fin_de_semana']

X = df[features_num + ['zona']]
y = df['consultas'].values

print(f"✅ Nueva feature agregada | Features total: {len(features_num)}")

# ==================== BACKTESTING (Últimos 30 días) ====================
print("\n📊 Realizando Backtesting (últimos 30 días)...")

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
print(f"📉 MAE Backtesting (últimos 30 días): {mae_bt:.1f} consultas")

# Comparación
comparacion = pd.DataFrame({
    'fecha': df['fecha'].iloc[-n_test:],
    'zona': df['zona'].iloc[-n_test:],
    'real': y_test,
    'predicho': y_pred.round(0)
})
print("\nÚltimos 5 días de backtesting:")
print(comparacion.tail(15))
