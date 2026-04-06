import streamlit as st
import pandas as pd
import time
from datetime import timedelta
from i18n import get_translations
from config import LOCAL_UTC_OFFSET, LOCAL_TZ_NAME, BROKER_UTC_OFFSET, AI_STALE_MINS, MAX_DAILY_LOSS_PCT, AI_MIN_INTERVAL_MINS


def _utc_to_local_hhmm(utc_h: int, utc_m: int) -> str:
    """Convierte hora UTC a hora local usando LOCAL_UTC_OFFSET. Retorna 'HH:MM'."""
    total_mins = utc_h * 60 + utc_m + LOCAL_UTC_OFFSET * 60
    total_mins %= 1440   # wrap 24h
    return f"{total_mins // 60:02d}:{total_mins % 60:02d}"


def render_news_marquee(news_data: dict, sentiment: dict, t: dict):
    """
    Fila superior con:
    - Badge de News Shield (verde / rojo / gris)
    - Sentimiento del mercado
    - Últimas noticias en texto compacto
    - Alerta si no hay API key o si hay error

    Args:
        news_data:  resultado de NewsService.get_economic_calendar()
        sentiment:  resultado de NewsService.get_market_sentiment()
        t:          traducciones
    """
    shield     = news_data.get("_shield", {})
    blocking   = shield.get("blocking", False)
    cal_error  = news_data.get("error")
    # Sentimiento: NO_API_KEY solo aplica a Finnhub (no al calendario FF)
    no_finnhub = sentiment.get("error") == "NO_API_KEY"

    # ── Badge de estado ───────────────────────────────────────────────────────
    if cal_error:
        badge_color = "#6c757d"
        badge_label = t["news_shield_error"]
    elif blocking:
        badge_color = "#dc3545"
        badge_label = t["news_shield_blocking"]
    else:
        badge_color = "#28a745"
        badge_label = t["news_shield_active"]

    col_badge, col_sent, col_news = st.columns([1.5, 1.5, 5])

    # Badge
    col_badge.markdown(
        f"""<div style="border:2px solid {badge_color};border-radius:6px;
                        padding:6px 10px;background:{badge_color}18;
                        text-align:center;">
              <span style="color:{badge_color};font-weight:bold;font-size:0.8rem;">
                {badge_label}
              </span>
            </div>""",
        unsafe_allow_html=True,
    )

    # Sentimiento
    sent_error = sentiment.get("error")
    if no_finnhub:
        col_sent.caption(t["news_no_key_warning"])
    elif sent_error:
        col_sent.caption(f"Sentiment: N/A")
    else:
        label = sentiment.get("label", "NEUTRAL")
        bull  = sentiment.get("bullish_pct", 0.33)
        bear  = sentiment.get("bearish_pct", 0.33)
        s_color = "#28a745" if label == "BULLISH" else "#dc3545" if label == "BEARISH" else "#aaa"
        col_sent.markdown(
            f"""<div style="text-align:center;">
                  <small style="color:#aaa;">{t['news_sentiment_title']}</small><br>
                  <span style="color:{s_color};font-weight:bold;">{label}</span>
                  <small style="color:#888;"> {bull*100:.0f}% / {bear*100:.0f}%</small>
                </div>""",
            unsafe_allow_html=True,
        )

    # Noticias recientes
    recent = news_data.get("_recent_news", [])
    if recent:
        headlines = "  |  ".join(
            f"[{n['source']}] {n['headline'][:80]}"
            for n in recent[:4]
        )
        col_news.markdown(
            f"<small style='color:#888;'>{headlines}</small>",
            unsafe_allow_html=True,
        )
    else:
        col_news.caption(t["news_no_events"])

    # Banner de bloqueo si shield está activo
    if blocking:
        st.error(
            f"🚫 {t['news_shield_blocking']} — "
            f"{t['news_blocked_reason'].format(cur=shield['currency'], n=shield['mins_away'], event=shield['event_name'])}"
        )


def render_news_panel(news_data: dict, sentiment: dict, t: dict):
    """
    Panel expandible con calendario económico del día + gráfico de sentimiento.
    Se usa dentro del tab Dashboard o de una pestaña dedicada.
    """
    cal_error = news_data.get("error")

    if cal_error:
        st.warning(t["news_api_error"].format(err=cal_error))

    col_cal, col_sent = st.columns([3, 1])

    # ── Calendario ────────────────────────────────────────────────────────────
    with col_cal:
        st.markdown(f"**{t['news_calendar_title']}**")
        events = news_data.get("events", [])
        if not events:
            st.caption(t["news_no_events"])
        else:
            impact_colors = {3: "#dc3545", 2: "#ffc107", 1: "#6c757d"}
            impact_labels = {
                3: t["news_impact_high"],
                2: t["news_impact_med"],
                1: t["news_impact_low"],
            }
            for ev in sorted(events, key=lambda x: x.get("mins_away", 999)):
                imp    = ev.get("impact", 1)
                color  = impact_colors.get(imp, "#6c757d")
                label  = impact_labels.get(imp, "")
                mins   = ev.get("mins_away", 999)
                timing = f"en {mins} min" if 0 <= mins <= 240 else (
                    f"hace {abs(mins)} min" if mins < 0 else ev.get("time", "")
                )
                actual   = f"  A:{ev['actual']}"   if ev.get("actual")   else ""
                estimate = f"  E:{ev['estimate']}" if ev.get("estimate") else ""
                prev     = f"  P:{ev['prev']}"     if ev.get("prev")     else ""
                st.markdown(
                    f"""<div style="border-left:3px solid {color};padding:4px 10px;
                                    margin:3px 0;background:{color}0d;border-radius:0 4px 4px 0;">
                          <span style="color:{color};font-size:0.75rem;font-weight:bold;">
                            [{label}] {ev.get('currency','')}
                          </span>
                          <span style="color:#ccc;font-size:0.85rem;">
                            {ev.get('event','')[:60]}
                          </span>
                          <span style="color:#888;font-size:0.75rem;float:right;">
                            {timing}{actual}{estimate}{prev}
                          </span>
                        </div>""",
                    unsafe_allow_html=True,
                )

    # ── Sentimiento ───────────────────────────────────────────────────────────
    with col_sent:
        st.markdown(f"**{t['news_sentiment_title']}**")
        sent_error = sentiment.get("error")
        if sent_error:
            st.caption(f"N/A ({sent_error})")
        else:
            bull = sentiment.get("bullish_pct", 0.33)
            bear = sentiment.get("bearish_pct", 0.33)
            neut = sentiment.get("neutral_pct", 0.34)
            buzz = sentiment.get("buzz", 0)
            label = sentiment.get("label", "NEUTRAL")
            s_color = "#28a745" if label == "BULLISH" else "#dc3545" if label == "BEARISH" else "#aaa"

            st.markdown(
                f"""<div style="text-align:center;padding:8px;">
                      <div style="font-size:1.3rem;font-weight:bold;color:{s_color};">
                        {label}
                      </div>
                      <div style="margin:6px 0;">
                        <div style="background:#333;border-radius:4px;height:8px;margin:2px 0;">
                          <div style="background:#28a745;width:{bull*100:.0f}%;height:8px;border-radius:4px;"></div>
                        </div>
                        <small style="color:#28a745;">Bull {bull*100:.0f}%</small>
                      </div>
                      <div style="margin:4px 0;">
                        <div style="background:#333;border-radius:4px;height:8px;margin:2px 0;">
                          <div style="background:#dc3545;width:{bear*100:.0f}%;height:8px;border-radius:4px;"></div>
                        </div>
                        <small style="color:#dc3545;">Bear {bear*100:.0f}%</small>
                      </div>
                      <small style="color:#666;">{t['news_buzz']}: {buzz}</small>
                    </div>""",
                unsafe_allow_html=True,
            )


def render_market_semaphore(
    smc_state: dict,
    mtf_state: dict,
    session_losses: int,
    spread_ok: bool,
    daily_exceeded: bool,
    t: dict,
):
    """
    Panel semáforo de 3 indicadores (solo lectura de datos ya calculados).
    Diseñado para usuarios no técnicos: verde/amarillo/rojo + texto humano.

    Args:
        smc_state     : resultado de SMCService.get_smc_state()
        mtf_state     : resultado de IndicatorsService.get_multi_timeframe_state()
        session_losses: pérdidas cerradas hoy (int)
        spread_ok     : True si el spread actual es aceptable
        daily_exceeded: True si se alcanzó el límite de pérdida diaria
    """
    st.markdown(f"**{t['sem_title']}**")

    # ── 1. Estado del Mercado ─────────────────────────────────────────────────
    structure  = smc_state.get("structure", "NEUTRAL") if smc_state else "NEUTRAL"
    d1_trend   = mtf_state.get("d1", {}).get("trend", "")
    h1_trend   = mtf_state.get("h1", {}).get("trend", "")
    in_kz      = (smc_state or {}).get("session", {}).get("in_kill_zone", False)
    d1h1_align = (d1_trend == "UP" and h1_trend == "UP") or \
                 (d1_trend == "DOWN" and h1_trend == "DOWN")

    if structure != "NEUTRAL" and d1h1_align:
        mkt_color, mkt_dot, mkt_lbl, mkt_detail = \
            "#28a745", "🟢", t["sem_green_mkt"], t["sem_detail_mkt_g"]
    elif structure != "NEUTRAL":
        mkt_color, mkt_dot, mkt_lbl, mkt_detail = \
            "#ffc107", "🟡", t["sem_yellow_mkt"], t["sem_detail_mkt_y"]
    else:
        mkt_color, mkt_dot, mkt_lbl, mkt_detail = \
            "#dc3545", "🔴", t["sem_red_mkt"], t["sem_detail_mkt_r"]

    # ── 2. Oportunidad ────────────────────────────────────────────────────────
    setup = (smc_state or {}).get("setup", "WAIT")

    if setup == "CONFIRMED" and in_kz:
        opp_color, opp_dot, opp_lbl, opp_detail = \
            "#28a745", "🟢", t["sem_green_opp"], t["sem_detail_opp_g"]
    elif setup in ("CONFIRMED", "AGGRESSIVE"):
        opp_color, opp_dot, opp_lbl, opp_detail = \
            "#ffc107", "🟡", t["sem_yellow_opp"], t["sem_detail_opp_y"]
    else:
        opp_color, opp_dot, opp_lbl, opp_detail = \
            "#dc3545", "🔴", t["sem_red_opp"], t["sem_detail_opp_r"]

    # ── 3. Riesgo Hoy ────────────────────────────────────────────────────────
    if daily_exceeded:
        risk_color, risk_dot, risk_lbl, risk_detail = \
            "#dc3545", "🔴", t["sem_limit_reached"], \
            t["sem_detail_risk_r"].format(pct=MAX_DAILY_LOSS_PCT)
    elif session_losses >= 2 or not spread_ok:
        risk_color, risk_dot, risk_lbl, risk_detail = \
            "#ffc107", "🟡", t["sem_yellow_risk"], \
            t["sem_detail_risk_y"].format(losses=session_losses)
    else:
        risk_color, risk_dot, risk_lbl, risk_detail = \
            "#28a745", "🟢", t["sem_green_risk"], \
            t["sem_detail_risk_g"].format(losses=session_losses)

    # ── Render: 3 tarjetas en columnas ───────────────────────────────────────
    c1, c2, c3 = st.columns(3)

    def _card(col, color, dot, title, label, detail):
        col.markdown(
            f"""<div style="border:1px solid {color};border-radius:8px;
                            padding:12px;background:{color}12;text-align:center;">
                  <div style="font-size:0.75rem;color:#aaa;margin-bottom:4px;">
                    {title}
                  </div>
                  <div style="font-size:1.5rem;">{dot}</div>
                  <div style="font-size:0.95rem;font-weight:bold;color:{color};
                              margin:2px 0;">
                    {label}
                  </div>
                  <div style="font-size:0.72rem;color:#888;margin-top:4px;">
                    {detail}
                  </div>
                </div>""",
            unsafe_allow_html=True,
        )

    _card(c1, mkt_color,  mkt_dot,  t["sem_market"],      mkt_lbl,  mkt_detail)
    _card(c2, opp_color,  opp_dot,  t["sem_opportunity"],  opp_lbl,  opp_detail)
    _card(c3, risk_color, risk_dot, t["sem_risk"],         risk_lbl, risk_detail)


def render_sessions_clock(times: dict, t: dict):
    """
    Widget de reloj y sesiones de mercado.

    times = {"utc": datetime, "broker": datetime, "local": datetime}
    Sesiones y Kill Zones evaluadas en hora local (configurable: LOCAL_UTC_OFFSET).
    Los horarios mostrados se calculan automáticamente desde UTC.
    """
    local_dt   = times["local"]
    local_mins = local_dt.hour * 60 + local_dt.minute

    # ── Helper: rango con soporte a cruce de medianoche ──────────────────────
    def _in(s_h, s_m, e_h, e_m):
        s = s_h * 60 + s_m
        e = e_h * 60 + e_m
        if s <= e:
            return s <= local_mins < e
        return local_mins >= s or local_mins < e

    # ── Sesiones en hora local ────────────────────────────────────────────────
    # Definidas en UTC y convertidas automáticamente:
    #   Asia UTC   00:00-09:00  | London UTC 07:00-16:00 | NY UTC 13:00-22:00
    # KZ London UTC 07:00-10:00 | KZ NY UTC 13:00-16:00
    def _local_range(utc_s_h, utc_e_h):
        """Retorna (local_start_h, local_end_h) aplicando el offset."""
        ls = (utc_s_h * 60 + LOCAL_UTC_OFFSET * 60) % 1440
        le = (utc_e_h * 60 + LOCAL_UTC_OFFSET * 60) % 1440
        return ls // 60, ls % 60, le // 60, le % 60

    # UTC ranges → (s_h, s_m, e_h, e_m) en local
    as_sh, as_sm, as_eh, as_em   = _local_range(0,  9)   # Asia
    lo_sh, lo_sm, lo_eh, lo_em   = _local_range(7, 16)   # London
    ny_sh, ny_sm, ny_eh, ny_em   = _local_range(13, 22)  # NY
    kl_sh, kl_sm, kl_eh, kl_em  = _local_range(7, 10)   # KZ London
    kn_sh, kn_sm, kn_eh, kn_em  = _local_range(13, 16)  # KZ NY

    asia_on = _in(as_sh, as_sm, as_eh, as_em)
    lon_on  = _in(lo_sh, lo_sm, lo_eh, lo_em)
    ny_on   = _in(ny_sh, ny_sm, ny_eh, ny_em)
    kz_lon  = _in(kl_sh, kl_sm, kl_eh, kl_em)
    kz_ny   = _in(kn_sh, kn_sm, kn_eh, kn_em)

    # Strings de horario para display
    tz_label = f"{LOCAL_TZ_NAME} (UTC{LOCAL_UTC_OFFSET:+d})"

    def _hhmm(h, m): return f"{h:02d}:{m:02d}"
    asia_range  = f"{_hhmm(as_sh,as_sm)} – {_hhmm(as_eh,as_em)}"
    lon_range   = f"{_hhmm(lo_sh,lo_sm)} – {_hhmm(lo_eh,lo_em)}"
    ny_range    = f"{_hhmm(ny_sh,ny_sm)} – {_hhmm(ny_eh,ny_em)}"
    kzl_range   = f"{_hhmm(kl_sh,kl_sm)} – {_hhmm(kl_eh,kl_em)}"
    kzn_range   = f"{_hhmm(kn_sh,kn_sm)} – {_hhmm(kn_eh,kn_em)}"

    # ── Render ────────────────────────────────────────────────────────────────
    st.markdown(f"**{t['clock_title']}**")

    cb, cu, cc = st.columns(3)
    broker_sign = f"UTC{BROKER_UTC_OFFSET:+d}"
    cb.markdown(
        f"<div style='text-align:center'>"
        f"<small style='color:#aaa;'>{t['clock_broker']} ({broker_sign})</small><br>"
        f"<span style='font-size:1.2rem;font-weight:bold;letter-spacing:1px;'>"
        f"{times['broker'].strftime('%H:%M:%S')}</span></div>",
        unsafe_allow_html=True,
    )
    cu.markdown(
        f"<div style='text-align:center'>"
        f"<small style='color:#aaa;'>{t['clock_utc']}</small><br>"
        f"<span style='font-size:1.2rem;font-weight:bold;letter-spacing:1px;'>"
        f"{times['utc'].strftime('%H:%M:%S')}</span></div>",
        unsafe_allow_html=True,
    )
    cc.markdown(
        f"<div style='text-align:center'>"
        f"<small style='color:#aaa;'>{LOCAL_TZ_NAME} (UTC{LOCAL_UTC_OFFSET:+d})</small><br>"
        f"<span style='font-size:1.4rem;font-weight:900;letter-spacing:1px;color:#42a5f5;'>"
        f"{local_dt.strftime('%H:%M:%S')}</span></div>",
        unsafe_allow_html=True,
    )

    st.markdown("")

    # Sesiones
    def _session_badge(label, active, hours):
        color      = "#28a745" if active else "#444"
        text_color = "#fff"    if active else "#888"
        status     = t["status_active"] if active else t["status_inactive"]
        st.markdown(
            f"""<div style="border:1px solid {color};border-radius:6px;
                            padding:6px 8px;margin-bottom:4px;background:{color}18;">
                  <span style="color:{text_color};font-weight:bold;">{label}</span>
                  <span style="float:right;color:{color};font-size:0.78rem;
                               font-weight:bold;">{status}</span><br>
                  <small style="color:#888;">{hours}</small>
                </div>""",
            unsafe_allow_html=True,
        )

    _session_badge(t["session_asia"],   asia_on, asia_range)
    _session_badge(t["session_london"], lon_on,  lon_range)
    _session_badge(t["session_ny"],     ny_on,   ny_range)

    st.markdown(f"<small style='color:#aaa;'><b>{t['kz_title']}</b></small>",
                unsafe_allow_html=True)

    # Kill Zones
    def _kz_badge(label, active, hours):
        if active:
            st.markdown(
                f"""<div style="border:2px solid #ffc107;border-radius:6px;
                                padding:6px 8px;margin-bottom:4px;
                                background:rgba(255,193,7,0.15);">
                      <span style="color:#ffc107;font-weight:bold;">⚡ {label}</span>
                      <span style="float:right;color:#ffc107;font-size:0.8rem;
                                   font-weight:bold;">{t['kz_active']}</span><br>
                      <small style="color:#aaa;">{hours}</small>
                    </div>""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""<div style="border:1px solid #444;border-radius:6px;
                                padding:6px 8px;margin-bottom:4px;">
                      <span style="color:#666;">{label}</span>
                      <span style="float:right;color:#555;font-size:0.78rem;">
                        {t['kz_inactive']}</span><br>
                      <small style="color:#555;">{hours}</small>
                    </div>""",
                unsafe_allow_html=True,
            )

    _kz_badge(t["kz_london"], kz_lon, kzl_range)
    _kz_badge(t["kz_ny"],     kz_ny,  kzn_range)


def render_metrics(acc, t: dict):
    """Muestra las métricas básicas de la cuenta."""
    if acc:
        c1, c2, c3 = st.columns(3)
        c1.metric(t["equity"],       f"${acc.equity:,.2f}")
        c2.metric(t["balance"],      f"${acc.balance:,.2f}")
        c3.metric(t["total_profit"], f"${acc.profit:,.2f}", delta=acc.profit)


def render_technical_analysis(state: dict, t: dict):
    """Muestra los indicadores técnicos H1."""
    st.subheader(t["technical_analysis"])
    if not state:
        st.warning(t["calculating"])
        return

    c1, c2, c3, c4 = st.columns(4)

    rsi = state.get("RSI_14", 50) or state.get("rsi", 50)
    rsi_delta = (
        t["overbought"] if rsi > 70
        else t["oversold"] if rsi < 30
        else t["neutral"]
    )
    c1.metric(t["rsi"], f"{rsi:.2f}", delta=rsi_delta)

    ema20 = state.get("EMA_20", 0) or state.get("ema20", 0)
    ema50 = state.get("EMA_50", 0) or state.get("ema50", 0)
    trend = t["bullish_trend"] if ema20 > ema50 else t["bearish_trend"]
    c2.metric(t["ema_trend"], trend)

    atr   = state.get("ATRr_14", 0) or state.get("atr", 0)
    close = state.get("close", 0)
    c3.metric(t["volatility"],   f"{atr:.5f}")
    c4.metric(t["close_price"],  f"{close:.5f}")


def render_mtf_badges(d1: dict, m15: dict, t: dict):
    """Muestra los badges compactos de D1 macro y M15 momentum."""
    if d1:
        d1_trend = d1.get("trend", "?")
        color = "#28a745" if d1_trend == "UP" else "#dc3545"
        label = t["bullish_trend"] if d1_trend == "UP" else t["bearish_trend"]
        st.markdown(
            f'<span style="color:{color};font-weight:bold;">'
            f'{t["d1_macro"]}: {label} | EMA200: {d1.get("ema200","?")} | RSI: {d1.get("rsi","?")}'
            f'</span>',
            unsafe_allow_html=True,
        )
    if m15:
        mom = m15.get("momentum", "?")
        color = "#28a745" if mom == "BULLISH" else "#dc3545"
        label = t["bullish_momentum"] if mom == "BULLISH" else t["bearish_momentum"]
        st.markdown(
            f'<span style="color:{color};">'
            f'{t["m15_entry"]}: {label} | RSI: {m15.get("rsi","?")}'
            f'</span>',
            unsafe_allow_html=True,
        )


def render_sidebar(symbols: list, callback, t: dict) -> tuple:
    """
    Renderiza la barra lateral completa.

    Returns:
        (symbol, refresh_interval, run_ai, autonomous_mode, lang, ai_interval_mins)
    """
    # ---- SECCIÓN OPERATIVA ----
    st.sidebar.header(t["trading_ops"])
    with st.sidebar.form("trade_form"):
        sym  = st.selectbox(t["asset"], symbols)
        lot  = st.number_input(t["lot"],     0.01, 1.0,  0.1,  step=0.01)
        sl   = st.number_input(t["sl_pips"], 0,    500,  20)
        tp   = st.number_input(t["tp_pips"], 0,    1000, 40)
        c1, c2 = st.columns(2)
        if c1.form_submit_button("BUY",  width="stretch"):
            callback("BUY",  sym, lot, sl, tp)
        if c2.form_submit_button("SELL", width="stretch"):
            callback("SELL", sym, lot, sl, tp)

    st.sidebar.divider()

    # ---- SECCIÓN CONFIGURACIÓN ----
    st.sidebar.header(t["settings"])

    refresh = st.sidebar.slider(t["auto_refresh"], 5, 300, 60)

    run_ai = st.sidebar.toggle(t["enable_ai"], value=False)

    autonomous_mode = st.sidebar.toggle(
        t["autonomous_mode"],
        value=False,
        help=t["autonomous_help"],
        disabled=not run_ai,
    )

    # Q8 — intervalo mínimo entre análisis AI (solo visible si IA activa)
    if run_ai:
        ai_interval = st.sidebar.number_input(
            t["ai_min_interval"],
            min_value=1, max_value=60,
            value=AI_MIN_INTERVAL_MINS,
            step=1,
            key="ai_interval_mins",
            help="Evita llamadas innecesarias a la API y controla el costo.",
        )
    else:
        ai_interval = AI_MIN_INTERVAL_MINS

    st.sidebar.divider()

    # ---- SECCIÓN IDIOMA ----
    lang = st.sidebar.radio(
        t["language"],
        options=["es", "en"],
        format_func=lambda x: "🇪🇸 Español" if x == "es" else "🇬🇧 English",
        horizontal=True,
        key="lang_selector",
    )

    return sym, refresh, run_ai, autonomous_mode, lang, ai_interval


def render_smc_chart(df: pd.DataFrame, swings: list, smc: dict, t: dict):
    """
    Gráfico de velas H1 con overlays SMC completos:
      - Candlestick OHLC + volumen
      - Order Blocks (rectángulos coloreados)
      - Fair Value Gaps (zonas sombreadas)
      - Swing Highs / Lows (marcadores triangulares)
      - PDH / PDL / PWH / PWL (líneas horizontales)
      - EQH / EQL (líneas de liquidez)
      - BOS / CHOCH (líneas de estructura)
    """
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        st.warning("Instala plotly: `pip install plotly`")
        return

    if df is None or df.empty or smc.get("error"):
        st.info(t.get("smc_no_data", "Sin datos"))
        return

    # Usar últimas 80 velas para claridad visual
    df_plot = df.tail(80).reset_index(drop=True)
    offset  = len(df) - len(df_plot)   # índice de inicio en el df original

    t_min = df_plot["time"].iloc[0]
    t_max = df_plot["time"].iloc[-1]
    # Extender el borde derecho para que las etiquetas no queden cortadas
    t_right = t_max + pd.Timedelta(hours=6)

    # ── Subplots: velas (80%) + volumen (20%) ────────────────────────────────
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.8, 0.2],
        vertical_spacing=0.02,
    )

    # 1. Candlestick
    fig.add_trace(go.Candlestick(
        x=df_plot["time"],
        open=df_plot["open"],
        high=df_plot["high"],
        low=df_plot["low"],
        close=df_plot["close"],
        name="H1",
        increasing=dict(line=dict(color="#26a69a"), fillcolor="#26a69a"),
        decreasing=dict(line=dict(color="#ef5350"), fillcolor="#ef5350"),
        showlegend=True,
    ), row=1, col=1)

    # 2. Volumen
    vol_colors = [
        "#26a69a" if df_plot["close"].iloc[i] >= df_plot["open"].iloc[i] else "#ef5350"
        for i in range(len(df_plot))
    ]
    fig.add_trace(go.Bar(
        x=df_plot["time"],
        y=df_plot["tick_volume"],
        marker_color=vol_colors,
        name="Volume",
        showlegend=False,
        opacity=0.6,
    ), row=2, col=1)

    # 3. Swing Highs / Lows
    vis = [s for s in swings if s["idx"] >= offset]
    if vis:
        sh = [s for s in vis if s["type"] == "H"]
        sl = [s for s in vis if s["type"] == "L"]
        if sh:
            fig.add_trace(go.Scatter(
                x=[df.iloc[s["idx"]]["time"] for s in sh],
                y=[s["price"] for s in sh],
                mode="markers+text",
                marker=dict(symbol="triangle-down", size=11, color="#ef5350"),
                text=["SH"] * len(sh),
                textposition="top center",
                textfont=dict(size=9, color="#ef5350"),
                name="Swing High",
                showlegend=True,
            ), row=1, col=1)
        if sl:
            fig.add_trace(go.Scatter(
                x=[df.iloc[s["idx"]]["time"] for s in sl],
                y=[s["price"] for s in sl],
                mode="markers+text",
                marker=dict(symbol="triangle-up", size=11, color="#26a69a"),
                text=["SL"] * len(sl),
                textposition="bottom center",
                textfont=dict(size=9, color="#26a69a"),
                name="Swing Low",
                showlegend=True,
            ), row=1, col=1)

    # 4. Order Blocks (rectángulos con borde y relleno semi-transparente)
    for ob in smc.get("order_blocks", []):
        is_bull = ob["type"] == "BULL"
        fill    = "rgba(38,166,154,0.18)"  if is_bull else "rgba(239,83,80,0.18)"
        border  = "#26a69a"                if is_bull else "#ef5350"
        x0 = df.iloc[ob["idx"]]["time"] if ob["idx"] < len(df) else t_min
        fig.add_shape(
            type="rect",
            xref="x", yref="y",
            x0=x0, x1=t_right,
            y0=ob["low"], y1=ob["high"],
            fillcolor=fill,
            line=dict(color=border, width=1),
            row=1, col=1,
        )
        fig.add_annotation(
            x=t_right, y=(ob["high"] + ob["low"]) / 2,
            xref="x", yref="y",
            text=f"{'🟢' if is_bull else '🔴'} {ob['type']} OB",
            showarrow=False,
            font=dict(size=9, color=border),
            xanchor="left",
            row=1, col=1,
        )

    # 5. FVG Zones
    for fvg in smc.get("fvg_zones", []):
        is_bull = fvg["type"] == "BULL"
        fill    = "rgba(255,193,7,0.15)"   if is_bull else "rgba(156,39,176,0.15)"
        border  = "#ffc107"                if is_bull else "#9c27b0"
        fig.add_shape(
            type="rect",
            xref="x", yref="y",
            x0=t_min, x1=t_right,
            y0=fvg["bottom"], y1=fvg["top"],
            fillcolor=fill,
            line=dict(color=border, width=1, dash="dot"),
            row=1, col=1,
        )
        fig.add_annotation(
            x=t_right, y=(fvg["top"] + fvg["bottom"]) / 2,
            xref="x", yref="y",
            text=f"{'🟡' if is_bull else '🟣'} FVG",
            showarrow=False,
            font=dict(size=9, color=border),
            xanchor="left",
            row=1, col=1,
        )

    # 6. Función auxiliar para líneas horizontales con etiqueta
    def _hline(price, color, dash, label, width=1):
        if price is None:
            return
        fig.add_shape(
            type="line",
            xref="x", yref="y",
            x0=t_min, x1=t_right,
            y0=price, y1=price,
            line=dict(color=color, width=width, dash=dash),
            row=1, col=1,
        )
        fig.add_annotation(
            x=t_right, y=price,
            xref="x", yref="y",
            text=label,
            showarrow=False,
            font=dict(size=9, color=color),
            xanchor="left",
            row=1, col=1,
        )

    # 7. PDH / PDL
    _hline(smc.get("pdh"), "#ff9800", "dash",     "PDH")
    _hline(smc.get("pdl"), "#ff9800", "dash",     "PDL")
    # 8. PWH / PWL
    _hline(smc.get("pwh"), "#9c27b0", "longdash", "PWH")
    _hline(smc.get("pwl"), "#9c27b0", "longdash", "PWL")
    # 9. EQH / EQL (liquidez)
    for p in smc.get("eqh", []):
        _hline(p, "#ef5350", "dot", "EQH ⚡")
    for p in smc.get("eql", []):
        _hline(p, "#26a69a", "dot", "EQL ⚡")
    # 10. BOS / CHOCH
    if smc.get("bos"):
        c = "#26a69a" if "BULL" in smc["bos"]["type"] else "#ef5350"
        _hline(smc["bos"]["price"], c, "dashdot", smc["bos"]["type"], width=2)
    if smc.get("choch"):
        c = "#26a69a" if "BULL" in smc["choch"]["type"] else "#ef5350"
        _hline(smc["choch"]["price"], c, "dashdot", smc["choch"]["type"], width=2)

    # ── Layout ────────────────────────────────────────────────────────────────
    structure = smc.get("structure", "")
    bias      = smc.get("bias", "")
    setup     = smc.get("setup", "")
    sess      = smc.get("session", {})
    kz_tag    = f"{'🔴 KZ' if sess.get('in_kill_zone') else '⚪ OFF'} {sess.get('time_utc','')}"

    fig.update_layout(
        title=dict(
            text=(f"<b>H1 · SMC</b>  |  "
                  f"Structure: <b>{structure}</b>  |  "
                  f"Bias: <b>{bias}</b>  |  "
                  f"Setup: <b>{setup}</b>  |  {kz_tag}"),
            font=dict(size=13),
        ),
        template="plotly_dark",
        height=620,
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=120, t=50, b=10),
        legend=dict(orientation="h", y=1.04, x=0),
        xaxis2=dict(showgrid=False),
    )
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)")
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)")

    st.plotly_chart(fig, width="stretch")


def render_smc_panel(smc: dict, t: dict):
    """Panel completo de Smart Money Concepts."""
    st.subheader(t["smc_title"])

    if not smc or smc.get("error"):
        st.warning(t["smc_no_data"])
        return

    colors = t["smc_setup_colors"]
    setup  = smc.get("setup", "WAIT")
    setup_color = colors.get(setup, "#6c757d")

    # ── Fila 1: estructura, sesión, bias, setup ──────────────────────────────
    c1, c2, c3, c4 = st.columns(4)

    struct = smc.get("structure", "NEUTRAL")
    s_color = "#28a745" if struct == "BULLISH" else "#dc3545" if struct == "BEARISH" else "#6c757d"
    labels  = " · ".join(smc.get("swing_labels", [])) or "—"
    c1.markdown(
        f"**{t['smc_structure']}**<br>"
        f'<span style="color:{s_color};font-size:1.2em;font-weight:bold;">'
        f"{struct}</span><br><small>{labels}</small>",
        unsafe_allow_html=True,
    )

    sess     = smc["session"]
    kz_color = "#28a745" if sess["in_kill_zone"] else "#6c757d"
    kz_label = t["smc_kill_zone"] if sess["in_kill_zone"] else t["smc_off_zone"]
    c2.markdown(
        f"**{t['smc_session']}**<br>"
        f'<span style="color:{kz_color};font-weight:bold;">{sess["session"]}</span><br>'
        f'<small style="color:{kz_color};">{kz_label} · {sess["time_utc"]}</small>',
        unsafe_allow_html=True,
    )

    bias       = smc.get("bias", "NEUTRAL")
    bias_color = "#28a745" if bias == "LONG" else "#dc3545" if bias == "SHORT" else "#6c757d"
    c3.markdown(
        f"**{t['smc_bias']}**<br>"
        f'<span style="color:{bias_color};font-size:1.2em;font-weight:bold;">{bias}</span>',
        unsafe_allow_html=True,
    )

    c4.markdown(
        f"**{t['smc_setup']}**<br>"
        f'<span style="color:{setup_color};font-size:1.1em;font-weight:bold;">{setup}</span>',
        unsafe_allow_html=True,
    )

    # ── Setup details ────────────────────────────────────────────────────────
    st.markdown(
        f'<div style="border-left:4px solid {setup_color};padding:8px 12px;'
        f'background:rgba(0,0,0,0.05);border-radius:4px;margin:8px 0;">'
        f'<b>{t["smc_details"]}:</b> {smc.get("setup_details","—")}</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Fila 2: BOS / CHOCH ──────────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    bos = smc.get("bos")
    with col_a:
        st.markdown(f"**{t['smc_bos']}**")
        if bos:
            bc = "#28a745" if "BULL" in bos["type"] else "#dc3545"
            st.markdown(
                f'<span style="color:{bc};font-weight:bold;">{bos["type"]}</span> '
                f'@ <code>{bos["price"]}</code>',
                unsafe_allow_html=True,
            )
        else:
            st.caption(t["smc_none"])

    choch = smc.get("choch")
    with col_b:
        st.markdown(f"**{t['smc_choch']}**")
        if choch:
            cc = "#28a745" if "BULL" in choch["type"] else "#dc3545"
            st.markdown(
                f'<span style="color:{cc};font-weight:bold;">{choch["type"]}</span> '
                f'@ <code>{choch["price"]}</code>',
                unsafe_allow_html=True,
            )
        else:
            st.caption(t["smc_none"])

    st.divider()

    # ── Fila 3: Order Blocks + FVGs ──────────────────────────────────────────
    col_ob, col_fvg = st.columns(2)

    with col_ob:
        st.markdown(f"**{t['smc_obs']}**")
        obs = smc.get("order_blocks", [])
        if obs:
            for ob in obs:
                oc = "#28a745" if ob["type"] == "BULL" else "#dc3545"
                st.markdown(
                    f'<span style="color:{oc};">▪ {ob["type"]} OB: '
                    f'<code>{ob["low"]} – {ob["high"]}</code></span>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption(t["smc_none"])

    with col_fvg:
        st.markdown(f"**{t['smc_fvg']}**")
        fvgs = smc.get("fvg_zones", [])
        if fvgs:
            for fvg in fvgs:
                fc = "#28a745" if fvg["type"] == "BULL" else "#dc3545"
                st.markdown(
                    f'<span style="color:{fc};">▪ {fvg["type"]} FVG: '
                    f'<code>{fvg["bottom"]} – {fvg["top"]}</code></span>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption(t["smc_none"])

    st.divider()

    # ── Fila 4: Niveles de liquidez ──────────────────────────────────────────
    st.markdown("**Liquidity Levels**")
    lc1, lc2, lc3, lc4 = st.columns(4)

    def _liq(col, label, value, buy_side=True):
        color = "#28a745" if buy_side else "#dc3545"
        col.markdown(
            f"<small>{label}</small><br>"
            f'<span style="color:{color};font-weight:bold;">'
            f"{value if value is not None else '—'}</span>",
            unsafe_allow_html=True,
        )

    eqh = smc.get("eqh", [])
    eql = smc.get("eql", [])
    _liq(lc1, t["smc_eqh"], ", ".join(str(x) for x in eqh) or "—", buy_side=True)
    _liq(lc2, t["smc_eql"], ", ".join(str(x) for x in eql) or "—", buy_side=False)
    _liq(lc3, f'{t["smc_pdh"]} / {t["smc_pdl"]}',
         f'{smc.get("pdh","—")} / {smc.get("pdl","—")}', buy_side=True)
    _liq(lc4, f'{t["smc_pwh"]} / {t["smc_pwl"]}',
         f'{smc.get("pwh","—")} / {smc.get("pwl","—")}', buy_side=True)


def render_ai_decision(ai_res: dict, t: dict):
    """Muestra el panel de decisión de la IA con colores dinámicos."""
    st.subheader(t["ai_verdict"])

    if not ai_res:
        st.info(t["waiting"])
        return

    decision   = ai_res.get("decision",   "HOLD")
    confidence = ai_res.get("confidence", 0.0)
    rr         = ai_res.get("risk_reward_ratio", 0.0)
    reasoning  = ai_res.get("reasoning",  "—")
    logic_path = ai_res.get("logic_path", "")

    # Q4 — edad del análisis
    ts         = ai_res.get("_ts", None)
    age_mins   = int((time.time() - ts) / 60) if ts else None

    # Q7 — banner de análisis obsoleto
    if age_mins is not None and age_mins >= AI_STALE_MINS:
        st.warning(t["analysis_stale"].format(n=age_mins))
    elif age_mins is not None:
        st.caption(t["analysis_age"].format(n=age_mins))

    color = "#28a745" if decision == "BUY" else "#dc3545" if decision == "SELL" else "#6c757d"

    # Barra de confianza visual
    conf_pct = int(confidence * 100)
    bar_color = "#28a745" if conf_pct >= 85 else "#ffc107" if conf_pct >= 60 else "#dc3545"

    st.markdown(
        f"""
        <div style="border:2px solid {color}; padding:20px; border-radius:10px;
                    background-color:rgba(0,0,0,0.05); margin-bottom:16px;">
            <h2 style="color:{color}; margin-top:0;">{decision}</h2>
            <p style="font-size:1.05em; color:white;">
                <b>{t["reasoning_label"]}:</b> {reasoning}
            </p>
            <hr style="border-color:{color}; opacity:0.3;">
            <div style="margin-bottom:6px;">
                <span style="font-weight:bold;">{t["confidence"]}: {conf_pct}%</span>
                <div style="background:#333;border-radius:4px;height:6px;margin-top:4px;">
                  <div style="background:{bar_color};width:{conf_pct}%;height:6px;
                              border-radius:4px;transition:width 0.3s;"></div>
                </div>
            </div>
            <div style="display:flex; justify-content:space-between; font-weight:bold;">
                <span>{t["rr_label"]}: 1:{rr:.1f}</span>
                <span>SL: {ai_res.get("sl_pips",0)} pips</span>
                <span>TP: {ai_res.get("tp_pips",0)} pips</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Logic path expandible
    if logic_path:
        with st.expander(t["logic_path_label"]):
            st.write(logic_path)
