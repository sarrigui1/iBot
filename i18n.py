"""
i18n.py — Internacionalización del Trading Bot MT5.
Idiomas soportados: Español (es) | English (en)

Uso:
    from i18n import get_translations
    t = get_translations("es")   # o "en"
    st.write(t["open_positions"])
"""

TRANSLATIONS = {
    # ------------------------------------------------------------------ ESPAÑOL
    "es": {
        # App / Branding
        "page_title":          "iBot · Intelligence Trading",
        "app_brand":           "iBot",
        "app_tagline":         "Intelligence Trading",
        "mt5_error":           "❌ Error MT5",

        # Sidebar — operativa
        "trading_ops":         "🕹️ Operativa",
        "asset":               "Activo",
        "lot":                 "Lote",
        "sl_pips":             "SL (pips)",
        "tp_pips":             "TP (pips)",

        # Sidebar — configuración
        "settings":            "⚙️ Configuración",
        "auto_refresh":        "Refresco automático (seg)",
        "enable_ai":           "Activar Análisis IA",
        "autonomous_mode":     "Modo Autónomo",
        "autonomous_help":     "Si confianza ≥ 85% el bot ejecuta la orden sin confirmación manual.",
        "language":            "Idioma / Language",

        # Pestañas
        "tab_dashboard":       "📊 Dashboard",
        "tab_journal":         "📖 Diario",

        # Métricas de cuenta
        "equity":              "Equity",
        "balance":             "Balance",
        "total_profit":        "Profit Total",

        # Análisis técnico
        "technical_analysis":  "🔍 Análisis Técnico (H1)",
        "calculating":         "Calculando indicadores...",
        "rsi":                 "RSI (14)",
        "overbought":          "SOBRECOMPRA",
        "oversold":            "SOBREVENTA",
        "neutral":             "NEUTRAL",
        "ema_trend":           "Tendencia EMA",
        "bullish_trend":       "ALCISTA",
        "bearish_trend":       "BAJISTA",
        "volatility":          "ATR (Volatilidad)",
        "close_price":         "Precio Cierre",
        "d1_macro":            "D1 Macro",
        "m15_entry":           "M15 Entrada",
        "bullish_momentum":    "ALCISTA",
        "bearish_momentum":    "BAJISTA",

        # Panel IA
        "ai_verdict":          "🤖 Veredicto de Claude AI",
        "waiting":             "Esperando análisis del agente...",
        "reasoning_label":     "Razonamiento",
        "logic_path_label":    "Lógica paso a paso",
        "confidence":          "Confianza",
        "rr_label":            "R:R",
        "analyze_btn":         "🧠 Analizar con Claude",
        "analyzing_spinner":   "🧠 Analizando con Claude (multi-TF)...",
        "ai_disabled":         "IA Desactivada.",
        "press_analyze":       "Pulsa 'Analizar con Claude' para obtener un veredicto.",
        "ai_error":            "Error IA",

        # Modo Autónomo
        "auto_banner":         "🤖 **MODO AUTÓNOMO ACTIVO**",
        "auto_executing":      "Ejecutando",
        "auto_lots":           "lotes · SL",
        "auto_pips":           "pips",
        "execute_manual":      "Ejecutar {decision} — {lot} lotes (manual)",

        # Posiciones
        "open_positions":      "📋 Posiciones Abiertas",
        "no_positions":        "Sin posiciones abiertas.",
        "panic_btn":           "🔥 PÁNICO",
        "panic_confirm":       "⚠️ ¿Cerrar TODAS las posiciones?",
        "order_error":         "Error orden",
        "pos_col_ticket":      "Ticket",
        "pos_col_symbol":      "Símbolo",
        "pos_col_type":        "Tipo",
        "pos_col_vol":         "Lote",
        "pos_col_open":        "Apertura",
        "pos_col_sl":          "SL",
        "pos_col_tp":          "TP",
        "pos_col_pnl":         "P&L",
        "close_btn":           "✕ Cerrar",
        "trail_btn":           "⟳ Trail SL",
        "trail_atr_label":     "ATR ×",
        "trail_atr_help":      "Multiplicador ATR para el trailing stop (ej. 1.5 = 1.5 × ATR)",
        "trail_ok":            "✅ Trail SL → {price}",
        "trail_no_move":       "ℹ️ SL ya en nivel óptimo",
        "trail_error":         "❌ Error Trail SL: {err}",
        "pos_closed_ok":       "✅ Posición {ticket} cerrada",
        "pos_closed_err":      "❌ Error cerrando {ticket}: {err}",
        "be_btn":              "BE",
        "be_ok":               "✅ Break Even → {price}",
        "be_not_ready":        "ℹ️ Precio no ha avanzado suficiente para BE",

        # Safety gates
        "auto_blocked":        "Operación bloqueada",
        "reject_spread":       "Spread {spread} pts > máximo {max} pts",
        "reject_daily_loss":   "Límite pérdida diaria {pct}% alcanzado",
        "reject_duplicate":    "Ya hay posición {dir} abierta en {sym}",

        # Q1 – guard handle_trade
        "order_no_response":   "MT5 no respondió (res=None) — verifica conexión",

        # Q2 – close_all parcial
        "panic_partial_error": "⚠️ No se pudieron cerrar los tickets: {tickets}",

        # Q3 – guard SL=0
        "error_no_sl":         "🚫 SL = 0 — operación bloqueada. La IA no definió un Stop Loss válido.",

        # Q5 – heartbeat MT5
        "mt5_disconnected":    "⚠️ MT5 desconectado — intentando reconectar...",
        "mt5_reconnected":     "✅ MT5 reconectado",
        "mt5_conn_failed":     "❌ No se pudo reconectar a MT5. Revisa la plataforma.",

        # Q4/Q7/Q8 – análisis AI
        "analysis_age":        "Análisis de hace {n} min",
        "analysis_stale":      "⚠️ Análisis de hace {n} min — considera re-analizar",
        "analysis_cooldown":   "Próximo análisis disponible en {n} min",
        "ai_min_interval":     "Intervalo mínimo entre análisis (min)",

        # Q6 – semáforo
        "sem_title":           "📊 Estado del Mercado",
        "sem_market":          "Mercado",
        "sem_opportunity":     "Oportunidad",
        "sem_risk":            "Riesgo Hoy",
        "sem_green_mkt":       "FAVORABLE",
        "sem_yellow_mkt":      "MIXTO",
        "sem_red_mkt":         "SIN DIRECCIÓN",
        "sem_green_opp":       "LISTA",
        "sem_yellow_opp":      "EN ESPERA",
        "sem_red_opp":         "SIN SETUP",
        "sem_green_risk":      "BAJO",
        "sem_yellow_risk":     "MODERADO",
        "sem_red_risk":        "ALTO",
        "sem_limit_reached":   "LÍMITE ALCANZADO",
        "sem_detail_mkt_g":    "Tendencia alineada D1+H1",
        "sem_detail_mkt_y":    "Tendencias en conflicto",
        "sem_detail_mkt_r":    "Estructura sin dirección clara",
        "sem_detail_opp_g":    "Setup confirmado en horario óptimo",
        "sem_detail_opp_y":    "Esperar mejor punto de entrada",
        "sem_detail_opp_r":    "No hay condiciones para operar",
        "sem_detail_risk_g":   "{losses} pérdidas hoy · Spread OK",
        "sem_detail_risk_y":   "{losses} pérdidas hoy · Revisar condiciones",
        "sem_detail_risk_r":   "Límite diario {pct}% cerca o alcanzado",

        # Diario
        "equity_curve":        "📈 Equity Curve",
        "full_history":        "📋 Historial Completo",
        "pnl_total":           "P&L Total",
        "win_rate":            "Win Rate",
        "winning_trades":      "Trades Ganados",
        "losing_trades":       "Trades Perdidos",

        # Registro actividad
        "activity_log":        "📝 Registro de Actividad",
        "cycle_started":       "🔄 Ciclo de actualización iniciado.",
        "connected_to":        "📡 Conectado a MT5. Activo:",
        "ai_active_log":       "🧠 IA activa. Threshold autónomo:",
        "ai_idle_log":         "💤 IA en reposo.",
        "next_refresh":        "Próximo refresco en {n}s",

        # Toasts
        "toast_auto":          "🤖 AUTO {action} en {sym} — {lot} lotes",
        "toast_manual":        "✅ {action} en {sym} OK",
        "toast_panic":         "⚠️ POSICIONES CERRADAS",

        # Reloj y sesiones
        "clock_title":         "🕐 Horas & Sesiones",
        "clock_broker":        "Broker",
        "clock_utc":           "UTC",
        "clock_col":           "Colombia",
        "session_title":       "Sesiones de Mercado",
        "session_asia":        "Asia",
        "session_london":      "Londres",
        "session_ny":          "Nueva York",
        "kz_title":            "Kill Zones",
        "kz_london":           "KZ Londres",
        "kz_ny":               "KZ Nueva York",
        "status_active":       "ACTIVA",
        "status_inactive":     "INACTIVA",
        "kz_active":           "⚡ ACTIVA",
        "kz_inactive":         "INACTIVA",

        # Instrucción de idioma para la IA
        "ai_lang_instruction": (
            "IMPORTANT: Write the 'logic_path' and 'reasoning' fields in Spanish (español)."
        ),

        # SMC Panel
        "smc_tab":          "🎯 SMC",
        "smc_title":        "🎯 Análisis Smart Money (H1)",
        "smc_structure":    "Estructura de Mercado",
        "smc_session":      "Sesión",
        "smc_kill_zone":    "KILL ZONE ACTIVA",
        "smc_off_zone":     "Fuera de Kill Zone",
        "smc_bias":         "Bias SMC",
        "smc_bos":          "BOS (Break of Structure)",
        "smc_choch":        "CHOCH (Cambio de Carácter)",
        "smc_none":         "Ninguno",
        "smc_obs":          "Order Blocks Activos",
        "smc_fvg":          "Fair Value Gaps",
        "smc_eqh":          "Equal Highs (Liquidez Buy-Side)",
        "smc_eql":          "Equal Lows (Liquidez Sell-Side)",
        "smc_pdh":          "PDH (Máximo Día Anterior)",
        "smc_pdl":          "PDL (Mínimo Día Anterior)",
        "smc_pwh":          "PWH (Máximo Semana Anterior)",
        "smc_pwl":          "PWL (Mínimo Semana Anterior)",
        "smc_setup":        "Setup Detectado",
        "smc_details":      "Detalles del Setup",
        "smc_no_data":      "Sin datos SMC disponibles.",
        "smc_setup_colors": {
            "CONFIRMED":  "#28a745",
            "AGGRESSIVE": "#ffc107",
            "WAIT":       "#6c757d",
            "NO_TRADE":   "#dc3545",
        },
    },

    # ------------------------------------------------------------------ ENGLISH
    "en": {
        # App / Branding
        "page_title":          "iBot · Intelligence Trading",
        "app_brand":           "iBot",
        "app_tagline":         "Intelligence Trading",
        "mt5_error":           "❌ MT5 Error",

        # Sidebar — trading
        "trading_ops":         "🕹️ Trading",
        "asset":               "Asset",
        "lot":                 "Lot Size",
        "sl_pips":             "SL (pips)",
        "tp_pips":             "TP (pips)",

        # Sidebar — settings
        "settings":            "⚙️ Settings",
        "auto_refresh":        "Auto Refresh (sec)",
        "enable_ai":           "Enable AI Analysis",
        "autonomous_mode":     "Autonomous Mode",
        "autonomous_help":     "If confidence ≥ 85% the bot executes the order without manual confirmation.",
        "language":            "Language / Idioma",

        # Tabs
        "tab_dashboard":       "📊 Dashboard",
        "tab_journal":         "📖 Journal",

        # Account metrics
        "equity":              "Equity",
        "balance":             "Balance",
        "total_profit":        "Total Profit",

        # Technical analysis
        "technical_analysis":  "🔍 Technical Analysis (H1)",
        "calculating":         "Calculating indicators...",
        "rsi":                 "RSI (14)",
        "overbought":          "OVERBOUGHT",
        "oversold":            "OVERSOLD",
        "neutral":             "NEUTRAL",
        "ema_trend":           "EMA Trend",
        "bullish_trend":       "BULLISH",
        "bearish_trend":       "BEARISH",
        "volatility":          "ATR (Volatility)",
        "close_price":         "Close Price",
        "d1_macro":            "D1 Macro",
        "m15_entry":           "M15 Entry",
        "bullish_momentum":    "BULLISH",
        "bearish_momentum":    "BEARISH",

        # AI panel
        "ai_verdict":          "🤖 Claude AI Verdict",
        "waiting":             "Waiting for agent analysis...",
        "reasoning_label":     "Reasoning",
        "logic_path_label":    "Step-by-step logic",
        "confidence":          "Confidence",
        "rr_label":            "R:R",
        "analyze_btn":         "🧠 Analyze with Claude",
        "analyzing_spinner":   "🧠 Analyzing with Claude (multi-TF)...",
        "ai_disabled":         "AI Disabled.",
        "press_analyze":       "Press 'Analyze with Claude' to get a verdict.",
        "ai_error":            "AI Error",

        # Autonomous mode
        "auto_banner":         "🤖 **AUTONOMOUS MODE ACTIVE**",
        "auto_executing":      "Executing",
        "auto_lots":           "lots · SL",
        "auto_pips":           "pips",
        "execute_manual":      "Execute {decision} — {lot} lots (manual)",

        # Positions
        "open_positions":      "📋 Open Positions",
        "no_positions":        "No open positions.",
        "panic_btn":           "🔥 PANIC",
        "panic_confirm":       "⚠️ Close ALL positions?",
        "order_error":         "Order error",
        "pos_col_ticket":      "Ticket",
        "pos_col_symbol":      "Symbol",
        "pos_col_type":        "Type",
        "pos_col_vol":         "Lot",
        "pos_col_open":        "Open",
        "pos_col_sl":          "SL",
        "pos_col_tp":          "TP",
        "pos_col_pnl":         "P&L",
        "close_btn":           "✕ Close",
        "trail_btn":           "⟳ Trail SL",
        "trail_atr_label":     "ATR ×",
        "trail_atr_help":      "ATR multiplier for trailing stop (e.g. 1.5 = 1.5 × ATR)",
        "trail_ok":            "✅ Trail SL → {price}",
        "trail_no_move":       "ℹ️ SL already at optimal level",
        "trail_error":         "❌ Trail SL error: {err}",
        "pos_closed_ok":       "✅ Position {ticket} closed",
        "pos_closed_err":      "❌ Error closing {ticket}: {err}",
        "be_btn":              "BE",
        "be_ok":               "✅ Break Even → {price}",
        "be_not_ready":        "ℹ️ Price hasn't moved enough for BE yet",

        # Safety gates
        "auto_blocked":        "Order blocked",
        "reject_spread":       "Spread {spread} pts > max {max} pts",
        "reject_daily_loss":   "Daily loss limit {pct}% reached",
        "reject_duplicate":    "Already has {dir} position open on {sym}",

        # Q1
        "order_no_response":   "MT5 did not respond (res=None) — check connection",

        # Q2
        "panic_partial_error": "⚠️ Could not close tickets: {tickets}",

        # Q3
        "error_no_sl":         "🚫 SL = 0 — order blocked. AI did not define a valid Stop Loss.",

        # Q5
        "mt5_disconnected":    "⚠️ MT5 disconnected — attempting reconnect...",
        "mt5_reconnected":     "✅ MT5 reconnected",
        "mt5_conn_failed":     "❌ Could not reconnect to MT5. Check the platform.",

        # Q4/Q7/Q8
        "analysis_age":        "Analysis from {n} min ago",
        "analysis_stale":      "⚠️ Analysis is {n} min old — consider re-analyzing",
        "analysis_cooldown":   "Next analysis available in {n} min",
        "ai_min_interval":     "Minimum interval between analyses (min)",

        # Q6
        "sem_title":           "📊 Market Status",
        "sem_market":          "Market",
        "sem_opportunity":     "Opportunity",
        "sem_risk":            "Risk Today",
        "sem_green_mkt":       "FAVORABLE",
        "sem_yellow_mkt":      "MIXED",
        "sem_red_mkt":         "NO DIRECTION",
        "sem_green_opp":       "READY",
        "sem_yellow_opp":      "WAITING",
        "sem_red_opp":         "NO SETUP",
        "sem_green_risk":      "LOW",
        "sem_yellow_risk":     "MODERATE",
        "sem_red_risk":        "HIGH",
        "sem_limit_reached":   "LIMIT REACHED",
        "sem_detail_mkt_g":    "D1+H1 trend aligned",
        "sem_detail_mkt_y":    "Conflicting timeframe trends",
        "sem_detail_mkt_r":    "No clear market structure",
        "sem_detail_opp_g":    "Confirmed setup in optimal session",
        "sem_detail_opp_y":    "Waiting for better entry point",
        "sem_detail_opp_r":    "No conditions to trade",
        "sem_detail_risk_g":   "{losses} losses today · Spread OK",
        "sem_detail_risk_y":   "{losses} losses today · Review conditions",
        "sem_detail_risk_r":   "Daily limit {pct}% near or reached",

        # Journal
        "equity_curve":        "📈 Equity Curve",
        "full_history":        "📋 Full History",
        "pnl_total":           "Total P&L",
        "win_rate":            "Win Rate",
        "winning_trades":      "Winning Trades",
        "losing_trades":       "Losing Trades",

        # Activity log
        "activity_log":        "📝 Activity Log",
        "cycle_started":       "🔄 Refresh cycle started.",
        "connected_to":        "📡 Connected to MT5. Asset:",
        "ai_active_log":       "🧠 AI active. Autonomous threshold:",
        "ai_idle_log":         "💤 AI idle.",
        "next_refresh":        "Next refresh in {n}s",

        # Toasts
        "toast_auto":          "🤖 AUTO {action} on {sym} — {lot} lots",
        "toast_manual":        "✅ {action} on {sym} OK",
        "toast_panic":         "⚠️ POSITIONS CLOSED",

        # Clock and sessions
        "clock_title":         "🕐 Times & Sessions",
        "clock_broker":        "Broker",
        "clock_utc":           "UTC",
        "clock_col":           "Colombia",
        "session_title":       "Market Sessions",
        "session_asia":        "Asia",
        "session_london":      "London",
        "session_ny":          "New York",
        "kz_title":            "Kill Zones",
        "kz_london":           "KZ London",
        "kz_ny":               "KZ New York",
        "status_active":       "ACTIVE",
        "status_inactive":     "INACTIVE",
        "kz_active":           "⚡ ACTIVE",
        "kz_inactive":         "INACTIVE",

        # Language instruction for the AI
        "ai_lang_instruction": (
            "IMPORTANT: Write the 'logic_path' and 'reasoning' fields in English."
        ),

        # SMC Panel
        "smc_tab":          "🎯 SMC",
        "smc_title":        "🎯 Smart Money Analysis (H1)",
        "smc_structure":    "Market Structure",
        "smc_session":      "Session",
        "smc_kill_zone":    "KILL ZONE ACTIVE",
        "smc_off_zone":     "Outside Kill Zone",
        "smc_bias":         "SMC Bias",
        "smc_bos":          "BOS (Break of Structure)",
        "smc_choch":        "CHOCH (Change of Character)",
        "smc_none":         "None",
        "smc_obs":          "Active Order Blocks",
        "smc_fvg":          "Fair Value Gaps",
        "smc_eqh":          "Equal Highs (Buy-Side Liquidity)",
        "smc_eql":          "Equal Lows (Sell-Side Liquidity)",
        "smc_pdh":          "PDH (Previous Day High)",
        "smc_pdl":          "PDL (Previous Day Low)",
        "smc_pwh":          "PWH (Previous Week High)",
        "smc_pwl":          "PWL (Previous Week Low)",
        "smc_setup":        "Detected Setup",
        "smc_details":      "Setup Details",
        "smc_no_data":      "No SMC data available.",
        "smc_setup_colors": {
            "CONFIRMED":  "#28a745",
            "AGGRESSIVE": "#ffc107",
            "WAIT":       "#6c757d",
            "NO_TRADE":   "#dc3545",
        },
    },
}


def get_translations(lang: str = "es") -> dict:
    """Retorna el diccionario de traducciones para el idioma dado."""
    return TRANSLATIONS.get(lang, TRANSLATIONS["es"])
