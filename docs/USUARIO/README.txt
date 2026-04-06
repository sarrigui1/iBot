==============================================================================
iBot · Intelligence Trading — Guía de Inicio Rápido
==============================================================================

Versión: 1.0
Fecha: Abril 2026
Modelo: Smart Money Concepts (SMC) + Claude Haiku AI

==============================================================================
REQUISITOS PREVIOS
==============================================================================

1. MetaTrader 5 instalado y cuenta activa
2. Python 3.9+ (si ejecutas desde source)
3. Conexión a Internet (para validación de licencia y Claude API)

==============================================================================
CONFIGURACIÓN INICIAL
==============================================================================

1. Abre el archivo: config.ini

2. Completa los siguientes campos:

   [LICENSE]
   LICENSE_KEY = tu_license_key_aqui

   [MT5_ACCOUNT]
   MT5_LOGIN = 123456789
   MT5_PASSWORD = tu_password_aqui
   MT5_SERVER = tu_broker_server_aqui

3. OPCIONAL: Personaliza los parámetros de trading:

   [TRADING_PARAMETERS]
   AUTONOMOUS_CONFIDENCE_THRESHOLD = 0.85 (85% confianza mínima)
   MAX_DAILY_LOSS_PCT = 3.0 (límite diario de pérdidas)
   MAX_SPREAD_POINTS = 30 (spread máximo aceptado)

4. Verifica tu zona horaria:

   [TIMEZONE]
   LOCAL_UTC_OFFSET = -5 (Colombia: UTC-5)
   LOCAL_TZ_NAME = Colombia

==============================================================================
EJECUCIÓN
==============================================================================

Opción A: Ejecutable (Recomendado)
  1. Haz doble clic en: ibot.exe
  2. Se abrirá automáticamente en tu navegador (http://localhost:8501)
  3. Espera a que cargue el dashboard

Opción B: Desde Python (Si tienes el source)
  1. Abre una terminal/CMD en esta carpeta
  2. Ejecuta: streamlit run app.py
  3. Se abrirá en tu navegador

==============================================================================
PRIMER USO
==============================================================================

1. El bot validará tu licencia contra nuestro servidor
2. Si no hay internet, usará el caché local (máx 7 días)
3. Verifica que MetaTrader 5 esté conectado (indicador en sidebar)
4. Selecciona un par de divisas para analizar
5. Haz clic en "Analizar con Claude" para obtener un veredicto
6. El bot mostrará análisis técnico, SMC y recomendación de IA

==============================================================================
MODOS DE OPERACIÓN
==============================================================================

👤 MODO MANUAL
  - Tú ejecutas cada trade manualmente
  - El bot solo sugiere, no ejecuta órdenes
  - Control total en tus manos

🤖 MODO AUTÓNOMO
  - El bot ejecuta órdenes automáticamente
  - Solo si confidence >= 85% (configurable)
  - Valida 6 safety gates antes de ejecutar
  - ⚠️ Usa con cuidado

==============================================================================
SAFETY GATES (Protecciones)
==============================================================================

Antes de ejecutar cualquier orden, el bot verifica:

1. NEWS SHIELD — ¿Hay un evento económico alto impacto en 60 min?
2. SPREAD FILTER — ¿El spread está dentro del máximo permitido?
3. DAILY LOSS — ¿Pérdidas hoy < 3% del balance?
4. NO DUPLICADOS — ¿Ya no hay posición abierta en ese símbolo?
5. STOP LOSS — ¿El SL es válido y > 0?
6. CONFIANZA — ¿La IA está ≥85% segura?

Si CUALQUIERA falla → la orden se rechaza automáticamente

==============================================================================
MONITOREO DE POSICIONES
==============================================================================

- Pestaña "Dashboard" → tabla "Posiciones Abiertas"
- Cada posición tiene 3 botones:
  • ❌ CERRAR — cierra la posición inmediatamente
  • 🔄 TRAILING STOP — sigue la tendencia dinámicamente
  • ✓ BREAK EVEN — mueve SL al precio de apertura

==============================================================================
ANÁLISIS TÉCNICO
==============================================================================

El bot analiza 3 timeframes simultáneamente:

D1 (Diario)    → Macro trend, bias general
H1 (Por hora)  → Estructura técnica, zonas clave
M15 (15 min)   → Entrada precisa, confirmación

Smart Money Concepts (SMC):
  - Order Blocks (OB)
  - Fair Value Gaps (FVG)
  - Break of Structure (BOS)
  - Change of Character (CHOCH)
  - Equal Highs/Lows (EH/EL)
  - Prior Day High/Low (PDH/PDL)

==============================================================================
PESTAÑA DIARIO
==============================================================================

Journal → Historial completo de trades ejecutados

Incluye:
  - Trades cerrados (date, symbol, direction, PnL)
  - Equity curve (gráfico de balance acumulado)
  - Estadísticas: Win Rate, trades ganadores/perdedores
  - Performance por setup y por sesión (London, NY, Asia)
  - Notas de calibración (feedback del bot sobre tu estilo)

==============================================================================
TROUBLESHOOTING
==============================================================================

❌ "Licencia inválida"
  → Verifica que LICENSE_KEY en config.ini es correcta
  → Asegúrate que la licencia existe en Google Sheets
  → Verifica que active_status = TRUE y expiry_date >= hoy

❌ "No conectado a MT5"
  → Abre MetaTrader 5 manualmente
  → Verifica login, password y server en config.ini
  → Intenta reconectar usando el botón en la UI

❌ "Error de API Claude"
  → Verifica que ANTHROPIC_API_KEY esté configurada
  → Revisa tu saldo de créditos en Anthropic console
  → Intenta nuevamente en 30 segundos

❌ "No hay datos de calendario"
  → Esto es normal (feed de Forex Factory puede estar lento)
  → El bot sigue funcionando sin noticias
  → Intenta actualizar en 1 minuto

==============================================================================
COSTOS
==============================================================================

Suscripción: $99 - $999 USD/mes (según plan)

Costos operativos incluidos:
  - Claude Haiku API: ~$1.50/mes (análisis IA)
  - Forex Factory: GRATIS (calendario económico)
  - Finnhub Free: GRATIS (sentimiento)
  - MetaTrader 5: tu spread + comisión del broker

==============================================================================
SOPORTE
==============================================================================

📧 Email: soporte@ibot-trading.com
🐛 Reporta bugs: https://github.com/ibot/issues
📖 Documentación: https://docs.ibot-trading.com

==============================================================================
DISCLAIMER
==============================================================================

⚠️ RIESGO DE PÉRDIDA TOTAL

El trading con apalancamiento conlleva riesgo de pérdida total del capital.
iBot es una HERRAMIENTA DE APOYO, no garantiza ganancias.

- Prueba en DEMO ACCOUNT primero
- Usa posiciones pequeñas (0.01-0.1 lots)
- Establece límites de pérdida diaria
- No trades fuera de tus horarios esperados
- Monitorea regularmente (no confíes 100% en automatización)

El usuario asume total responsabilidad por sus trades.

==============================================================================
Última actualización: 2026-04-05
Licencia: Privada (No redistribuible)
==============================================================================
