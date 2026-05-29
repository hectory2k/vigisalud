import os
from dotenv import load_dotenv
load_dotenv()

# Supabase
SUPABASE_URL = "https://qlbczflygozfvwyilhes.supabase.co/rest/v1/consultas_historicas"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# APIs externas
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY")

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Coordenadas
COORDENADAS = {
    "Norte": (-38.95, -68.06),
    "Centro": (-38.95, -68.06),
    "Sur": (-39.10, -67.80)
}

# Feriados 2026
FERIADOS_NACIONALES = [
    "2026-01-01","2026-02-16","2026-02-17","2026-03-23","2026-03-24",
    "2026-04-02","2026-04-03","2026-05-01","2026-05-25","2026-06-17",
    "2026-06-20","2026-07-09","2026-08-17","2026-10-12","2026-11-23",
    "2026-12-08","2026-12-25"
]

# Umbrales por zona
UMBRALES = {"Norte": 130, "Centro": 110, "Sur": 90}

# Features del modelo
FEATURES_NUM = [
    'dia_desde_inicio', 'mes', 'dia_semana', 'mes_sin', 'dia_semana_sin',
    'consultas_lag_1', 'consultas_lag_7', 'consultas_lag_14', 'consultas_ma7',
    'es_fin_de_semana', 'es_feriado', 'es_vacaciones', 'es_no_laboral'
]

# Hiperparámetros
HIPERPARAMETROS = {
    'n_estimators': 100,
    'max_depth': 8,
    'min_samples_leaf': 2,
    'random_state': 42,
    'n_jobs': 1
}

