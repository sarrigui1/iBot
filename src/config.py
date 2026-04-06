"""
Configuration Module — Exporta constantes globales para la aplicación

Este módulo carga la configuración de config.ini a través de ConfigLoader
y exporta constantes en mayúsculas para que app.py pueda utilizarlas.
"""

import os
from core.config_loader import ConfigLoader

# Calcular ruta absoluta a config.ini
# El archivo config.ini está en: raiz/config/config.ini
# Este archivo está en: raiz/src/config.py
_src_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_src_dir)
_config_ini_path = os.path.join(_project_root, 'config', 'config.ini')

# Cargar configuración una sola vez
_config = ConfigLoader(_config_ini_path)

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTES EXPORTADAS — Derivadas de config.ini
# ═══════════════════════════════════════════════════════════════════════════════

# Símbolos de trading
SYMBOLS = _config.symbols

# Mapeo de símbolos a divisas para análisis de noticias
# Derivado automáticamente de SYMBOLS (asume formato XXX[YYY] donde YYY es la divisa objetivo)
SYMBOL_CURRENCIES = {
    "EURUSD": ["EUR", "USD"],
    "GBPUSD": ["GBP", "USD"],
    "USDJPY": ["USD", "JPY"],
    "XAUUSD": ["XAU", "USD"],
    "BTCUSD": ["BTC", "USD"],
}

# Parámetros de trading
AUTONOMOUS_CONFIDENCE_THRESHOLD = _config.autonomous_confidence_threshold
MAX_SPREAD_POINTS = _config.max_spread_points
MAX_DAILY_LOSS_PCT = _config.max_daily_loss_pct
MAX_POSITIONS_PER_SYMBOL = _config.max_positions_per_symbol

# Zona horaria
LOCAL_UTC_OFFSET = _config.local_utc_offset
LOCAL_TZ_NAME = _config.local_tz_name
BROKER_UTC_OFFSET = _config.broker_utc_offset

# Timings
AI_MIN_INTERVAL_MINS = _config.ai_min_interval_mins
NEWS_SHIELD_MINUTES = _config.news_shield_minutes
NEWS_CACHE_TTL = _config.news_cache_ttl

# Parámetros de MT5
# Número mágico único para identificar órdenes de esta aplicación
MAGIC_NUMBER = 12345
# Desviación máxima permitida en el precio de ejecución (en pips)
ORDER_DEVIATION = 20

# Constantes adicionales de UI
# Máximo tiempo (en minutos) antes de considerar que el análisis AI está obsoleto
AI_STALE_MINS = 30

# Cache de sentimiento de noticias (en segundos)
# Valor por defecto: 900 segundos (15 minutos)
NEWS_SENTIMENT_CACHE = 900


def __repr__() -> str:
    """Representación útil para debugging."""
    return (
        f"<ConfigModule "
        f"symbols={len(SYMBOLS)} "
        f"confidence_threshold={AUTONOMOUS_CONFIDENCE_THRESHOLD} "
        f"max_daily_loss={MAX_DAILY_LOSS_PCT}%>"
    )
