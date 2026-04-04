import os
from dotenv import load_dotenv

load_dotenv()

LOGIN = int(os.getenv("MT5_LOGIN", 0))
PASSWORD = os.getenv("MT5_PASSWORD", "")
SERVER = os.getenv("MT5_SERVER", "")

SYMBOLS = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'BTCUSD']
MAGIC_NUMBER = 2026
DEFAULT_REFRESH = 60  # segundos

# ── Timezone local ───────────────────────────────────────────────────────────
# Cambia LOCAL_UTC_OFFSET para adaptar el sistema a tu país.
# Ejemplos:
#   Colombia / Ecuador / Perú : -5
#   México (Centro)           : -6
#   Argentina / Chile         : -3
#   España (invierno)         : +1   España (verano): +2
#   Estados Unidos ET         : -5   (invierno) / -4 (verano)
LOCAL_UTC_OFFSET = -5          # offset entero respecto a UTC
LOCAL_TZ_NAME    = "Colombia"  # nombre que aparece en pantalla

# ── Broker timezone ─────────────────────────────────────────────────────────
# Offset UTC del servidor del broker (la mayoría usa UTC+2 o UTC+3).
BROKER_UTC_OFFSET = 2

# ── Safety gates (motor de decisión) ────────────────────────────────────────
AUTONOMOUS_CONFIDENCE_THRESHOLD = 0.85  # confianza mínima para ejecución auto
MAX_SPREAD_POINTS = 30                   # puntos; bloquea si spread > este valor
MAX_DAILY_LOSS_PCT = 3.0                 # % máximo de pérdida diaria sobre balance
MAX_POSITIONS_PER_SYMBOL = 1             # posiciones simultáneas por símbolo
ORDER_DEVIATION = 20                     # slippage máximo aceptado (puntos)

# ── Control de llamadas a la IA ──────────────────────────────────────────────
AI_MIN_INTERVAL_MINS = 5    # minutos mínimos entre análisis (configurable en sidebar)
AI_STALE_MINS        = 15   # minutos tras los cuales el análisis se considera obsoleto

# ── News Shield ──────────────────────────────────────────────────────────────
NEWS_SHIELD_MINUTES   = 60    # bloquear si hay noticia high-impact en los próximos N min
NEWS_CACHE_TTL        = 1800  # segundos que se cachean los datos de noticias (30 min)
NEWS_SENTIMENT_CACHE  = 1800  # segundos para cachear sentimiento (30 min)

# Monedas que componen cada símbolo (para filtrar noticias relevantes)
SYMBOL_CURRENCIES = {
    "EURUSD": ["EUR", "USD"],
    "GBPUSD": ["GBP", "USD"],
    "USDJPY": ["USD", "JPY"],
    "XAUUSD": ["USD"],          # Oro cotiza en USD
    "BTCUSD": ["USD"],          # Bitcoin cotiza en USD
    "GBPJPY": ["GBP", "JPY"],
    "AUDUSD": ["AUD", "USD"],
    "USDCAD": ["USD", "CAD"],
    "USDCHF": ["USD", "CHF"],
    "NZDUSD": ["NZD", "USD"],
}
