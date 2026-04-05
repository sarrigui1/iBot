# Flujo de Análisis IA — Explicación Detallada
## Qué información se envía a Claude y cómo se valida

**Fecha:** 03 de Abril de 2026
**Propósito:** Entender cada dato que llega a Claude, cómo lo procesa, y dónde mejorar

---

## 1. El Momento Crítico: Usuario Presiona "Analizar con Claude"

```
┌────────────────────────────────────────────────────────────────┐
│ DASHBOARD STREAMLIT                                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Símbolo: EURUSD | Refresco: 60s | Análisis: DISPONIBLE   │   │
│  │ ┌──────────────────────────────────────────────────────┐  │   │
│  │ │ [🧠 ANALIZAR CON CLAUDE] ← USUARIO PRESIONA          │  │   │
│  │ └──────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
            VALIDACIÓN 0: ¿Es el momento correcto?
            ════════════════════════════════════════════════════
            - ¿Han pasado ≥ 5 minutos desde el último análisis?
            - ¿El símbolo cambió? (invalida caché anterior)
            - ¿El bot está conectado a MT5?

            SI TODO OK → continuar
            NO → mostrar "Espera X minutos" o "Reconectando..."
```

---

## 2. Recopilación de Datos (sin bloqueos, en paralelo)

Una vez validado, el sistema recopila **12 bloques de información** simultáneamente:

```python
# app.py líneas ~230-250
_history       = LoggerService.get_history()
_spread        = service.get_spread(selected_symbol)
_session_loss  = RiskManager.get_session_loss_count(_history)
_cur_session   = (smc_state or {}).get("session", {}).get("session", "")
_feedback_blk  = FeedbackService.build_prompt_block(
                    symbol=selected_symbol, session=_cur_session)
```

### Bloque 1: INSTRUMENT
```
INSTRUMENT: EURUSD

✓ VALIDACIÓN:
  - Símbolo existe en config.SYMBOLS
  - Precio bid > 0 (si no, símbolo inválido en MT5)
```

### Bloque 2: D1 MACRO (Temporalidad diaria — tendencia general)
```
D1 MACRO — Trend: BULLISH | Price: 1.0832 | EMA200: 1.0754 | RSI: 58.2 | ATR: 0.0067

📊 DATOS INCLUIDOS:
  • Price:      precio cierre H1 más reciente (en D1 hay ~24 velas diarias)
  • EMA200:     media móvil 200 períodos = tendencia de 200 días
  • RSI(14):    momentum (0-100), >70 sobrecompra, <30 sobreventa
  • ATR:        volatilidad en USD

✓ VALIDACIONES ANTES DE ENVIAR:
  - ¿EMA200 existe? Si no hay 200 velas en D1, error.
  - ¿RSI en rango [0, 100]? Si no, redondear a 0-100.
  - ¿ATR > 0? Si = 0, usar valor default 0.0001.
```

### Bloque 3: H1 TECHNICAL (Temporalidad cada hora — contexto táctico)
```
H1 TECHNICAL — Trend: BULLISH | EMA20: 1.0818 | EMA50: 1.0795 | RSI: 54.1 | ATR: 0.0021

✓ VALIDACIONES IDÉNTICAS A D1:
  - EMA20, EMA50 deben estar presentes
  - RSI en [0, 100]
  - ATR > 0
```

### Bloque 4: M15 ENTRY (Temporalidad 15 minutos — precisión de entrada)
```
M15 ENTRY — Momentum: BULLISH | Price: 1.0829 | EMA9: 1.0824 | RSI: 52.8 | ATR: 0.0009

✓ VALIDACIÓN:
  - EMA9 presente
  - RSI, ATR validados como antes
  - Momentum derivado de: si Close[0] > Close[1] = "BULLISH"
```

### Bloque 5: SMC CONTEXT (Estructuras de orden de los bancos)
```
SMC CONTEXT (H1):
  Structure        : Bullish (HH, HL, HH)
  BOS              : BullishBOS @ 1.0815
  CHOCH            : None
  Order Blocks     : Bullish OB 1.0802–1.0809 | Bullish OB 1.0791–1.0797
  FVG Zones        : Bullish FVG 1.0811–1.0818
  EQH (BSL)        : [1.0832, 1.0834]
  EQL (SSL)        : [1.0798, 1.0801]
  PDH/PDL          : 1.0841 / 1.0772
  Session          : London (Kill Zone ACTIVE)
  SMC Bias         : Bullish
  Setup Type       : CONFIRMED — FVG mitigation at OB confluence

📊 CÓMO SE GENERAN ESTOS DATOS:
  • Structure: analizar últimas 100 velas H1, buscar HH (Higher High) y HL (Higher Low)
  • BOS: precio rompe el último máximo estructural significativo
  • Order Block: última vela opuesta antes del BOS
  • FVG: gap entre High/Low de 3 velas consecutivas
  • EQH/EQL: máximos/mínimos de igual nivel (±0.0002 tolerancia)
  • Setup Type: si hay FVG + OB + BOS + sesión = CONFIRMED
               si solo hay uno de estos = AGGRESSIVE

✓ VALIDACIONES:
  - ¿Hay datos suficientes (≥100 velas H1)? Si no, Setup = "INSUFFICIENT DATA"
  - ¿Hay al menos UNA estructura (OB, FVG o BOS)? Si no, Setup = "NEUTRAL"
  - ¿Estructura válida (prices aumentan lógicamente)? Si no, ignorar esa estructura.
```

### Bloque 6: ACCOUNT (Estado de la cuenta)
```
ACCOUNT — Equity: $5,218.40 | Balance: $5,200.00 | Open P&L: $18.40

✓ VALIDACIONES:
  - ¿Equity > Balance? (puede ser por ganancias no realizadas) → OK
  - ¿Equity < 0? → ERROR CRÍTICO: no enviar a Claude, mostrar alerta
  - ¿Balance = 0? → ERROR: cambio de ceros en MT5
```

### Bloque 7: SESSION CONTEXT (Hora del mercado y contexto temporal)
```
SESSION CONTEXT — Losses today: 0 | Current spread: 1.2 pts

SESSION STATE:
  • Sesión actual: London
  • En Kill Zone: YES (03:15 UTC = 10:15 local Colombia)
  • Próxima sesión: NY (abre en 5 horas)

✓ VALIDACIONES:
  - ¿Losses today > 2? → Claude recibirá "sesión con pérdidas, precaución extra"
  - ¿Spread > 30 pts? → Later será rechazado en Safety Gate 2
  - ¿Kill Zone activa? → Mejora confianza de Claude si setup es en Kill Zone
```

### Bloque 8: FUNDAMENTAL DATA (Noticias + sentimiento)
```
DATOS FUNDAMENTALES:
  Sentiment: BULLISH (score=0.35, buzz=12)
  Sin Carpetas Rojas en las próximas 2 horas.

✓ VALIDACIONES:
  - ¿Sentimiento tiene error (NO_API_KEY / HTTP_429)? → Enviar "error: API"
  - ¿Próximo evento High Impact? → Si está dentro de 60 min, Claude lo sabe
  - ¿Buzz > 0? → Hay actividad de noticias (mercado atento)
```

### Bloque 9: HISTORICAL PERFORMANCE (Lo que aprendió el bot)
```
HISTORICAL PERFORMANCE [12 trades]:
  Win rate global: 66.7% | Avg RR real: 1:1.8
  CONFIRMED setup: 75% WR (mejor setup, +33% vs promedio)
  London session: 72% WR (mejor sesión)

CALIBRATION NOTES:
  -> Aumentar confianza en setups CONFIRMED en London
  -> Usar RR mínimo 1:3 en NY (sesión débil)

✓ VALIDACIONES:
  - ¿Total de trades < 5? → No inyectar este bloque (evitar overfitting)
  - ¿Win rate < 40%? → Mostrar advertencia al trader
  - ¿Sesión actual = "mejor sesión" de historial? → Claude eleva confianza 5-10%
```

### Bloque 10: ACCOUNT RESTRICTION (Límites de riesgo)
```
ACCOUNT RESTRICTIONS:
  • Max daily loss: 3% del balance ($156)
  • Current daily loss: $0 (0%)
  • Positions open: 1 (máximo 1 por símbolo)
  • Max spread: 30 pts (actual: 1.2 pts) ✓

✓ VALIDACIÓN:
  - ¿Ya hay 1 posición en EURUSD? → Safety Gate 4 rechazará si hay BUY/SELL
  - ¿Losses + riesgo de esta operación > 3%? → Rechazar antes de enviar a Claude
```

### Bloque 11: RISK PARAMETERS (Números concretos de riesgo)
```
RISK PARAMETERS:
  • Risk per trade: 1% of equity = $52.18
  • Default SL calculation: ATR × 1.5 = 0.0067 × 1.5 = ~100 pips
  • Lot size formula: (risk_amount) / (sl_pips × pip_value_per_lot)

✓ VALIDACIÓN:
  - ¿SL > 0? → OK
  - ¿Lote mínimo 0.01? ¿Máximo 2.0? → Forzar rango
```

### Bloque 12: LANGUAGE & INSTRUCTIONS (Idioma y reglas explícitas)
```
Analyze en ESPAÑOL.

REGLAS NO NEGOCIABLES:
  1. Si RR < 1.5 → emitir HOLD automático
  2. Si fuera de Kill Zone → HOLD automático
  3. Si sin BOS/CHOCH → HOLD automático
  4. Si Bias D1 contradice entrada → HOLD automático
  5. Si sesión con 2+ pérdidas → HOLD automático

RESPONDER SIEMPRE EN JSON VÁLIDO:
{
  "decision": "BUY|SELL|HOLD",
  "confidence": 0.0-1.0,
  "logic_path": "descripción paso a paso",
  ...
}
```

---

## 3. Construcción del Prompt Final

El `AnthropicService` **construye un único string de texto** que envía a Claude:

```python
# anthropic_service.py líneas ~120-200
prompt = f"""
Eres un trader institucional SMC en una prop firm Tier-1.
Tu única responsabilidad: analizar precio y emitir BUY/SELL/HOLD.

{bloque_1_instrumento}

{bloque_2_d1_macro}
{bloque_3_h1_technical}
{bloque_4_m15_entry}

{bloque_5_smc_context}

{bloque_6_account}
{bloque_7_session}
{bloque_8_fundamental}
{bloque_9_historical_performance}
{bloque_10_account_restrictions}
{bloque_11_risk_parameters}

{bloque_12_idioma_y_reglas}

RESPONDE EN JSON PURO. NADA MÁS.
"""
```

**Tamaño aproximado:** ~2,000-2,500 caracteres = ~500-600 tokens

---

## 4. Envío a Claude Haiku 4.5 con Prefill

```python
# anthropic_service.py líneas ~220-240
messages = [
    {"role": "user", "content": prompt},
    {"role": "assistant", "content": "{"},  # ← PREFILL: fuerza JSON
]

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=500,
    messages=messages,
)

# Claude continúa desde "{" y devuelve JSON puro: {"decision":"BUY",...}
raw_json = "{" + response.content[0].text.strip()
ai_res = json.loads(raw_json)
```

### ¿Por qué prefill?

Sin prefill, Claude a veces responde:
```
"Aquí está el análisis: {"decision":"BUY",...}"
```

Con prefill `"{"`, Claude **debe** continuar desde esa brace y devolver JSON puro:
```
{"decision":"BUY","confidence":0.87,...}
```

---

## 5. Validaciones de la Respuesta Claude

Una vez que recibe el JSON, el sistema valida **cada campo antes de confiar en él**:

```python
# app.py líneas ~280-290
ai_res = st.session_state[cache_key]
decision   = ai_res.get("decision",   "HOLD")      # default HOLD si falta
confidence = ai_res.get("confidence", 0.0)         # default 0 si falta
sl_pips    = ai_res.get("sl_pips",    20)          # default 20 si falta
tp_pips    = ai_res.get("tp_pips",    40)          # default 40 si falta

# VALIDACIONES:
if decision not in ("BUY", "SELL", "HOLD"):
    st.error("Decision inválida de Claude")
    decision = "HOLD"  # forzar seguro

if not (0.0 <= confidence <= 1.0):
    st.error("Confidence fuera de rango")
    confidence = 0.0  # forzar seguro

if sl_pips <= 0:
    st.error("SL no puede ser ≤ 0")
    decision = "HOLD"  # rechazar trade

if tp_pips <= 0:
    st.error("TP no puede ser ≤ 0")
    decision = "HOLD"
```

---

## 6. Flujo de Decisión Post-IA

Después de recibir (y validar) la respuesta, el sistema **evalúa si ejecuta o no**:

```
┌─────────────────────────────────────────────────────┐
│ Claude devolvió JSON válido                         │
│ decision ∈ {BUY, SELL, HOLD}                        │
│ confidence ∈ [0.0, 1.0]                             │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
          ¿decision == "HOLD"?
          /                   \
        SÍ                     NO (BUY o SELL)
         │                          │
         ▼                          ▼
    MOSTRAR RESULTADO         ¿confidence ≥ 0.85?
    "Claude dice HOLD"        /              \
    Fin                      SÍ              NO
                              │               │
                              ▼               ▼
                      ¿Modo autónomo?  SOLO MANUAL
                      /           \     Mostrar botón
                     SÍ            NO   "Ejecutar"
                      │             │
                      ▼             ▼
                  SAFETY GATES    (espera trader)
                  (6 capas)
                      │
                ¿Algún gate        ¿Trader presiona
                   falla?          "Ejecutar"?
                /       \              │
              SÍ         NO           ▼
              │          │      VALIDAR GATES
              │          │      (mismas 6 capas)
              │          ▼
              │      ENVIAR ORDEN MT5
              │
              ▼
          RECHAZAR
          + Log en CSV
          "Rechazado por: [GATE]"
```

---

## 7. Las 6 Safety Gates en Detalle

Cada gate es **independiente** — si **cualquiera** falla, la orden se rechaza.

### GATE 1: NEWS SHIELD (Paso 1)

```python
if shield.get("blocking"):  # ¿Hay Carpeta Roja en próximos 60 min?
    _reject = t["news_reject_shield"].format(
        event=shield.get("event_name", "?"),
        cur=shield.get("currency", "?"),
        n=shield.get("mins_away", "?"),
    )
    # Ejemplo: "News Shield: NFP (USD) en 30 min"
    # RECHAZA LA ORDEN
```

**Validaciones del dato:**
- ¿shield tiene key "blocking"? Si no, asumir False (no bloquea)
- ¿mins_away > 0 y < NEWS_SHIELD_MINUTES (60)? Si sí, bloquea

### GATE 2: SPREAD FILTER (Paso 2)

```python
if not RiskManager.is_spread_ok(_spread, MAX_SPREAD_POINTS):  # ¿Spread > 30?
    _reject = t["reject_spread"].format(spread=_spread, max=MAX_SPREAD_POINTS)
    # Ejemplo: "Spread 45 pts > máx 30 pts"
```

**Validaciones:**
- ¿Spread es numérico? Si no, calcular: (ask - bid) / point_size
- ¿Spread >= 0? Si < 0, ignorar (error en MT5, usar valor default)

### GATE 3: DAILY LOSS LIMIT (Paso 3)

```python
if RiskManager.is_daily_loss_limit_exceeded(_history, acc.balance, MAX_DAILY_LOSS_PCT):
    _reject = t["reject_daily_loss"].format(pct=MAX_DAILY_LOSS_PCT)
    # Ejemplo: "Pérdidas hoy 3.2% > límite 3%"
```

**Validaciones:**
- ¿_history es DataFrame válido? Si está vacío, asumir sin pérdidas
- ¿Cerrado trades hoy? Sumar losses, dividir por balance
- ¿Resultado + riesgo de esta operación > 3%? Rechazar

### GATE 4: DUPLICATE POSITION GUARD (Paso 4)

```python
if RiskManager.has_open_position(_df_pos, selected_symbol, decision):
    _reject = t["reject_duplicate"].format(sym=selected_symbol, dir=decision)
    # Ejemplo: "Ya hay BUY abierto en EURUSD"
```

**Validaciones:**
- ¿_df_pos contiene la columna "symbol"? Si no, error en MT5
- ¿Hay posición con symbol == "EURUSD" Y type == 0 (BUY) o 1 (SELL)?
- Si hay coincidencia, rechazar para no duplicar

### GATE 5: SL GUARD (Paso 5)

```python
if sl <= 0:  # ¿SL inválido?
    st.error(t["error_no_sl"])  # "SL no puede ser ≤ 0"
    return  # Rechazar sin enviar a MT5
```

**Validación:**
- sl_pips debe venir de Claude en la respuesta
- Si Claude devolvió sl_pips = 0, rechazar (riesgo ilimitado)

### GATE 6: CONFIDENCE THRESHOLD (Paso 6 — no rechaza, muta de autónomo a manual)

```python
if confidence < AUTONOMOUS_CONFIDENCE_THRESHOLD:  # 0.85
    # No rechaza — solo requiere confirmación manual
    # Mostrar botón "Ejecutar {decision} — {lot} lotes"
else:
    # confidence ≥ 0.85 → ejecutar sin confirmación
    handle_trade(decision, selected_symbol, lot, sl_pips, tp_pips, auto=True)
```

**Validación:**
- ¿confidence está en [0.0, 1.0]? Si no, forzar a ese rango
- ¿confidence >= threshold? Si sí, ejecutar autónomo; si no, esperar trader

---

## 8. Ejecución Final: handle_trade()

Si **todos los gates pasan**, se ejecuta:

```python
def handle_trade(action, sym, lot, sl, tp, auto=False):

    # GUARD FINAL: ¿SL > 0?
    if sl <= 0:
        st.error(t["error_no_sl"])
        return

    # ENVIAR ORDEN MT5
    res = service.send_order(sym, action, lot, sl, tp)

    # ¿Respuesta válida?
    if res is None:
        st.error(t["order_no_response"])  # "MT5 no respondió"
        return

    # ¿Orden ejecutada? (retcode 10009 = OK)
    if res.retcode == 10009:
        # ✅ ÉXITO
        FeedbackService.log_trade_context(...)  # guardar para aprendizaje
        st.toast(f"✅ {action} {lot} lotes en {sym}")
        time.sleep(1)
        st.rerun()  # actualizar dashboard
    else:
        # ❌ ERROR MT5
        st.error(f"Error {res.retcode}: {res.comment}")
```

---

## 9. Registro Completo de la Decisión

**Siempre** se registra en CSV (`trading_decisions.csv`):

```csv
fecha,simbolo,decision,confianza,sl_pips,tp_pips,aceptada,motivo_rechazo
2026-04-03 10:15:30,EURUSD,BUY,0.87,18,40,1,
2026-04-03 10:20:15,GBPUSD,SELL,0.92,22,55,1,
2026-04-03 10:25:45,USDJPY,HOLD,0.71,0,0,0,confidence < 0.85
2026-04-03 10:30:00,XAUUSD,BUY,0.88,520,1300,0,Daily loss 3.2% > 3%
```

Esto permite **auditoría completa** y **mejora continua** del sistema.

---

## 10. Puntos de Mejora Identificados

### 🔴 Prioridad ALTA

| Mejora | Razón | Esfuerzo |
|--------|-------|----------|
| **Validar datos en tiempo real antes de enviar a Claude** | Actualmente enviamos datos que podrían ser NaN o inválidos | 🔧 Bajo |
| **Agregar timeout explícito a Claude (máx 3 segundos)** | Si Claude demora > 3s, mostrar "Análisis lento" | 🔧 Bajo |
| **Detectar NaN en indicadores y usar fallback** | Si EMA = NaN, usar Close price como fallback | 🔧 Bajo |
| **Revisar estructura SMC antes de enviar a Claude** | Si Setup = "NEUTRAL" y Bias = "Neutral", aumentar caché mínimo | 🔧 Bajo |

### 🟡 Prioridad MEDIA

| Mejora | Razón | Esfuerzo |
|--------|-------|----------|
| **Agregar "señal de divergencia"** | RSI sube pero precio baja = precaución | 🔧 Bajo |
| **Validar que bid/ask no sean iguales** | Si bid == ask, spread = 0 (anormal) | 🔧 Bajo |
| **Alertar si EMA200 < Close pero Trend = BULLISH** | Contradicción en datos — verificar fuente | 🔧 Bajo |
| **Agregar timestamp exacto a cada bloque** | Saber si datos de 1 min vs 5 min vs stale | 🔧 Medio |

### 🟢 Prioridad BAJA (Nice-to-have)

| Mejora | Razón | Esfuerzo |
|--------|-------|----------|
| **Enviar score de confiabilidad de datos al lado de cada valor** | "Price: 1.0832 (score: 0.95)" — qué tan reciente | 🔧 Medio |
| **Comparar predicción de Claude vs. resultado real en tiempo real** | Dashboard: "Claude dijo BUY a 1.0815, precio ahora 1.0840 (+25 pips)" | 🔧 Medio |
| **Agregar "notas de operador"** en cada orden (texto libre) | "Operador cree que hay divergencia no detectada" | 🔧 Bajo |

---

## 11. Test de Validación: Escenarios Críticos

### Escenario 1: EMA inválida (NaN)

```
Claude recibe: "EMA200: NaN"
✓ DEBE FALLAR:
  - En anthropic_service.py, validar EMA != NaN antes de hacer f-string
  - Si NaN, reemplazar con Close price y anotar "[usando Close como fallback]"

Hoy: ❌ RIESGO: Claude ve "NaN" y puede responder con lógica incierta
Mejora: ✅ Reemplazar NaN con Close, documentar en prompt
```

### Escenario 2: Spread anormalmente alto en el último segundo

```
Última lectura: Spread 1.2 pts ✓
Usuario presiona "Analizar" → retraso de 0.5s
Nueva lectura: Spread 450 pts (¿flash crash o glitch MT5?)

✓ DEBE VALIDAR:
  - Comparar spread con histórico (últimos 5 lecturas)
  - Si spread actual > 5× promedio, usar promedio en lugar de valor puntual
  - Anotar: "[spread anomalía detectada, usando promedio]"

Hoy: ❌ RIESGO: Claude ve 450 pts y rechaza lógicamente
Mejora: ✅ Detección de outliers, usar mediana de últimas 5 muestras
```

### Escenario 3: Clock skew (reloj local vs. MT5 desincronizados)

```
Hora local: 10:15 (pensamos que es London Kill Zone)
Hora MT5 (broker UTC+2): 15:45 (en realidad es Asia, no Londres)

✓ DEBE VALIDAR:
  - Comparar server_time (MT5) vs. local_time cada ciclo
  - Si diferencia > 5 minutos, alertar "Sincronización de reloj recomendada"
  - Usar SIEMPRE server_time (MT5) para sesiones, no local

Hoy: ⚠️ RIESGO: Operador cree estar en Kill Zone cuando no lo está
Mejora: ✅ Validar sync cada 60 segundos
```

### Escenario 4: Claude devuelve JSON incompleto

```
Claude devuelve:
{
  "decision": "BUY",
  "confidence": 0.88
  (falta: logic_path, sl_pips, tp_pips, reasoning)
}

✓ DEBE MANEJAR:
  - Validar que todos los campos requeridos estén presentes
  - Si faltan: sl_pips, usar ATR × 1.5 como default
            tp_pips, usar sl_pips × 2 como default
  - Anotar en log: "JSON incompleto de Claude, usando defaults"

Hoy: ⚠️ RIESGO: KeyError si accedemos a fields que no existen
Mejora: ✅ Usar .get() con defaults, validación schema al inicio
```

---

## 12. Checklist de Validación Pre-Envío a Claude

Antes de enviar el prompt a Claude, el sistema DEBE validar:

```python
# Checklist que proponer implementar en app.py
validations = {
    "INSTRUMENT": {
        "symbol": selected_symbol in SYMBOLS,
    },
    "D1_MACRO": {
        "price": price > 0,
        "ema200": ema200 > 0 and not isnan(ema200),
        "rsi": 0 <= rsi <= 100,
        "atr": atr > 0,
    },
    "H1_TECHNICAL": {
        "ema20": ema20 > 0 and not isnan(ema20),
        "ema50": ema50 > 0 and not isnan(ema50),
        "rsi": 0 <= rsi <= 100,
        "atr": atr > 0,
    },
    "M15_ENTRY": {
        "ema9": ema9 > 0 and not isnan(ema9),
        "rsi": 0 <= rsi <= 100,
    },
    "SMC_CONTEXT": {
        "has_structures": len(order_blocks) > 0 or len(fvg_zones) > 0,
        "setup_type": setup_type in ["AGGRESSIVE", "CONFIRMED", "NEUTRAL"],
        "bias": bias in ["Bullish", "Bearish", "Neutral"],
    },
    "ACCOUNT": {
        "equity": equity > 0,
        "balance": balance > 0 and balance <= equity,
    },
    "SESSION": {
        "session_name": session in ["London", "NY", "Asia", "OFF"],
        "losses_today": losses_today >= 0,
        "spread": 0 <= spread <= 100,  # anything > 100 es anormal
    },
}

failed = [k for k, checks in validations.items() if not all(checks.values())]
if failed:
    st.error(f"Validación fallida en: {', '.join(failed)}")
    st.stop()  # NO enviar a Claude si hay datos inválidos
else:
    # OK para enviar
    ai_res = ai_agent.get_strategy_decision(...)
```

---

## 13. Conclusión: El Flujo Completo en 2 Minutos

```
USUARIO PRESIONA "ANALIZAR"
        ↓
VALIDAR: ¿5 min desde último análisis? ¿Símbolo válido? ¿MT5 conectado?
        ↓
RECOPILAR 12 BLOQUES DE DATOS (paralelo)
        ↓
VALIDAR: ¿EMA ≠ NaN? ¿RSI en [0,100]? ¿Spread normal? ¿Account > 0?
        ↓
SI FALLA ALGUNA VALIDACIÓN → mostrar error y STOP (no enviar a Claude)
        ↓
CONSTRUIR PROMPT (12 bloques + rules)
        ↓
ENVIAR A CLAUDE (con prefill "{" para forzar JSON)
        ↓
RECIBIR JSON
        ↓
VALIDAR JSON: ¿decision en {BUY, SELL, HOLD}? ¿confidence en [0,1]?
        ↓
SI FALLA → usar defaults y HOLD automático
        ↓
¿decision == HOLD? → mostrar resultado, fin
¿decision ∈ {BUY, SELL}?
        ├─ confidence < 0.85 → esperar confirmación manual
        └─ confidence ≥ 0.85 → evaluar 6 Safety Gates
                ↓
GATE 1: ¿News Shield? → rechazar si Carpeta Roja en 60 min
GATE 2: ¿Spread > 30? → rechazar
GATE 3: ¿Pérdidas > 3%? → rechazar
GATE 4: ¿Ya hay posición? → rechazar
GATE 5: ¿SL > 0? → rechazar si no
GATE 6: (solo muta a manual, no rechaza)
        ↓
SI ALGÚN GATE RECHAZA → log en CSV y mostrar motivo
SI TODOS PASAN → enviar orden MT5
        ↓
¿Retcode 10009? → éxito, guardar para aprendizaje, actualizar dashboard
¿Error MT5? → mostrar error específico del bróker
        ↓
REGISTRO: guardar en trading_decisions.csv (auditoría completa)
        ↓
FIN
```

---

**Documentado por:** Equipo de desarrollo iBot
**Fecha de revisión sugerida:** Cada 50 operaciones (calibrar umbrales con datos reales)
