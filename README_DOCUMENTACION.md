# Documentación Técnica — iBot · Intelligence Trading

**Versión:** 1.0
**Fecha:** 03 de Abril de 2026
**Estado:** Sistema Validado y Operacional

---

## Documentos Disponibles

Este proyecto incluye **4 documentos técnicos detallados** para entender completamente cómo funciona el sistema:

### 1. DOCUMENTO_TECNICO_IBOT.md — COMENZAR AQUÍ
**Propósito:** Resumen ejecutivo para inversionistas y stakeholders

**Secciones principales:**
- Resumen ejecutivo (propuesta de valor)
- Arquitectura general del sistema
- Motor SMC (Smart Money Concepts)
- Inteligencia Artificial (Claude Haiku)
- Gestión de riesgo
- Sistema de seguridad (6 Safety Gates)
- Análisis fundamental (News Shield)
- Aprendizaje continuo (FeedbackService)
- Pruebas y validaciones
- Costos operativos (~$1.50 USD/mes)
- Limitaciones y riesgos

**Público objetivo:** Inversionistas, C-level, auditores

---

### 2. FLUJO_ANALISIS_IA_DETALLADO.md — ENTENDER EL PROCESO
**Propósito:** Explicación línea por línea de cada validación

**Secciones principales:**
- Los 12 bloques de datos que se envían a Claude
- Cómo se valida cada bloque
- Técnica de prefill para forzar JSON
- Validaciones de la respuesta Claude
- Las 6 Safety Gates en detalle
- Test de validación en 4 escenarios críticos
- 11 puntos de mejora identificados

**Público objetivo:** Desarrolladores, traders técnicos

---

### 3. EJEMPLOS_DATOS_ENVIADOS_A_CLAUDE.md — VER CASOS REALES
**Propósito:** 6 ejemplos completos con datos exactos

**Incluye:**
- Ejemplo 1: EURUSD Kill Zone (BUY ejecutado)
- Ejemplo 2: XAUUSD neutral (HOLD porque sin estructura)
- Ejemplo 3: GBPUSD evento BoE (NEWS SHIELD bloquea)
- Ejemplo 4: USDJPY spread alto
- Ejemplo 5: BTCUSD pérdidas cercanas a límite
- Ejemplo 6: Validación de datos inválidos

Cada ejemplo: contexto + prompt + respuesta Claude + resultado

**Público objetivo:** Traders, product managers, QA

---

### 4. DIAGRAMA_FLUJO_VISUAL.txt — VISIÓN GENERAL
**Propósito:** Diagramas ASCII del flujo completo

**Incluye:**
- Diagrama principal: dashboard → orden MT5
- Escenarios de rechazo
- Validaciones pre-Claude
- Árbol de decisión

**Público objetivo:** Todos (visual y fácil de seguir)

---

## Cómo Usar Esta Documentación

### INVERSOR/STAKEHOLDER (30 minutos)
1. DOCUMENTO_TECNICO_IBOT.md (15 min)
2. Sección 12: Pruebas (3 min)
3. Sección 13: Costos (2 min)

### TRADER/OPERADOR (25 minutos)
1. DIAGRAMA_FLUJO_VISUAL.txt (5 min)
2. EJEMPLOS_DATOS_ENVIADOS_A_CLAUDE.md ejemplos 1-3 (15 min)
3. FLUJO_ANALISIS_IA_DETALLADO.md sección mejoras (5 min)

### DESARROLLADOR/AUDITOR (60 minutos)
1. FLUJO_ANALISIS_IA_DETALLADO.md completo (30 min)
2. EJEMPLOS_DATOS_ENVIADOS_A_CLAUDE.md todos (25 min)
3. Puntos de mejora en FLUJO_ANALISIS (10 min)
4. DIAGRAMA_FLUJO_VISUAL.txt contexto (5 min)

### PRODUCT MANAGER (30 minutos)
1. DOCUMENTO_TECNICO_IBOT.md secciones 1-8 (15 min)
2. DIAGRAMA_FLUJO_VISUAL.txt (5 min)
3. Hoja de ruta y limitaciones (10 min)

---

## Resumen Ultra-Rápido (2 Minutos)

```
CUANDO PRESIONA "ANALIZAR":

1. Recopila 12 bloques de datos
2. Valida que datos sean lógicos
3. Construye prompt de ~2,500 caracteres
4. Envía a Claude Haiku (fuerza JSON)
5. Recibe: decision, confidence, SL, TP, RR
6. Si decision=HOLD → fin
7. Si confidence<0.85 → solo manual
8. Si confidence≥0.85 → evalúa 6 Safety Gates:
   • Gate 1: ¿Carpeta Roja en 60 min?
   • Gate 2: ¿Spread > 30 pts?
   • Gate 3: ¿Pérdidas + riesgo > 3%?
   • Gate 4: ¿Ya hay posición?
   • Gate 5: ¿SL > 0?
   • Gate 6: (confidence check)
9. Si pasa todos → enviar a MT5
10. Log en CSV + actualizar dashboard

TIEMPO: < 3 segundos
```

---

## Validaciones Clave

| Etapa | Validación | Si Falla |
|-------|-----------|----------|
| Pre-Claude | EMA≠NaN, RSI∈[0,100], spread normal | ERROR+STOP |
| Claude | decision∈{BUY,SELL,HOLD}, confidence∈[0,1] | HOLD |
| Gate 1 | ¿Carpeta Roja? | RECHAZAR |
| Gate 2 | ¿Spread>30? | RECHAZAR |
| Gate 3 | ¿Pérdidas+riesgo>3%? | RECHAZAR |
| Gate 4 | ¿Ya hay posición? | RECHAZAR |
| Gate 5 | ¿SL>0? | RECHAZAR |

---

## Estado de Validación

```
✅ Sintaxis (11/11 archivos)
✅ MT5 (conexión, órdenes, posiciones)
✅ Claude API (JSON, retries)
✅ Forex Factory (104 eventos/semana)
✅ Finnhub News (palabras clave)
✅ 6 Safety Gates
✅ FeedbackService (aprendizaje)
✅ Degradación graceful
✅ i18n (ES/EN)
✅ Logging CSV

COSTO: ~$1.50 USD/mes total
```

---

## Preguntas Frecuentes

### ¿Qué previene que Claude envíe datos inválidos?

Dos capas:
1. Pre-Claude: validar EMA, RSI, ATR, spread, equity
2. Post-Claude: validar JSON, valores en rango

Si falla cualquiera → NO se envía a MT5

### ¿Cómo aprende?

FeedbackService guarda contexto + resultados. Calcula:
- Win rate por setup (CONFIRMED=75%, AGGRESSIVE=60%)
- Win rate por sesión (London=72%, NY=55%)
- Win rate por símbolo

Inyecta notas a Claude: "CONFIRMED: +33% mejor que promedio"

### ¿Qué si Claude se desconecta?

Reintenta 2 veces. Si falla:
- Muestra error
- Emite HOLD automático
- No envía orden

### ¿Por qué News Shield es crítico?

Eventos macro (Fed, NFP, BoE) generan volatilidad extrema que análisis técnico no predice. Bloquea antes+después de evento.

---

## Próximos Pasos

1. **Operadores:** EJEMPLOS_DATOS_ENVIADOS_A_CLAUDE.md
2. **Desarrolladores:** FLUJO_ANALISIS_IA_DETALLADO.md + puntos mejora
3. **Inversionistas:** DOCUMENTO_TECNICO_IBOT.md completo
4. **Todos:** DIAGRAMA_FLUJO_VISUAL.txt como referencia

---

*© 2026 iBot · Intelligence Trading*
