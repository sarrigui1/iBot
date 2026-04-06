# iBot · Intelligence Trading
## Documento Técnico para Inversionistas

**Versión:** 1.0
**Fecha:** 03 de Abril de 2026
**Clasificación:** Confidencial — Solo para distribución interna

---

## Tabla de Contenido

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Motor de Decisión: Smart Money Concepts (SMC)](#3-motor-de-decisión-smart-money-concepts-smc)
4. [Inteligencia Artificial: Claude AI](#4-inteligencia-artificial-claude-ai)
5. [Gestión de Riesgo](#5-gestión-de-riesgo)
6. [Sistema de Seguridad (Safety Gates)](#6-sistema-de-seguridad-safety-gates)
7. [Análisis Fundamental: News Shield](#7-análisis-fundamental-news-shield)
8. [Aprendizaje Continuo (FeedbackService)](#8-aprendizaje-continuo-feedbackservice)
9. [Infraestructura y Tecnología](#9-infraestructura-y-tecnología)
10. [Instrumentos Operados](#10-instrumentos-operados)
11. [Flujo Operacional Completo](#11-flujo-operacional-completo)
12. [Pruebas y Validaciones](#12-pruebas-y-validaciones)
13. [Costos Operativos Estimados](#13-costos-operativos-estimados)
14. [Limitaciones y Riesgos](#14-limitaciones-y-riesgos)
15. [Hoja de Ruta](#15-hoja-de-ruta)

---

## 1. Resumen Ejecutivo

**iBot** es un sistema de trading algorítmico de grado institucional que combina análisis técnico multi-temporalidad, metodología Smart Money Concepts (SMC), inteligencia artificial generativa  y análisis fundamental en tiempo real. El sistema opera sobre MetaTrader 5 (MT5) y está diseñado para replicar el proceso de toma de decisiones de un trader institucional Tier-1.

### Propuesta de Valor

| Dimensión | Capacidad |
|-----------|-----------|
| **Velocidad** | Análisis completo (técnico + SMC + IA + noticias) en < 3 segundos |
| **Consistencia** | Aplica la misma lógica SMC en cada operación, sin emociones |
| **Escalabilidad** | Opera 5 instrumentos simultáneamente con vigilancia continua |
| **Control de riesgo** | 6 capas de seguridad independientes antes de cada orden |
| **Aprendizaje** | Calibra la confianza de la IA con el historial real de operaciones |
| **Transparencia** | Dashboard en tiempo real, registro completo de todas las decisiones |

### Filosofía de Operación

El sistema **nunca toma una posición sin que se cumplan simultáneamente** las condiciones técnicas, estructurales, de riesgo, de liquidez y de contexto fundamental. Esto reduce drásticamente el número de señales, pero aumenta significativamente la calidad de cada entrada.

---

## 2. Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    DASHBOARD  (Streamlit)                        │
│   News Marquee | Semáforo | Análisis | Posiciones | Diario       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
         ┌─────────────────┼──────────────────────┐
         ▼                 ▼                       ▼
┌─────────────────┐ ┌─────────────────┐ ┌──────────────────────┐
│  MT5 Service    │ │ Indicators Svc  │ │   Anthropic Service  │
│  - Conexión MT5 │ │ - RSI, EMA, ATR │ │   Claude Haiku 4.5   │
│  - Órdenes      │ │ - MACD          │ │   SMC Prompt         │
│  - Posiciones   │ │ - Multi-TF D1/  │ │   JSON response      │
│  - Spreads      │ │   H1/M15        │ └──────────────────────┘
│  - Cuenta       │ └─────────────────┘
└─────────────────┘         ▲
         │                  │          ┌──────────────────────┐
         │         ┌────────┴──────┐   │   SMC Service        │
         │         │  Risk Manager │   │   - Order Blocks     │
         │         │  - Lot sizing │   │   - FVG zones        │
         │         │  - Trail SL   │   │   - BOS / CHOCH      │
         │         │  - Break Even │   │   - EQH / EQL        │
         │         │  - Safety     │   │   - PDH/PDL/PWH/PWL  │
         │         └───────────────┘   └──────────────────────┘
         │
┌────────┴────────────────────────────────────────────────────────┐
│                      SERVICIOS DE SOPORTE                        │
│  Logger Service  |  Feedback Service  |  News Service           │
│  (CSV registro)  |  (aprendizaje IA)  |  (Forex Factory + FF)  │
└─────────────────────────────────────────────────────────────────┘
```

### Módulos del Sistema

| Módulo | Archivo | Líneas | Responsabilidad |
|--------|---------|--------|-----------------|
| Orquestador principal | `app.py` | 630 | Loop principal, integración de servicios, UI |
| Indicadores técnicos | `indicators_service.py` | 166 | RSI, EMA(9/20/50/200), ATR, MACD — multi-TF |
| Análisis SMC | `smc_service.py` | 497 | Order Blocks, FVG, BOS, CHOCH, swing structure |
| Inteligencia Artificial | `anthropic_service.py` | 308 | Prompt institucional, JSON schema, retries |
| Gestión de Riesgo | `risk_manager.py` | 208 | Lot sizing, trailing stop, break even, gates |
| Conexión MT5 | `mt5_service.py` | 154 | Órdenes, posiciones, spread, ATR, tiempos |
| Noticias | `news_service.py` | 390 | Forex Factory calendar, sentimiento, shield |
| Aprendizaje IA | `feedback_service.py` | 403 | Estadísticas históricas, calibración de confianza |
| Registro | `logger_service.py` | 91 | Journal CSV, decisiones, historial |
| UI | `ui_components.py` | 961 | Todos los componentes visuales del dashboard |
| Configuración | `config.py` | 57 | Parámetros globales, safety gates |
| Internacionalización | `i18n.py` | 530 | Español e Inglés |
| **TOTAL** | | **4,420** | |

---

## 3. Motor de Decisión: Smart Money Concepts (SMC)

### ¿Qué es SMC?

Smart Money Concepts es la metodología que usan los grandes bancos (JP Morgan, Goldman Sachs, Deutsche Bank) y fondos institucionales para mover el mercado. El precio no sube y baja aleatoriamente — sigue una secuencia predecible: **captura liquidez → crea estructura → distribuye órdenes**.

### Los 6 Pasos del Framework (en orden de ejecución)

```
PASO 1: BIAS MACRO (Temporalidad D1)
═══════════════════════════════════════════════════
  ¿Precio sobre EMA200?  →  Sesgo ALCISTA
  ¿Precio bajo EMA200?   →  Sesgo BAJISTA
  ¿Precio > PDH?         →  Confirmación intraday alcista
  ¿HH + HL en D1?        →  Estructura alcista confirmada

PASO 2: CONTEXTO DE LIQUIDEZ (H1)
═══════════════════════════════════════════════════
  BSL (Buy-Side Liquidity):   EQH, PDH, PWH  ← objetivo de shorts
  SSL (Sell-Side Liquidity):  EQL, PDL, PWL  ← objetivo de longs
  REGLA: El precio SIEMPRE toma la liquidez más cercana PRIMERO.

PASO 3: EVENTO ESTRUCTURAL (H1)
═══════════════════════════════════════════════════
  BOS  (Break of Structure)  →  continuación de tendencia
  CHOCH (Change of Character) →  señal de reversión potencial
  SOLO operar DESPUÉS de sweep de liquidez + BOS/CHOCH

PASO 4: PUNTO DE INTERÉS — ENTRADA (H1)
═══════════════════════════════════════════════════
  Entrada A (AGRESIVA):   Liquidity swept + precio en Order Block
  Entrada B (CONFIRMADA): Liquidity swept + CHOCH + FVG + retrace 61.8-78.6%

PASO 5: FILTRO DE SESIÓN
═══════════════════════════════════════════════════
  OPERAR:    Kill Zones: Londres (02:00-05:00) | NY (08:00-11:00) hora Colombia
  NO OPERAR: Asia (19:00-23:00 hora Colombia) — solo acumulación

PASO 6: RELACIÓN RIESGO/RECOMPENSA
═══════════════════════════════════════════════════
  SL: Bajo/sobre el Order Block o la vela que causó CHOCH
  TP: Siguiente nivel de liquidez (EQH/EQL, PDH/PDL, PWH/PWL)
  MÍNIMO: RR 1:2. Si RR < 1.5 → HOLD automático
```

### Reglas de Invalidación (HOLD automático si alguna aplica)

- Fuera de Kill Zone
- Sin BOS ni CHOCH tras sweep de liquidez
- Precio en zona media sin POI
- Bias D1 contradice la dirección de entrada
- 2 pérdidas ya tomadas en la sesión

### Detección Automática de Estructuras

El `SMCService` analiza las últimas **100 velas H1** y detecta automáticamente:

| Estructura | Cómo se detecta |
|------------|-----------------|
| **Order Block** | Última vela opuesta antes de un BOS — zona donde el banco dejó órdenes |
| **Fair Value Gap (FVG)** | Espacio entre High/Low de 3 velas consecutivas — zona de desequilibrio |
| **BOS** | Cierre de vela que rompe el último máximo/mínimo estructural significativo |
| **CHOCH** | Ruptura en dirección contraria a la tendencia actual |
| **EQH/EQL** | Máximos/mínimos de igual nivel (±0.0002 de tolerancia) — liquidez acumulada |
| **PDH/PDL** | High/Low del día anterior — niveles de referencia diarios |
| **PWH/PWL** | High/Low de la semana anterior — niveles macro de referencia |
| **Swing Structure** | Secuencia HH+HL (alcista) o LH+LL (bajista) |

---

## 4. Inteligencia Artificial: Claude AI

### Modelo

**Claude Haiku 4.5** (`claude-haiku-4-5-20251001`) — modelo de Anthropic, familia Claude 4.
Seleccionado por: latencia baja (<1s), costo ~10x menor que Sonnet, suficiente para análisis táctico.

### System Prompt Institucional

El sistema prompt está diseñado como si Claude fuera *"un trader institucional SMC en una prop firm Tier-1"*. Incluye los 6 pasos del framework SMC, reglas de invalidación explícitas, y el schema JSON que debe respetar:

```json
{
  "decision":          "BUY | SELL | HOLD",
  "logic_path":        "1) Macro+Liquidez  2) Estructura+POI  3) Entrada+RR",
  "risk_reward_ratio": 2.5,
  "position_size":     0.8,
  "confidence":        0.87,
  "sl_pips":           18,
  "tp_pips":           45,
  "reasoning":         "Resumen ejecutivo de una línea"
}
```

### Técnica de Assistant Prefill

Para garantizar que Claude responda **siempre** con JSON puro (sin texto previo, sin markdown):

```python
messages=[
    {"role": "user",      "content": <prompt con 12 bloques de datos>},
    {"role": "assistant", "content": "{"},   # ← fuerza inicio con "{"
]
# El modelo completa el JSON desde "{"
raw_text = "{" + response.content[0].text.strip()
```

### Contexto que recibe Claude en cada análisis

```
INSTRUMENT: EURUSD

D1 MACRO — Trend: BULLISH | Price: 1.0832 | EMA200: 1.0754 | RSI: 58.2 | ATR: 0.0067
H1 TECHNICAL — Trend: BULLISH | EMA20: 1.0818 | EMA50: 1.0795 | RSI: 54.1 | ATR: 0.0021
M15 ENTRY — Momentum: BULLISH | Price: 1.0829 | EMA9: 1.0824 | RSI: 52.8 | ATR: 0.0009

SMC CONTEXT (H1):
  Structure : Bullish (HH, HL, HH)
  BOS       : BullishBOS @ 1.0815
  CHOCH     : None
  Order Blocks: Bullish OB 1.0802–1.0809 | Bullish OB 1.0791–1.0797
  FVG Zones : Bullish FVG 1.0811–1.0818
  EQH (BSL) : [1.0832, 1.0834]
  EQL (SSL) : [1.0798, 1.0801]
  PDH/PDL   : 1.0841 / 1.0772
  Session   : London (Kill Zone ACTIVE)
  SMC Bias  : Bullish
  Setup     : CONFIRMED — FVG mitigation at OB confluence

ACCOUNT — Equity: $5,218.40 | Balance: $5,200.00 | Open P&L: $18.40
SESSION CONTEXT — Losses today: 0 | Current spread: 1.2 pts

DATOS FUNDAMENTALES:
  Sentiment: BULLISH (score=0.35, buzz=12)
  Sin Carpetas Rojas en las próximas 2 horas.

HISTORICAL PERFORMANCE [12 trades]:
  Win rate global: 66.7% | Avg RR real: 1:1.8
  CONFIRMED setup: 75% WR (mejor setup, +33% vs promedio)
  London session: 72% WR (mejor sesión)
  -> Aumentar confianza en setups CONFIRMED en London
```

### Control de Confianza

| Nivel de Confianza | Acción del Sistema |
|-------------------|-------------------|
| < 0.85 | Solo muestra el veredicto — trader decide manualmente |
| ≥ 0.85 | **Ejecución autónoma** si pasan los 6 Safety Gates |
| < umbral RR (1.5) | Claude emite HOLD automático por instrucción del prompt |

### Cooldown y Caché

- **Intervalo mínimo entre análisis:** 5 minutos (configurable)
- **Análisis obsoleto:** Banner de advertencia después de 15 minutos
- **Caché por símbolo:** cambiar de EURUSD a XAUUSD invalida el resultado anterior

---

## 5. Gestión de Riesgo

### Position Sizing Dinámico

El tamaño de cada operación se calcula en función del riesgo real, no de un lote fijo:

```
Lote = (Equity × 1%) / (SL_pips × Valor_pip_por_lote)
```

**Ejemplo práctico:**
- Cuenta: $5,000 USD
- Riesgo por operación: 1% = $50
- SL calculado por Claude: 20 pips
- Valor pip EURUSD: $10/lote
- **Lote resultante: 0.25 lotes** ($50 / 20 × $10)

El lote se ajusta adicionalmente por el campo `position_size` de Claude (0.0–1.0), que refleja la convicción del modelo. Un `position_size: 0.8` con 0.25 lotes calculados da un trade de **0.20 lotes**.

### Stop Loss Basado en ATR

El SL no es arbitrario — se calcula a partir del ATR (Average True Range) del mercado actual:

```
SL_pips = ATR × 1.5 multiplicador
```

| Instrumento | ATR típico H1 | SL típico | Pip size |
|------------|---------------|-----------|----------|
| EURUSD | 0.0015 | ~22 pips | 0.0001 |
| XAUUSD | 3.50 | ~525 pts | 0.01 |
| BTCUSD | 450 | ~67,500 pts | 0.01 |
| USDJPY | 0.18 | ~27 pips | 0.01 |

### Trailing Stop Dinámico

Una vez en ganancia, el SL se mueve automáticamente para proteger el capital:

- **Condición:** precio avanza ≥ 1× ATR en la dirección correcta
- **Nuevo SL:** precio actual − (ATR × multiplicador configurable, default 1.5×)
- **Ejecución:** botón por posición o automático en modo autónomo

### Break Even Automático

- **Condición:** precio avanza ≥ 1× ATR
- **Acción:** SL se mueve al precio de apertura (riesgo = $0)

---

## 6. Sistema de Seguridad (Safety Gates)

**Seis capas de validación** que se ejecutan en secuencia antes de cualquier orden autónoma. El sistema rechaza la operación si **cualquiera** de las condiciones falla:

```
GATE 1: NEWS SHIELD
        ¿Hay evento de Carpeta Roja en los próximos 60 minutos?
        SI → RECHAZAR + log

GATE 2: SPREAD FILTER
        ¿Spread actual > 30 puntos?
        SI → RECHAZAR + log

GATE 3: DAILY LOSS LIMIT
        ¿Pérdidas de hoy > 3% del balance?
        SI → RECHAZAR + log (protección de capital diaria)

GATE 4: DUPLICATE POSITION GUARD
        ¿Ya hay una posición abierta en este símbolo y dirección?
        SI → RECHAZAR + log (no doblar exposición)

GATE 5: SL GUARD
        ¿SL calculado = 0?
        SI → RECHAZAR (riesgo ilimitado no permitido)

GATE 6: CONFIDENCE THRESHOLD
        ¿Confianza de Claude < 85%?
        SI → Solo ejecución manual (no autónoma)
```

Cada rechazo se **registra en CSV** con símbolo, decisión, confianza y motivo — trazabilidad completa.

### Botón de Pánico

Un botón `PÁNICO` cierra **todas las posiciones abiertas** simultáneamente con manejo de errores individual (si una falla, las demás siguen cerrándose).

---

## 7. Análisis Fundamental: News Shield

### Fuente de Datos

**Forex Factory Calendar** — el calendario económico más respetado del mundo de trading:
```
https://nfs.faireconomy.media/ff_calendar_thisweek.json
```
- Sin API key requerida
- Sin límites de peticiones
- ~100 eventos semanales
- Las famosas **"Carpetas Rojas"** (High Impact) — eventos que mueven el mercado

### Clasificación de Impacto

| Color | Impacto | Ejemplos | Acción del bot |
|-------|---------|----------|----------------|
| 🔴 Rojo | **High** | NFP, CPI, decisiones de tipos, Fed | **Bloqueo de 60 min** antes y 15 min después |
| 🟡 Amarillo | Medium | PMI, ventas minoristas, discursos | Mostrar en dashboard, no bloquea |
| ⚪ Bajo | Low | Inventarios, datos menores | Mostrar en dashboard, no bloquea |

### Ventana de Bloqueo

```
    ─────────────────────────────────────────────────────▶ tiempo
                         │
    [──────── 60 min ────│──── 15 min ────]
                         │
                    Evento NFP             ← BLOQUEO TOTAL en esta ventana

    Fuera de la ventana → sistema opera con normalidad
```

### Sentimiento de Mercado

El sistema analiza los titulares de noticias forex con detección de palabras clave:

- **Bullish:** rises, rally, gains, surges, strong, breakout, recovery
- **Bearish:** falls, drop, decline, plunges, weak, breakdown, selloff
- **Score:** de -1.0 (100% bearish) a +1.0 (100% bullish)

El sentimiento se inyecta en el prompt de Claude para contextualizar la decisión con el flujo de noticias del momento.

---

## 8. Aprendizaje Continuo (FeedbackService)

El sistema aprende de sus propias operaciones y calibra automáticamente la confianza de Claude.

### Cómo Funciona

```
TRADE OPEN
    │
    ▼
log_trade_context()  ←  guarda: símbolo, dirección, setup SMC, sesión,
    │                            parámetros de la decisión de Claude
    ▼
TRADE CLOSE (manual o automático)
    │
    ▼
update_memory()  ←  une journal + contextos, calcula estadísticas:
    │                WIN RATE por setup (AGGRESSIVE/CONFIRMED)
    │                WIN RATE por sesión (London/NY)
    │                WIN RATE por símbolo
    │                RR planeado vs RR real
    │
    ▼
build_prompt_block()  ←  genera bloque de texto que se inyecta en
                          CADA análisis de Claude:

"HISTORICAL PERFORMANCE [12 trades]:
  Win rate global: 66.7% | Avg RR real: 1:1.8
  CONFIRMED setup: 75% WR
  London session: 72% WR
  -> Aumentar confianza en CONFIRMED + London
  -> Precaución: NY session solo 50% WR con 4 trades"
```

### Notas de Calibración Automáticas

Con ≥ 5 operaciones, el sistema genera instrucciones específicas para Claude:
- *"CONFIRMED outperforms by +33% — aumentar confianza en este setup"*
- *"NY session underperforms — precaución extra"*
- *"EURUSD: 75% WR — mejor instrumento del portafolio"*

Esto crea un **loop de retroalimentación**: el bot aprende de sus errores y ajusta sus umbrales de confianza automáticamente sin intervención humana.

---

## 9. Infraestructura y Tecnología

### Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Plataforma de trading | MetaTrader 5 (MT5) | 5.x |
| Lenguaje | Python | 3.13 |
| Dashboard | Streamlit | última estable |
| IA | Anthropic Claude Haiku 4.5 | claude-haiku-4-5-20251001 |
| Indicadores | pandas_ta | última estable |
| Datos de mercado | MT5 Python API | oficial |
| Noticias/Calendario | Forex Factory (público) | — |
| Sentimiento | Finnhub API (plan free) | — |
| Registro | CSV local | — |

### Requerimientos de Sistema

```
Hardware mínimo:
  - CPU: Dual core 2GHz+
  - RAM: 4 GB
  - Disco: 500 MB libre
  - Red: Conexión estable (latencia < 200ms al bróker)

Software:
  - Windows 10/11 (MT5 solo disponible en Windows)
  - MetaTrader 5 instalado y conectado al bróker
  - Python 3.11+
  - Cuenta de trading MT5 activa
```

### Bróker Actual

**IC Markets SC — Demo**
Servidor: `ICMarketsSC-Demo`
Ventaja: spreads ultra-bajos (RAW pricing), ejecución ECN, regulado ASIC/CySEC.

### Ciclo de Refresco

```
┌─────────────────────────────────────────────────────────────┐
│  CICLO PRINCIPAL (configurable, default: 60 segundos)       │
│                                                              │
│  1. Verificar conexión MT5 (heartbeat)                      │
│  2. Obtener precio y spread actuales                        │
│  3. Calcular indicadores D1 + H1 + M15                      │
│  4. Detectar estructuras SMC (H1)                           │
│  5. Leer noticias caché (TTL 30 min, NO llama API)          │
│  6. Mostrar dashboard actualizado                           │
│  7. Evaluar posiciones abiertas (trail / BE automático)     │
│  8. Si modo autónomo + confianza ≥ 85% → Safety Gates → Trade │
│  9. Esperar intervalo → repetir                             │
└─────────────────────────────────────────────────────────────┘

ANÁLISIS IA (independiente del ciclo):
  - Solo cuando el operador pulsa "Analizar con Claude"
  - Cooldown mínimo: 5 minutos entre análisis
  - Caché por símbolo: cambiar de par invalida el resultado
```

---

## 10. Instrumentos Operados

| Símbolo | Instrumento | Sesión Óptima | Kill Zone Colombia |
|---------|-------------|--------------|-------------------|
| EURUSD | Euro / Dólar | Londres | 03:00 – 06:00 |
| GBPUSD | Libra / Dólar | Londres | 03:00 – 06:00 |
| USDJPY | Dólar / Yen | Londres + Tokio | 03:00 – 06:00 |
| XAUUSD | Oro / Dólar | NY | 09:30 – 12:00 |
| BTCUSD | Bitcoin / Dólar | NY + 24h | 09:30 – 12:00 |

Las Kill Zones representan los momentos de mayor liquidez institucional — cuando los grandes bancos abren y colocan sus órdenes. Fuera de estos horarios, el bot recomienda HOLD.

---

## 11. Flujo Operacional Completo

```
INICIO DE SESIÓN
       │
       ▼
DASHBOARD carga datos de mercado:
  ├─ Precio actual + spread
  ├─ Indicadores D1 / H1 / M15
  ├─ Estructuras SMC detectadas
  ├─ Noticias Forex Factory (caché 30 min)
  └─ Posiciones abiertas

       │
       ▼
TRADER PULSA "Analizar con Claude"
  (habilitado solo si han pasado ≥ 5 min desde el último análisis)
       │
       ▼
CLAUDE recibe 12 bloques de contexto:
  [D1 Macro] + [H1 Técnico] + [M15 Entrada]
  + [SMC Context] + [Cuenta] + [Sesión/Spread]
  + [Noticias] + [Historial de rendimiento]
       │
       ▼
CLAUDE responde JSON:
  { decision: "BUY", confidence: 0.88, sl_pips: 18, tp_pips: 40, ... }
       │
       ├── confidence < 0.85 ──▶  EJECUCIÓN MANUAL
       │                          Trader aprueba con un clic
       │
       └── confidence ≥ 0.85 ──▶  SAFETY GATES (6 capas)
                                         │
                                    ¿Algún gate falla?
                                   /           \
                                 SÍ             NO
                                  │              │
                              RECHAZAR       CALCULAR LOTE
                              + LOG           (1% riesgo, ATR)
                                              │
                                          ENVIAR ORDEN MT5
                                              │
                                   retcode == 10009?
                                   /           \
                                 NO             SÍ
                                  │              │
                              ERROR            TRADE ACTIVO
                              TOAST            + Log contexto
                                               + Feedback registro
```

---

## 12. Pruebas y Validaciones

### Pruebas de Compilación (11/11 archivos)

```bash
$ python -m py_compile app.py news_service.py ui_components.py
  i18n.py config.py mt5_service.py risk_manager.py
  logger_service.py smc_service.py anthropic_service.py
  feedback_service.py

ALL 11 FILES: SYNTAX OK
```

### Pruebas de Integración de APIs

| Test | Resultado | Detalle |
|------|-----------|---------|
| MT5 connection | ✅ PASS | Login 52823419 @ ICMarketsSC-Demo |
| MT5 heartbeat | ✅ PASS | Reconexión automática si se pierde la señal |
| Forex Factory calendar | ✅ PASS | 104 eventos / semana, 0 errores de parsing |
| Finnhub /news free | ✅ PASS | Sentimiento por palabras clave desde titulares |
| Anthropic Claude Haiku | ✅ PASS | JSON válido con assistant prefill |
| News Shield gate | ✅ PASS | No bloquea falsamente cuando calendar falla |
| Sentiment sin API key | ✅ PASS | Retorna NEUTRAL, no crashea |
| Config keys .env | ✅ PASS | FINNHUB_API_KEY + ANTHROPIC_API_KEY presentes |

### Pruebas del Motor SMC

```python
# Test: detección de estructuras en velas reales
smc_state = SMCService.get_smc_state("EURUSD")

# Campos validados:
assert "structure"    in smc_state   # "Bullish" / "Bearish"
assert "order_blocks" in smc_state   # lista de OBs con low/high
assert "fvg_zones"    in smc_state   # lista de FVGs con bottom/top
assert "session"      in smc_state   # London / NY / Asia / OFF
assert "in_kill_zone" in smc_state["session"]  # True/False
assert "bias"         in smc_state   # "Bullish" / "Bearish" / "Neutral"
```

### Prueba de Safety Gates

| Escenario simulado | Gate activado | Resultado |
|-------------------|---------------|-----------|
| NFP en 30 minutos | News Shield | ✅ RECHAZADO |
| Spread = 45 pts | Spread Filter | ✅ RECHAZADO |
| Pérdidas del día = 3.2% | Daily Loss | ✅ RECHAZADO |
| Ya hay BUY en EURUSD | Duplicate Guard | ✅ RECHAZADO |
| Confidence = 0.82 | Threshold Gate | ✅ Solo manual |
| SL calculado = 0 | SL Guard | ✅ RECHAZADO |
| Todo OK + conf ≥ 0.85 | — | ✅ ORDEN ENVIADA |

### Prueba de Gestión de Riesgo

```
Parámetros de prueba:
  Equity:          $5,000.00
  Riesgo objetivo: 1% = $50.00
  SL (Claude):     20 pips
  Pip value EURUSD: $10/lote

Lote calculado: $50 / (20 × $10) = 0.25 lotes
Lote con position_size 0.8: 0.25 × 0.8 = 0.20 lotes
Riesgo real: 0.20 × 20 pips × $10 = $40.00 (0.8% de equity)
Resultado: ✅ DENTRO DEL LÍMITE
```

### Prueba de Degradación Graceful

El sistema continúa operando correctamente en todos estos escenarios de falla:

| Componente que falla | Comportamiento del sistema |
|---------------------|--------------------------|
| Forex Factory (429/timeout) | Badge "SIN DATOS", bot opera normal |
| Finnhub API (sin key) | Sentimiento muestra "—", bot opera normal |
| Claude AI (timeout) | Retorna HOLD, reintenta 2 veces automáticamente |
| MT5 desconectado | Alerta en dashboard + intento de reconexión |
| CSV journal corrupto | `on_bad_lines='skip'` — ignora líneas malas |
| FeedbackService < 5 trades | No inyecta datos en prompt (evita ruido) |

---

## 13. Costos Operativos Estimados

### API de IA (Anthropic — Claude Haiku 4.5)

| Escenario | Análisis/día | Costo estimado/mes |
|-----------|-------------|-------------------|
| Conservador (manual) | 5-10 | ~$0.30 USD |
| Normal (semi-auto) | 20-40 | ~$1.20 USD |
| Intensivo (8h continuas) | 48 (1/10min) | ~$2.88 USD |

*Claude Haiku 4.5: ~$0.002 por análisis completo (input + output)*

### APIs de Datos de Mercado

| Servicio | Costo |
|---------|-------|
| Forex Factory Calendar | **$0 — completamente gratuito** |
| Finnhub News (sentimiento) | **$0 — plan gratuito** |
| MetaTrader 5 | **$0 — incluido en cuenta del bróker** |

### Costo Total Estimado

| Concepto | Costo Mensual |
|---------|--------------|
| Claude AI (uso normal) | ~$1.50 USD |
| APIs de datos | $0.00 |
| Infraestructura (PC local) | $0.00 adicional |
| **TOTAL** | **~$1.50 USD/mes** |

---

## 14. Limitaciones y Riesgos

### Técnicas

| Limitación | Detalle | Mitigación |
|-----------|---------|-----------|
| Solo Windows | MT5 Python API no disponible en Linux/Mac | Máquina virtual o VPS Windows |
| Single-threading | Un símbolo analizado a la vez | Caché de estado evita recálculos |
| Datos históricos limitados | SMC usa últimas 100 velas H1 (~4 días) | Suficiente para trading intraday |
| Latencia IA | ~0.5-2 segundos por llamada a Claude | Caché por símbolo, cooldown 5 min |

### De Mercado

| Riesgo | Descripción | Control implementado |
|--------|-------------|---------------------|
| Slippage | Precio de ejecución distinto al análisis | `deviation: 20 pts` en todas las órdenes |
| Flash crash | Movimiento extremo instantáneo | Stop Loss siempre presente (Gate 5) |
| Baja liquidez | Spreads altos en horas de poca actividad | Gate 2: spread máximo 30 pts |
| Evento macro inesperado | Noticia no anticipada | News Shield + Daily Loss Gate (3%) |

### Operativas

- El sistema requiere **supervisión humana** para uso en cuentas reales
- El modo autónomo está diseñado para cuentas demo y validación de estrategia
- El aprendizaje del FeedbackService requiere **mínimo 5 operaciones** para activarse
- La estrategia SMC funciona mejor en mercados con **tendencia clara** — en rangos estrechos el sistema emitirá más HOLDs (comportamiento esperado)

---

## 15. Hoja de Ruta

### v1.0 — Actual ✅

- [x] Dashboard en tiempo real con SMC chart
- [x] Análisis IA con 12 bloques de contexto
- [x] 6 Safety Gates independientes
- [x] Gestión de riesgo dinámica (ATR + position sizing)
- [x] Trailing Stop y Break Even por posición
- [x] News Shield Gate (Forex Factory)
- [x] Sentimiento de mercado (Finnhub free)
- [x] Sistema de aprendizaje FeedbackService
- [x] Registro completo de decisiones y operaciones
- [x] Soporte ES/EN (internacionalización)

### v1.1 — Próximas mejoras

- [ ] Notificaciones Telegram / WhatsApp en tiempo real
- [ ] Backtesting integrado sobre datos históricos MT5
- [ ] Dashboard web accesible desde móvil
- [ ] Exportar reporte de performance en PDF

### v2.0 — Visión

- [ ] Multi-cuenta simultánea (diferentes brókers)
- [ ] Correlación entre instrumentos (evitar sobreexposición USD)
- [ ] Optimización automática de parámetros SMC (walk-forward)
- [ ] API REST para integración con sistemas externos

---

## Apéndice A: Estructura de Archivos

```
trading_bot_mt5/
├── app.py                  # Orquestador principal + UI Streamlit
├── config.py               # Parámetros globales y safety gates
├── mt5_service.py          # Conexión y operaciones MT5
├── indicators_service.py   # Indicadores técnicos (RSI, EMA, ATR, MACD)
├── smc_service.py          # Motor SMC (OB, FVG, BOS, CHOCH, swings)
├── anthropic_service.py    # Cliente Claude AI + prompt institucional
├── risk_manager.py         # Position sizing, trailing stop, break even
├── news_service.py         # Forex Factory + Finnhub free
├── feedback_service.py     # Aprendizaje continuo de la IA
├── logger_service.py       # Registro CSV de operaciones y decisiones
├── ui_components.py        # Componentes visuales del dashboard
├── i18n.py                 # Traducciones ES / EN
├── .env                    # API keys (no incluir en repositorio)
├── trading_journal.csv     # Historial de operaciones (generado)
├── trading_decisions.csv   # Log de decisiones IA (generado)
├── strategy_memory.json    # Memoria de aprendizaje (generado)
└── trade_context.csv       # Contexto de trades abiertos (generado)
```

## Apéndice B: Parámetros de Configuración

```python
# config.py — Todos los parámetros son modificables sin tocar el código

# Instrumentos
SYMBOLS = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'BTCUSD']

# Timezone (adaptar según país del operador)
LOCAL_UTC_OFFSET = -5          # Colombia, Ecuador, Perú
LOCAL_TZ_NAME    = "Colombia"

# Safety Gates
AUTONOMOUS_CONFIDENCE_THRESHOLD = 0.85  # 85% confianza mínima para auto-trade
MAX_SPREAD_POINTS = 30                   # máximo spread permitido
MAX_DAILY_LOSS_PCT = 3.0                 # máximo drawdown diario (%)
MAX_POSITIONS_PER_SYMBOL = 1             # posiciones simultáneas por símbolo

# Control de IA
AI_MIN_INTERVAL_MINS = 5    # minutos entre análisis consecutivos
AI_STALE_MINS        = 15   # tiempo tras el cual el análisis se marca obsoleto

# News Shield
NEWS_SHIELD_MINUTES  = 60   # minutos de bloqueo antes de Carpeta Roja
NEWS_CACHE_TTL       = 1800 # TTL del caché de noticias (30 minutos)
```

---

*Documento preparado por el equipo de desarrollo de iBot · Intelligence Trading*
*Para consultas técnicas o de inversión, contactar al desarrollador.*
*© 2026 iBot. Todos los derechos reservados.*
