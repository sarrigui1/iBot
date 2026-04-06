import sys
import os
import streamlit as st
import MetaTrader5 as mt5
import pandas as pd
import time

# Agregar raíz y src del proyecto al path
_app_dir = os.path.dirname(os.path.abspath(__file__))  # src/
_root_dir = os.path.dirname(_app_dir)                  # raiz/
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

# ═══════════════════════════════════════════════════════════════════════════════
# FASE 0: CONFIGURACIÓN DE UI — st.set_page_config PRIMERO
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="iBot", page_icon="🤖", layout="wide")

# ═══════════════════════════════════════════════════════════════════════════════
# FASE 1: i18n — Inicializar traducciones antes de cualquier render
# ═══════════════════════════════════════════════════════════════════════════════
from i18n import get_translations

_lang_init = st.session_state.get("lang_selector", "es")
t = get_translations(_lang_init)

# Actualizar page_config con el título en el idioma correcto
st.set_page_config(page_title=t["page_title"], page_icon="🤖", layout="wide")

# ═══════════════════════════════════════════════════════════════════════════════
# FASE 2: INICIALIZAR DEBUG LOGGER y CARGAR CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════
from core.config_loader import ConfigLoader
from core.license_manager import LicenseManager
from debug_logger import DebugLogger

try:
    # Calcular ruta absoluta a config.ini
    _config_ini_path = os.path.join(_root_dir, 'config', 'config.ini')
    config = ConfigLoader(_config_ini_path)
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()
except ValueError as e:
    st.error(f"Error en config.ini: {e}")
    st.stop()

# Inicializar logger con la configuración
log_dir = os.path.join(_root_dir, 'data')
DebugLogger.initialize(debug_mode=config.debug_mode, log_dir=log_dir)
logger = DebugLogger()

logger.info("═" * 60)
logger.info("iBot Trading iniciado")
logger.info(f"Modo: {'DEBUG' if config.debug_mode else 'INFO'}")
logger.info(f"Zona horaria: {config.local_tz_name} (UTC{config.local_utc_offset:+d})")
logger.info(f"Símbolos: {', '.join(config.symbols)}")
logger.info("═" * 60)

# ═══════════════════════════════════════════════════════════════════════════════
# FASE 3: VALIDACIÓN DE LICENCIA
# ═══════════════════════════════════════════════════════════════════════════════
lic_mgr = LicenseManager(config)
is_valid, msg, was_cached, cached_date = lic_mgr.validate()

logger.info(f"Validación de licencia: {msg}")

if not is_valid:
    logger.error(f"Licencia inválida: {msg}")
    st.error(f"❌ Licencia inválida: {msg}")
    st.error("Por favor, verifica tu license_key en config.ini")
    st.stop()

if was_cached:
    logger.warning(f"Licencia no validada hoy (última validación exitosa: {cached_date})")

# ═══════════════════════════════════════════════════════════════════════════════
# FASE 4: IMPORTACIONES DIFERIDAS — Solo después de validar licencia
# (Los decoradores @st.cache_data/@st.cache_resource se registran aquí)
# ═══════════════════════════════════════════════════════════════════════════════
from mt5_service import MT5Service
from indicators_service import IndicatorsService
from anthropic_service import AnthropicService
from smc_service import SMCService
from risk_manager import RiskManager
from ui_components import (
    render_metrics,
    render_sidebar,
    render_sessions_clock,
    render_market_semaphore,
    render_news_marquee,
    render_news_panel,
    render_technical_analysis,
    render_mtf_badges,
    render_ai_decision,
    render_smc_chart,
    render_smc_panel,
)
from logger_service import LoggerService
from feedback_service import FeedbackService
from news_service import NewsService
from config import (
    SYMBOLS,
    SYMBOL_CURRENCIES,
    AUTONOMOUS_CONFIDENCE_THRESHOLD,
    MAX_SPREAD_POINTS,
    MAX_DAILY_LOSS_PCT,
    MAX_POSITIONS_PER_SYMBOL,
    AI_MIN_INTERVAL_MINS,
    NEWS_SHIELD_MINUTES,
    NEWS_CACHE_TTL,
    NEWS_SENTIMENT_CACHE,
)


@st.cache_resource
def get_services():
    return MT5Service(config), AnthropicService(config)


# Caché de noticias — TTL configurable para no ralentizar cada refresco
@st.cache_data(ttl=NEWS_CACHE_TTL)
def fetch_news_calendar(symbol: str) -> dict:
    """Cached: calendario económico del día."""
    currencies = SYMBOL_CURRENCIES.get(symbol, ["USD"])
    cal = NewsService.get_economic_calendar(currencies)
    # Adjuntar shield y noticias recientes dentro del mismo objeto cacheado
    cal["_shield"]       = NewsService.check_news_shield(cal, NEWS_SHIELD_MINUTES)
    cal["_recent_news"]  = NewsService.get_recent_news(symbol)
    return cal


@st.cache_data(ttl=NEWS_SENTIMENT_CACHE)
def fetch_news_sentiment(symbol: str) -> dict:
    """Cached: sentimiento de mercado."""
    return NewsService.get_market_sentiment(symbol)


service, ai_agent = get_services()
success, msg = service.connect()

if not success:
    st.error(f"{t['mt5_error']}: {msg}")
    st.stop()

# Q5 — Heartbeat MT5: verificar conexión en cada ciclo
if mt5.terminal_info() is None:
    st.warning(t["mt5_disconnected"])
    _recon_ok, _ = service.connect()
    if _recon_ok:
        st.success(t["mt5_reconnected"])
    else:
        st.error(t["mt5_conn_failed"])
        st.stop()

# ── Branding header ──────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">
        <span style="font-size:2rem;font-weight:900;
                     background:linear-gradient(90deg,#26a69a,#42a5f5);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            {t['app_brand']}
        </span>
        <span style="font-size:1rem;color:#aaa;letter-spacing:2px;text-transform:uppercase;">
            {t['app_tagline']}
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)


# --- FUNCIONES ---
def handle_trade(action, sym, lot, sl, tp, auto=False):
    # Q3 — bloquear si SL = 0 (riesgo ilimitado)
    if sl <= 0:
        st.error(t["error_no_sl"])
        return
    res = service.send_order(sym, action, lot, sl, tp)
    # Q1 — guard: MT5 puede devolver None en desconexión
    if res is None:
        st.error(t["order_no_response"])
        return
    if res.retcode == 10009:
        # Feedback — guardar contexto de apertura para aprendizaje posterior
        try:
            _fb_smc = st.session_state.get("last_smc_state", {})
            _fb_ai  = st.session_state.get("last_ai_res",    {})
            if _fb_ai:
                FeedbackService.log_trade_context(
                    ticket=res.order, symbol=sym, direction=action,
                    smc_state=_fb_smc, ai_res=_fb_ai,
                )
        except Exception:
            pass   # no bloquear el trade si falla el log de contexto
        if auto:
            st.toast(t["toast_auto"].format(action=action, sym=sym, lot=lot), icon="🚀")
        else:
            st.toast(t["toast_manual"].format(action=action, sym=sym), icon="🚀")
        time.sleep(1)
        st.rerun()
    else:
        st.error(f"{t['order_error']}: {res.comment}")


def close_all_positions():
    positions = service.get_positions()
    if not positions.empty:
        # Q2 — try/except individual: intentar cerrar TODAS aunque alguna falle
        failed = []
        for ticket in positions["ticket"]:
            try:
                res = service.close_position(int(ticket))
                if res is None or res.retcode != 10009:
                    failed.append(str(int(ticket)))
            except Exception as e:
                failed.append(f"{int(ticket)}({e})")
        if failed:
            st.error(t["panic_partial_error"].format(tickets=", ".join(failed)))
        FeedbackService.update_memory()   # actualizar aprendizaje
        st.toast(t["toast_panic"], icon="🔥")
        time.sleep(1)
        st.rerun()


# --- SIDEBAR ---
# render_sidebar devuelve (symbol, refresh, run_ai, autonomous_mode, lang)
selected_symbol, refresh_interval, run_ai, autonomous_mode, lang, ai_interval_mins = render_sidebar(
    SYMBOLS, handle_trade, t
)

# Recargar traducciones si el usuario cambió el idioma en esta misma ejecución
t = get_translations(lang)

# --- RELOJ Y SESIONES (sidebar) ---
with st.sidebar:
    st.divider()
    times = service.get_times()
    render_sessions_clock(times, t)


# --- CUERPO PRINCIPAL ---
tab_dash, tab_smc, tab_journal = st.tabs([
    t["tab_dashboard"], t["smc_tab"], t["tab_journal"]
])

with tab_dash:
    acc = service.get_account()
    render_metrics(acc, t)
    st.divider()

    mtf_state              = IndicatorsService.get_multi_timeframe_state(selected_symbol)
    smc_state              = SMCService.get_smc_state(selected_symbol)
    smc_df, smc_swings     = SMCService.get_chart_data(selected_symbol)
    h1_state  = mtf_state.get("h1", {})

    # Fetch noticias (cacheadas — no ralentizan el ciclo de refresco)
    news_data  = fetch_news_calendar(selected_symbol)
    sentiment  = fetch_news_sentiment(selected_symbol)
    shield     = news_data.get("_shield", {})

    # Marquee de noticias (antes del semáforo)
    render_news_marquee(news_data, sentiment, t)

    # Q6 — Semáforo (pre-calcular valores de riesgo para pasarlos como primitivos)
    _sem_history  = LoggerService.get_history()
    _sem_spread   = service.get_spread(selected_symbol)
    _sem_losses   = RiskManager.get_session_loss_count(_sem_history)
    _sem_spread_ok = RiskManager.is_spread_ok(_sem_spread, MAX_SPREAD_POINTS)
    _sem_daily_exc = RiskManager.is_daily_loss_limit_exceeded(
        _sem_history, acc.balance, MAX_DAILY_LOSS_PCT
    )
    render_market_semaphore(
        smc_state, mtf_state,
        _sem_losses, _sem_spread_ok, _sem_daily_exc, t,
    )
    st.divider()

    col_l, col_r = st.columns([1, 1])

    with col_l:
        render_technical_analysis(h1_state, t)
        render_mtf_badges(mtf_state.get("d1", {}), mtf_state.get("m15", {}), t)

    with col_r:
        if run_ai:
            cache_key  = f"ai_result_{selected_symbol}"
            auto_fired = f"auto_fired_{selected_symbol}"

            # Q8 — cooldown: deshabilitar botón si el análisis es reciente
            _last_ts   = st.session_state.get(f"ai_ts_{selected_symbol}", 0.0)
            _elapsed   = (time.time() - _last_ts) / 60   # minutos
            _can_analyze = _elapsed >= ai_interval_mins
            _btn_help  = (
                None if _can_analyze
                else t["analysis_cooldown"].format(n=max(1, int(ai_interval_mins - _elapsed)))
            )

            if st.button(t["analyze_btn"], width="stretch",
                         disabled=not _can_analyze, help=_btn_help):
                with st.spinner(t["analyzing_spinner"]):
                    try:
                        _history       = LoggerService.get_history()
                        _spread        = service.get_spread(selected_symbol)
                        _session_loss  = RiskManager.get_session_loss_count(_history)
                        # Feedback — construir bloque de rendimiento histórico
                        _cur_session   = (smc_state or {}).get("session", {}).get("session", "")
                        _feedback_blk  = FeedbackService.build_prompt_block(
                            symbol=selected_symbol, session=_cur_session
                        )
                        # Fundamental block — enriquece el contexto IA con noticias
                        _hdr   = t["fundamental_block_hdr"]
                        _lines = [f"{_hdr}:"]

                        # Sentimiento de mercado
                        if not sentiment.get("error"):
                            _lines.append(
                                f"  Sentiment: {sentiment.get('label','N/A')} "
                                f"(score={sentiment.get('score',0):.2f}, "
                                f"buzz={sentiment.get('buzz',0)})"
                            )

                        # Análisis interpretativo de noticias recientes
                        _recent_news = news_data.get("_recent_news", [])
                        if _recent_news and not sentiment.get("error"):
                            logger.debug(f"Analizando {len(_recent_news)} noticias para {selected_symbol}")
                            _news_analysis = ai_agent.analyze_news_sentiment(
                                selected_symbol, _recent_news, sentiment, lang=lang
                            )
                            _lines.append(f"  News Analysis: {_news_analysis}")

                        # Eventos económicos de alto impacto
                        _events = news_data.get("high_impact", [])
                        if _events:
                            for _ev in _events[:3]:
                                _lines.append(
                                    f"  Event: {_ev.get('event','?')} "
                                    f"[{_ev.get('currency','?')}] "
                                    f"in {_ev.get('mins_away','?')} min"
                                )
                        else:
                            _lines.append(f"  {t['news_no_events']}")

                        # News shield gate
                        if shield.get("blocking"):
                            _lines.append(
                                f"  NEWS SHIELD BLOCKING: {shield.get('event_name','?')} "
                                f"({shield.get('currency','?')}) in {shield.get('mins_away','?')} min"
                            )

                        _fundamental_blk = "\n".join(_lines)
                        ai_res = ai_agent.get_strategy_decision(
                            selected_symbol, mtf_state, acc,
                            lang=lang, smc_state=smc_state,
                            session_losses=_session_loss,
                            spread_pts=_spread,
                            feedback_block=_feedback_blk,
                            fundamental_block=_fundamental_blk,
                        )
                        # Q4 — timestamp + guardar para feedback de apertura
                        ai_res["_ts"] = time.time()
                        st.session_state[cache_key]                   = ai_res
                        st.session_state[f"ai_ts_{selected_symbol}"]  = ai_res["_ts"]
                        st.session_state["last_smc_state"]            = smc_state
                        st.session_state["last_ai_res"]               = ai_res
                        st.session_state[auto_fired]                  = False
                    except Exception as e:
                        st.error(f"{t['ai_error']}: {e}")

            if cache_key in st.session_state:
                ai_res     = st.session_state[cache_key]
                decision   = ai_res.get("decision",   "HOLD")
                confidence = ai_res.get("confidence", 0.0)

                render_ai_decision(ai_res, t)

                # ---- MODO AUTÓNOMO ----
                if (
                    autonomous_mode
                    and decision in ("BUY", "SELL")
                    and confidence >= AUTONOMOUS_CONFIDENCE_THRESHOLD
                    and not st.session_state.get(auto_fired, False)
                ):
                    # ── Safety gates ─────────────────────────────────────────
                    _history    = LoggerService.get_history()
                    _spread     = service.get_spread(selected_symbol)
                    _df_pos     = service.get_positions()
                    _reject     = None

                    if shield.get("blocking"):
                        _reject = t["news_reject_shield"].format(
                            event=shield.get("event_name", "?"),
                            cur=shield.get("currency", "?"),
                            n=shield.get("mins_away", "?"),
                        )
                    elif not RiskManager.is_spread_ok(_spread, MAX_SPREAD_POINTS):
                        _reject = t["reject_spread"].format(spread=_spread, max=MAX_SPREAD_POINTS)
                    elif RiskManager.is_daily_loss_limit_exceeded(
                        _history, acc.balance, MAX_DAILY_LOSS_PCT
                    ):
                        _reject = t["reject_daily_loss"].format(pct=MAX_DAILY_LOSS_PCT)
                    elif RiskManager.has_open_position(_df_pos, selected_symbol, decision):
                        _reject = t["reject_duplicate"].format(sym=selected_symbol, dir=decision)

                    if _reject:
                        st.error(f"🚫 {t['auto_blocked']}: {_reject}")
                        LoggerService.log_decision(
                            selected_symbol, decision, confidence,
                            ai_res.get("sl_pips", 0), ai_res.get("tp_pips", 0),
                            accepted=False, reject_reason=_reject,
                        )
                        st.session_state[auto_fired] = True  # no reintentar en este ciclo
                    else:
                        pip_val = service.get_pip_value_per_lot(selected_symbol)
                        lot = RiskManager.calculate_lot_size(
                            equity=acc.equity,
                            risk_pct=RiskManager.DEFAULT_RISK_PCT,
                            sl_pips=ai_res.get("sl_pips", 20),
                            pip_value_per_lot=pip_val,
                        )
                        lot = max(
                            RiskManager.MIN_LOT,
                            round(lot * float(ai_res.get("position_size", 1.0)), 2),
                        )
                        st.warning(
                            f"{t['auto_banner']} — {t['confidence']}: {confidence*100:.0f}% "
                            f"≥ {AUTONOMOUS_CONFIDENCE_THRESHOLD*100:.0f}%\n\n"
                            f"{t['auto_executing']} **{decision}** · {lot} {t['auto_lots']} "
                            f"{ai_res['sl_pips']} {t['auto_pips']}"
                        )
                        LoggerService.log_decision(
                            selected_symbol, decision, confidence,
                            ai_res.get("sl_pips", 0), ai_res.get("tp_pips", 0),
                            accepted=True,
                        )
                        st.session_state[auto_fired] = True
                        handle_trade(
                            decision, selected_symbol, lot,
                            ai_res["sl_pips"], ai_res["tp_pips"], auto=True,
                        )

                # ---- EJECUCIÓN MANUAL ----
                elif decision in ("BUY", "SELL") and (
                    not autonomous_mode
                    or confidence < AUTONOMOUS_CONFIDENCE_THRESHOLD
                ):
                    pip_val = service.get_pip_value_per_lot(selected_symbol)
                    lot = RiskManager.calculate_lot_size(
                        equity=acc.equity,
                        risk_pct=RiskManager.DEFAULT_RISK_PCT,
                        sl_pips=ai_res.get("sl_pips", 20),
                        pip_value_per_lot=pip_val,
                    )
                    btn_label = t["execute_manual"].format(decision=decision, lot=lot)
                    if st.button(btn_label, type="primary", width="stretch"):
                        handle_trade(
                            decision, selected_symbol, lot,
                            ai_res["sl_pips"], ai_res["tp_pips"],
                        )
            else:
                st.info(t["press_analyze"])
        else:
            st.info(t["ai_disabled"])

    st.divider()
    # ── Panel de Noticias (expandible) ──────────────────────────────────────
    with st.expander(t["news_calendar_title"], expanded=False):
        render_news_panel(news_data, sentiment, t)

    st.divider()
    # ── Título + Botón Pánico ────────────────────────────────────────────────
    ph1, ph2 = st.columns([7, 1])
    ph1.subheader(t["open_positions"])
    if ph2.button(t["panic_btn"], type="primary"):
        close_all_positions()

    df_pos = service.get_positions()
    if not df_pos.empty:
        # Configuración global del trailing stop
        atr_mult = st.number_input(
            t["trail_atr_label"],
            min_value=0.5, max_value=5.0, value=1.5, step=0.1,
            help=t["trail_atr_help"],
            key="trail_atr_mult",
        )

        # Encabezado de columnas
        h = st.columns([1, 1.5, 1, 1, 1.5, 1.5, 1.5, 1.5, 1, 1, 1])
        for lbl, col in zip(
            [t["pos_col_ticket"], t["pos_col_symbol"], t["pos_col_type"],
             t["pos_col_vol"], t["pos_col_open"], t["pos_col_sl"], t["pos_col_tp"],
             t["pos_col_pnl"], "", "", ""],
            h,
        ):
            col.markdown(f"**{lbl}**")

        # Filas por posición
        for _, row in df_pos.iterrows():
            ticket = int(row["ticket"])
            c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11 = st.columns(
                [1, 1.5, 1, 1, 1.5, 1.5, 1.5, 1.5, 1, 1, 1]
            )
            pnl_color = "#28a745" if row["profit"] >= 0 else "#dc3545"
            c1.caption(str(ticket))
            c2.caption(row["symbol"])
            c3.caption(row["type_name"])
            c4.caption(f"{row['volume']:.2f}")
            c5.caption(f"{row['price_open']:.5f}")
            c6.caption(f"{row['sl']:.5f}" if row["sl"] else "—")
            c7.caption(f"{row['tp']:.5f}" if row["tp"] else "—")
            c8.markdown(
                f'<span style="color:{pnl_color};font-weight:bold;">'
                f'${row["profit"]:,.2f}</span>',
                unsafe_allow_html=True,
            )

            if c9.button(t["close_btn"], key=f"close_{ticket}"):
                res = service.close_position(ticket)
                if res and res.retcode == 10009:
                    FeedbackService.update_memory()   # actualizar aprendizaje
                    st.toast(t["pos_closed_ok"].format(ticket=ticket), icon="✅")
                else:
                    err = res.comment if res else "?"
                    st.toast(t["pos_closed_err"].format(ticket=ticket, err=err), icon="❌")
                time.sleep(0.5)
                st.rerun()

            if c10.button(t["trail_btn"], key=f"trail_{ticket}"):
                atr = service.get_h1_atr(row["symbol"])
                if atr > 0:
                    should_move, new_sl = RiskManager.should_trail_stop(
                        current_price=row["price_current"],
                        current_sl=row["sl"],
                        action=row["type_name"],
                        atr=atr,
                        multiplier=float(atr_mult),
                    )
                    if should_move:
                        service.modify_sl(ticket, new_sl)
                        st.toast(t["trail_ok"].format(price=round(new_sl, 5)), icon="✅")
                    else:
                        st.toast(t["trail_no_move"], icon="ℹ️")
                else:
                    st.toast(t["trail_error"].format(err="ATR=0"), icon="❌")

            if c11.button(t["be_btn"], key=f"be_{ticket}"):
                atr = service.get_h1_atr(row["symbol"])
                if atr > 0:
                    should_be, be_price = RiskManager.should_break_even(
                        current_price=row["price_current"],
                        open_price=row["price_open"],
                        current_sl=row["sl"],
                        action=row["type_name"],
                        atr=atr,
                    )
                    if should_be:
                        service.modify_sl(ticket, be_price)
                        st.toast(t["be_ok"].format(price=round(be_price, 5)), icon="✅")
                    else:
                        st.toast(t["be_not_ready"], icon="ℹ️")
                else:
                    st.toast(t["trail_error"].format(err="ATR=0"), icon="❌")
    else:
        st.success(t["no_positions"])


# --- PESTAÑA SMC ---
with tab_smc:
    render_smc_chart(smc_df, smc_swings, smc_state, t)
    st.divider()
    render_smc_panel(smc_state, t)

# --- DIARIO + EQUITY CURVE ---
with tab_journal:
    history = LoggerService.get_history()

    if not history.empty:
        closed = history[history["accion"] == "CLOSE"].copy()
        closed["profit"] = pd.to_numeric(
            closed.get("profit", pd.Series(dtype=float)), errors="coerce"
        )
        closed = closed.dropna(subset=["profit"]).sort_values("fecha")

        if not closed.empty:
            st.subheader(t["equity_curve"])
            closed["equity_acumulado"] = closed["profit"].cumsum()
            curve_color = (
                "#28a745" if closed["equity_acumulado"].iloc[-1] >= 0 else "#dc3545"
            )
            st.line_chart(
                closed[["fecha", "equity_acumulado"]].set_index("fecha"),
                color=curve_color,
                width="stretch",
            )

            total_pnl    = closed["profit"].sum()
            win_trades   = (closed["profit"] > 0).sum()
            loss_trades  = (closed["profit"] <= 0).sum()
            total_trades = len(closed)
            win_rate     = win_trades / total_trades * 100 if total_trades > 0 else 0

            c1, c2, c3, c4 = st.columns(4)
            c1.metric(t["pnl_total"],      f"${total_pnl:,.2f}", delta=f"${total_pnl:,.2f}")
            c2.metric(t["win_rate"],        f"{win_rate:.1f}%")
            c3.metric(t["winning_trades"],  win_trades)
            c4.metric(t["losing_trades"],   loss_trades)
            st.divider()

    # ── Panel de Aprendizaje AI ───────────────────────────────────────────────
    st.divider()
    st.subheader(t["feedback_title"])
    mem = FeedbackService.get_memory()
    if not mem or mem.get("total_trades", 0) < 5:
        st.info(t["feedback_no_data"].format(n=5))
    else:
        st.caption(t["feedback_updated"].format(ts=mem.get("last_updated", "—")))

        # Métricas globales
        fm1, fm2, fm3, fm4 = st.columns(4)
        fm1.metric(t["feedback_trades"],     mem["total_trades"])
        fm2.metric(t["feedback_winrate"],    f"{mem['win_rate']*100:.1f}%")
        fm3.metric(t["feedback_avg_win"],    f"${mem['avg_win']:+.2f}")
        fm4.metric(t["feedback_avg_loss"],   f"-${mem['avg_loss']:.2f}")

        rr1, rr2 = st.columns(2)
        rr1.metric(t["feedback_planned_rr"], f"1:{mem['avg_planned_rr']}")
        rr2.metric(t["feedback_actual_rr"],  f"1:{mem['avg_actual_rr']}")

        # Rendimiento por setup
        by_setup = mem.get("by_setup", {})
        if by_setup:
            st.markdown(f"**{t['feedback_by_setup']}**")
            cols_s = st.columns(len(by_setup))
            for i, (setup, stats) in enumerate(by_setup.items()):
                if not setup or setup == "nan":
                    continue
                color = "#28a745" if stats["win_rate"] >= mem["win_rate"] else "#dc3545"
                cols_s[i].markdown(
                    f"<div style='border:1px solid {color};border-radius:6px;"
                    f"padding:8px;text-align:center;'>"
                    f"<b style='color:{color};'>{setup}</b><br>"
                    f"<span style='font-size:1.2rem;font-weight:bold;'>"
                    f"{stats['win_rate']*100:.0f}%</span><br>"
                    f"<small style='color:#888;'>{stats['wins']}/{stats['n']} trades</small>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # Rendimiento por sesión
        by_session = mem.get("by_session", {})
        valid_sessions = {k: v for k, v in by_session.items()
                         if k and k not in ("nan", "OFF") and v["n"] > 0}
        if valid_sessions:
            st.markdown(f"**{t['feedback_by_session']}**")
            cols_ss = st.columns(len(valid_sessions))
            for i, (sess, stats) in enumerate(valid_sessions.items()):
                color = "#28a745" if stats["win_rate"] >= mem["win_rate"] else "#ffc107"
                cols_ss[i].markdown(
                    f"<div style='border:1px solid {color};border-radius:6px;"
                    f"padding:8px;text-align:center;'>"
                    f"<b style='color:{color};'>{sess}</b><br>"
                    f"<span style='font-size:1.2rem;font-weight:bold;'>"
                    f"{stats['win_rate']*100:.0f}%</span><br>"
                    f"<small style='color:#888;'>{stats['wins']}/{stats['n']} trades</small>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # Notas de calibración
        notes = mem.get("calibration_notes", [])
        if notes:
            st.markdown(f"**{t['feedback_calibration']}**")
            for note in notes:
                st.markdown(
                    f"<div style='border-left:3px solid #ffc107;padding:6px 12px;"
                    f"margin:4px 0;background:rgba(255,193,7,0.08);border-radius:0 4px 4px 0;'>"
                    f"<small>💡 {note}</small></div>",
                    unsafe_allow_html=True,
                )

        # Botón para forzar recálculo manual
        if st.button(t["feedback_refresh_btn"]):
            FeedbackService.update_memory()
            st.toast(t["feedback_refreshed"], icon="🧠")
            st.rerun()

    st.divider()
    st.subheader(t["full_history"])
    st.dataframe(history, width="stretch")


# --- REGISTRO DE ACTIVIDAD ---
st.divider()
with st.expander(t["activity_log"], expanded=False):
    tn = time.strftime("%H:%M:%S")
    st.write(f"[{tn}] {t['cycle_started']}")
    st.write(f"[{tn}] {t['connected_to']} **{selected_symbol}**")
    if run_ai:
        mode_tag = f"{'🤖 AUTO' if autonomous_mode else '👤 MANUAL'}"
        st.write(
            f"[{tn}] {t['ai_active_log']} "
            f"{AUTONOMOUS_CONFIDENCE_THRESHOLD*100:.0f}% | {mode_tag}"
        )
    else:
        st.write(f"[{tn}] {t['ai_idle_log']}")


# --- AUTO-REFRESCO ---
st.caption(t["next_refresh"].format(n=refresh_interval))
time.sleep(refresh_interval)
st.rerun()
