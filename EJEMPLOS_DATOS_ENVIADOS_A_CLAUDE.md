# Ejemplos Reales: Qué Información Recibe Claude
## Escenarios de operación en mercados reales

---

## Ejemplo 1: EURUSD en Kill Zone London (SETUP BULLISH CONFIRMADO)

### Contexto
- **Hora:** 03:45 UTC (10:45 Colombia local)
- **Sesión:** London (Kill Zone ACTIVA)
- **Condición de mercado:** Bullish, FVG recent, OB confluence
- **Tema:** Entrada en condiciones ÓPTIMAS

### Prompt enviado a Claude

```
Eres un trader institucional SMC en una prop firm Tier-1.
Tu única responsabilidad: analizar precio y emitir BUY/SELL/HOLD.

═══════════════════════════════════════════════════════════════════

INSTRUMENT: EURUSD

D1 MACRO — Trend: BULLISH | Price: 1.0832 | EMA200: 1.0754 | RSI: 58.2 | ATR: 0.0067
  Higher High @ 1.0841, Higher Low @ 1.0772 confirm uptrend.

H1 TECHNICAL — Trend: BULLISH | EMA20: 1.0818 | EMA50: 1.0795 | RSI: 54.1 | ATR: 0.0021
  Price above both EMAs, RSI not overbought.

M15 ENTRY — Momentum: BULLISH | Price: 1.0829 | EMA9: 1.0824 | RSI: 52.8 | ATR: 0.0009

═══════════════════════════════════════════════════════════════════

SMC CONTEXT (H1):
  Structure        : Bullish (HH, HL, HH)
  BOS              : BullishBOS @ 1.0815 ← swept liquidity
  CHOCH            : None
  Order Blocks     : Bullish OB 1.0802–1.0809 (very recent)
  FVG Zones        : Bullish FVG 1.0811–1.0818 (unmitigated)
  EQH (BSL)        : [1.0832, 1.0834] ← current level
  EQL (SSL)        : [1.0798, 1.0801] ← lower liquidity
  PDH/PDL          : 1.0841 / 1.0772
  PWH/PWL          : 1.0878 / 1.0701
  Session          : London (Kill Zone ACTIVE 03:00–05:00 Colombia)
  SMC Bias         : Bullish
  Setup Type       : CONFIRMED
    Reason: FVG mitigation + OB confluence + BOS + London Kill Zone

═══════════════════════════════════════════════════════════════════

ACCOUNT — Equity: $5,218.40 | Balance: $5,200.00 | Open P&L: +$18.40

SESSION CONTEXT:
  Session         : London
  In Kill Zone    : YES (current time 03:45 local, Kill Zone 03:00–05:00)
  Session Losses  : 0 (no losses in London so far)
  Spread          : 1.2 pts (very tight, excellent)
  Next Session    : NY (opens in 5 hours)

═══════════════════════════════════════════════════════════════════

DATOS FUNDAMENTALES:
  Sentiment       : BULLISH (score = +0.45, articles = 14)
  Economic Events : No high-impact events in next 60 minutes ✓
  News Shield     : INACTIVE (green — safe to trade)

═══════════════════════════════════════════════════════════════════

HISTORICAL PERFORMANCE [15 trades]:
  Total Win Rate       : 66.7% (10 winners / 5 losers)
  Average R:R Actual   : 1:1.8

  By Setup:
    CONFIRMED Setup   : 75% WR (6/8 trades) ← BEST SETUP
    AGGRESSIVE Setup  : 60% WR (3/5 trades)
    NEUTRAL Setup     : 50% WR (1/2 trades)

  By Session:
    London Session    : 72% WR (8/11 trades) ← BEST SESSION
    NY Session        : 55% WR (2/4 trades)

  By Symbol:
    EURUSD            : 70% WR (7/10 trades) ← STRONG
    XAUUSD            : 60% WR (3/5 trades)

CALIBRATION NOTES:
  → CONFIRMED setup in London = highest conviction (75% WR)
  → Increase confidence by 10–15% when both conditions met
  → Use minimum R:R 1:2.5 (not 1:2) for London trades
  → NY session underperforming — apply caution

═══════════════════════════════════════════════════════════════════

ACCOUNT RESTRICTIONS:
  • Max daily loss limit: 3% of balance = $156.00
  • Current daily loss: $0 (0%)
  • Positions open today: 0 (limit: 1 per symbol)
  • Current spread: 1.2 pts (limit: 30 pts) ✓
  • Risk per trade: 1% of equity = $52.18

═══════════════════════════════════════════════════════════════════

RISK PARAMETERS:
  • Default SL: ATR × 1.5 = 0.0021 × 1.5 = 0.00315 ≈ 31.5 pips
  • Use SL: 28–32 pips (round to 30)
  • Position size: (1% risk) / (30 pips × $10 pip value) = 0.17 lotes
  • TP: Use next liquidation level (EQH at 1.0832–1.0834) = +45–50 pips
  • Resulting R:R: 50 pips up / 30 pips down = 1:1.67 (acceptable, > 1.5)

═══════════════════════════════════════════════════════════════════

INSTRUCCIONES PARA ANÁLISIS:
  Idioma: ESPAÑOL

  REGLAS INAMOVIBLES:
    1. Si R:R < 1.5 → responder HOLD (nunca BUY/SELL)
    2. Si fuera de Kill Zone → responder HOLD (no operar fuera sesiones)
    3. Si Setup = NEUTRAL SIN BOS/CHOCH → responder HOLD
    4. Si Bias D1 contradice dirección → responder HOLD
    5. Si sesión con 2+ pérdidas hoy → responder HOLD
    6. Si no hay estructura (OB + FVG o BOS) → responder HOLD

  RESPONDE SIEMPRE EN JSON VÁLIDO, NADA MÁS:
  {
    "decision": "BUY|SELL|HOLD",
    "logic_path": "paso 1) ... paso 2) ... paso 3) ...",
    "risk_reward_ratio": 1.67,
    "position_size": 0.17,
    "confidence": 0.92,
    "sl_pips": 30,
    "tp_pips": 50,
    "reasoning": "EURUSD bullish, FVG mitigated at OB, London Kill Zone active, sentiment bullish, no news events. CONFIRMED setup with 75% historical WR. Spread optimal, no daily losses. Entry justified."
  }
```

### Respuesta de Claude

```json
{
  "decision": "BUY",
  "logic_path": "1) D1 macro bullish (HH, HL, EMA200 abajo). 2) H1 estructura: BOS bullish + OB + FVG sin mitigar = CONFIRMED. 3) M15 momentum alcista, precio sobre EMA9. 4) Kill Zone London activa, setup histórico 75% WR. 5) Sentimiento bullish, sin noticias. 6) R:R 1.67 > 1.5 ✓",
  "risk_reward_ratio": 1.67,
  "position_size": 0.17,
  "confidence": 0.92,
  "sl_pips": 30,
  "tp_pips": 50,
  "reasoning": "Setup CONFIRMED en Kill Zone con sentimiento bullish. FVG + OB confluence en 1.0802-1.0809 es zona de acumulación institucional. Histórico muestra 75% WR en CONFIRMED + London. Spread 1.2pts excelente, sin pérdidas de sesión. Riesgo/recompensa 1:1.67 es aceptable."
}
```

### Qué sucede después

```
confidence = 0.92 >= UMBRAL 0.85 ✓ → modo autónomo permitido
decision = "BUY" ✓ → intentar ejecución

GATE 1 (News Shield):  No hay evento en 60 min ✓ PASA
GATE 2 (Spread):       1.2 pts <= 30 pts ✓ PASA
GATE 3 (Daily Loss):   $0 + $52.18 risk <= 3% ✓ PASA
GATE 4 (Duplicado):    No hay BUY abierto ✓ PASA
GATE 5 (SL > 0):       30 pips > 0 ✓ PASA
GATE 6 (Confianza):    0.92 >= 0.85 ✓ AUTÓNOMO

RESULTADO: ORDEN ENVIADA A MT5
  symbol: EURUSD
  action: BUY
  lots: 0.17
  sl: 1.0802 (precio actual 1.0829 - 30 pips)
  tp: 1.0879 (precio actual 1.0829 + 50 pips)

LOG: "2026-04-03 10:45:30,EURUSD,BUY,0.92,30,50,1,"
```

---

## Ejemplo 2: XAUUSD en NY, pero SIN Setup estructural (HOLD)

### Contexto
- **Hora:** 14:30 UTC (09:30 Colombia, NY opening)
- **Sesión:** NY (Kill Zone ACTIVA)
- **Condición de mercado:** Neutral, rango, sin BOS/CHOCH
- **Tema:** Mercado sin dirección clara → Claude debe rechazar

### Prompt enviado a Claude (abreviado)

```
INSTRUMENT: XAUUSD

D1 MACRO — Trend: NEUTRAL | Price: 2341.50 | EMA200: 2335.20 | RSI: 51.8 | ATR: 12.50

H1 TECHNICAL — Trend: NEUTRAL | EMA20: 2340.80 | EMA50: 2338.50 | RSI: 50.2 | ATR: 4.20

SMC CONTEXT (H1):
  Structure        : Neutral (oscilando entre HH + HL sin confirmación)
  BOS              : None (precio no rompe máximo estructural)
  CHOCH            : None
  Order Blocks     : Sin OB reciente validado
  FVG Zones        : Sin FVG sin mitigar
  EQH              : [2341.80]
  EQL              : [2338.90]
  Session          : NY (Kill Zone ACTIVE)
  SMC Bias         : NEUTRAL
  Setup Type       : NEUTRAL ← sin estructura clara

ACCOUNT — Equity: $5,218.40 | Balance: $5,200.00

SESSION CONTEXT:
  Session Losses  : 1 (una pérdida en NY hoy, mercado errático)
  Spread          : 2.8 pts (normal)

HISTORICAL PERFORMANCE [15 trades]:
  By Session:
    NY Session    : 55% WR ← débil, precaución extra

REGLAS INAMOVIBLES:
  3. Si Setup = NEUTRAL SIN BOS/CHOCH → responder HOLD
  5. Si sesión con 2+ pérdidas hoy → responder HOLD (tienes 1, precaución)
```

### Respuesta de Claude

```json
{
  "decision": "HOLD",
  "logic_path": "1) Bias neutral, sin HH confirmado. 2) Setup NEUTRAL: sin BOS, sin CHOCH, sin OB/FVG validados. 3) NY sesión débil (55% WR histórico). 4) Ya 1 pérdida hoy en NY. 5) Mercado en rango, sin dirección.",
  "confidence": 0.42,
  "reasoning": "Mercado en acumulación, no hay ruptura estructural. NY sesión históricamente débil. Esperar a BOS o CHOCH antes de entrar."
}
```

### Qué sucede después

```
decision = "HOLD" → fin del análisis, mostrar resultado
Mensaje al trader: "Claude dice HOLD — mercado neutral, esperar estructura clara"

LOG: "2026-04-03 14:30:15,XAUUSD,HOLD,0.42,0,0,0,"
```

---

## Ejemplo 3: GBPUSD con Noticia de Alto Impacto (NEWS SHIELD BLOQUEA)

### Contexto
- **Hora:** 08:25 UTC (03:25 Colombia, London)
- **Evento:** **Bank of England Rate Decision en 5 minutos** (alto impacto)
- **Setup:** Bullish CONFIRMED (normalmente ejecutaría)
- **Tema:** Safety Gate 1 rechaza, aunque Claude diga BUY

### Prompt enviado a Claude (abreviado)

```
INSTRUMENT: GBPUSD

D1 MACRO — Trend: BULLISH | Price: 1.2745 | EMA200: 1.2680 | RSI: 62.3 | ATR: 0.0045

SMC CONTEXT:
  Structure      : Bullish (HH, HL, HH)
  BOS            : BullishBOS @ 1.2720
  Setup Type     : CONFIRMED

DATOS FUNDAMENTALES:
  Sentiment      : BULLISH (score = +0.52)
  Economic Events: 🔴 BoE Rate Decision in 5 minutes (HIGH IMPACT)
  News Shield    : BLOCKING — HIGH IMPACT EVENT PRÓXIMO
```

### Respuesta de Claude

```json
{
  "decision": "BUY",
  "confidence": 0.89,
  "sl_pips": 25,
  "tp_pips": 60,
  "reasoning": "Setup CONFIRMED, sentimiento bullish, estructura clara..."
}
```

### Safety Gate 1: NEWS SHIELD

```python
shield = news_data.get("_shield", {})
if shield.get("blocking"):  # TRUE ← BoE en 5 min
    _reject = t["news_reject_shield"].format(
        event="Bank of England Rate Decision",
        cur="GBP",
        n=5,
    )
    # "News Shield: Bank of England Rate Decision (GBP) en 5 min"

    st.error(f"🚫 Auto-blocked: {_reject}")
    LoggerService.log_decision(
        "GBPUSD", "BUY", 0.89, 25, 60,
        accepted=False,
        reject_reason="News Shield: BoE Rate Decision in 5 min"
    )
    st.session_state[auto_fired] = True  # no reintentar
```

### Resultado

```
❌ ORDEN RECHAZADA por Safety Gate 1
Motivo: "News Shield: Bank of England Rate Decision (GBP) en 5 min"

LOG: "2026-04-03 08:25:45,GBPUSD,BUY,0.89,25,60,0,News Shield: BoE in 5 min"

Dashboard: "🚫 Auto-blocked: News Shield: Bank of England Rate Decision (GBP) en 5 min"
```

**Nota:** Aunque Claude emitió BUY con confianza 0.89, el sistema automáticamente **rechazó la orden** porque el News Shield Gate es más confiable que cualquier predicción técnica frente a un evento macro anunciado.

---

## Ejemplo 4: USDJPY con Spread Anormalmente Alto (GATE 2)

### Contexto
- **Hora:** 19:00 UTC (14:00 Colombia, mercado cerrado en NY)
- **Evento:** Spread de 0.8 pts → salta a 18 pts (volatilidad anormal)
- **Setup:** Bullish válido, Claude emite BUY 0.87
- **Tema:** Gate 2 rechaza por spread alto

### Análisis de Claude (sin cambios)

```json
{
  "decision": "BUY",
  "confidence": 0.87,
  "sl_pips": 22,
  "reasoning": "..."
}
```

### Safety Gate 2: SPREAD FILTER

```python
_spread = service.get_spread("USDJPY")  # returns 18.0 pts

if not RiskManager.is_spread_ok(_spread, MAX_SPREAD_POINTS):  # 18 > 30? NO
    # Validación: 18 <= 30 ✓ PASA
```

**Resultado:** ORDEN EJECUTADA (spread está dentro de límite)

```
✅ ORDEN ENVIADA
Spread 18 pts es alto pero < 30 pts límite máximo
LOG: "2026-04-03 19:00:30,USDJPY,BUY,0.87,22,55,1,"
```

### Si el spread fuera 31 pts

```python
if not RiskManager.is_spread_ok(31.0, 30):  # 31 > 30? SI
    _reject = t["reject_spread"].format(spread=31.0, max=30)
    # "Spread 31.0 pts > máx 30 pts"

    st.error(f"🚫 Auto-blocked: {_reject}")
    LoggerService.log_decision(
        "USDJPY", "BUY", 0.87, 22, 55,
        accepted=False,
        reject_reason="Spread 31.0 pts > max 30 pts"
    )
```

**Resultado:** ❌ RECHAZADA por Gate 2

---

## Ejemplo 5: BTCUSD con Pérdidas del Día Cercanas al Límite (GATE 3)

### Contexto
- **Día:** Ya han ocurrido 2 operaciones perdedoras (-1.2% y -1.5% de account)
- **Pérdidas acumuladas:** -2.7% (límite es 3%)
- **Riesgo de esta operación:** 1% = $52.18
- **Tema:** Total sería -3.7% > -3% límite

### Cálculo previo a Claude

```python
_history = LoggerService.get_history()
closed = _history[_history["accion"] == "CLOSE"]
today_loss = closed[closed["fecha"] == "2026-04-03"]["profit"].sum()
# today_loss = -140.00 (en USD)

balance = 5200.00
current_loss_pct = (-140.00) / 5200.00 * 100 = -2.69%

# Esta operación riesgo: 1% = 52.18
# Total sería: -2.69% - 1% = -3.69% > -3.0% LÍMITE

# Decision: NO enviar a Claude, rechazar directamente
```

### Qué hace el sistema

```python
# app.py ~ línea 318
if RiskManager.is_daily_loss_limit_exceeded(
    _history, acc.balance, MAX_DAILY_LOSS_PCT
):
    # Esta validación ocurre DESPUÉS de Claude
    # Pero ANTES de enviar la orden a MT5

    _reject = t["reject_daily_loss"].format(pct=3.0)
    # "Daily Loss Limit: Pérdidas hoy 2.7% + riesgo 1% = 3.7% > límite 3%"

    st.error(f"🚫 Auto-blocked: {_reject}")
    LoggerService.log_decision(..., accepted=False,
                              reject_reason="Daily Loss Limit exceeded")
```

### Resultado

```
❌ ORDEN RECHAZADA por Safety Gate 3
Motivo: "Daily Loss Limit: Pérdidas hoy 2.7% > límite 3%"

Alternativa: El operador PUEDE seguir operando si cierra 1 operación ganadora
o espera al próximo día.
```

---

## Ejemplo 6: Validación de Datos ANTES de enviar a Claude

### Escenario: EMA200 = NaN (error en MT5)

```python
# anthropic_service.py ~ validación previa
d1_state = IndicatorsService.get_multi_timeframe_state("EURUSD")
ema200 = d1_state.get("d1", {}).get("ema200")

if ema200 is None or math.isnan(ema200):
    # NO enviar a Claude con "NaN"
    # Usar fallback
    ema200 = d1_state.get("d1", {}).get("close")
    ema_note = "[usando Close como fallback, EMA200 sin datos]"
else:
    ema_note = ""

# Prompt que se envía:
# "D1 MACRO — EMA200: 1.0754 [usando Close como fallback, EMA200 sin datos]"
```

### Beneficio
Claude recibe "1.0754" (valor válido) + nota de que fue fallback. Así:
- ✓ No crashea
- ✓ Sabe que ese dato puede ser menos confiable
- ✓ Puede ajustar confianza levemente hacia abajo

---

## Resumen: Tabla de Validaciones por Paso

| Paso | Dato | Validación | Si Falla |
|------|------|-----------|----------|
| **1. Recopilación** | EMA, RSI, ATR | ≠ NaN, rango válido | usar fallback |
| **1. Recopilación** | Spread | ≥ 0 y < 100 pts | usar promedio histórico |
| **1. Recopilación** | Account equity | > 0 | ERROR, no operar |
| **2. Prompt** | Todas las métricas | consistent (bid<ask, etc) | fallar early |
| **3. IA response** | JSON sintaxis | válido, parseable | HOLD default |
| **3. IA response** | decision field | ∈ {BUY, SELL, HOLD} | HOLD |
| **3. IA response** | confidence | ∈ [0.0, 1.0] | clamp a rango |
| **3. IA response** | sl_pips, tp_pips | > 0 | HOLD |
| **4. Gate 1** | News Shield | blocking = False | rechazar |
| **4. Gate 2** | Spread | ≤ 30 pts | rechazar |
| **4. Gate 3** | Daily Loss | (loss% + risk%) ≤ 3% | rechazar |
| **4. Gate 4** | Duplicate | no posición abierta | rechazar |
| **4. Gate 5** | SL | > 0 | rechazar |
| **5. MT5 order** | Respuesta retcode | = 10009 | error, no trade |

---

*Documento de ejemplos por Claude AI — iBot Trading System*
*Usar para capacitación de operadores y debugging*
