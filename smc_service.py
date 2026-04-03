"""
SMC Service — Smart Money Concepts engine.

Implementa:
  - Swing Structure (HH, HL, LH, LL)
  - Break of Structure (BOS) y Change of Character (CHOCH)
  - Order Blocks (OB)
  - Fair Value Gaps (FVG / Imbalances)
  - Equal Highs / Equal Lows (EQH / EQL)
  - Previous Day/Week High-Low (PDH/PDL, PWH/PWL)
  - Session Kill Zones (Asia, London, NY)
  - Setup Checklist algorítmico (AGGRESSIVE / CONFIRMED / WAIT / NO_TRADE)
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timezone


class SMCService:
    N_SWING      = 2       # velas a cada lado para confirmar swing
    EQ_TOLERANCE = 0.0002  # tolerancia 0.02% (~2 pips) para EQH/EQL

    # =========================================================================
    # API PÚBLICA
    # =========================================================================

    @staticmethod
    def get_chart_data(symbol: str) -> tuple:
        """
        Retorna (df_h1, swings) para alimentar el gráfico de velas SMC.
        df_h1 : DataFrame con columnas time/open/high/low/close/tick_volume.
        swings: lista de swing points {'type','price','idx'}.
        """
        df = SMCService._fetch_df(symbol, mt5.TIMEFRAME_H1, 120)
        if df is None:
            return None, []
        swings = SMCService._find_swings(df)
        return df, swings

    @staticmethod
    def get_smc_state(symbol: str) -> dict:
        """
        Retorna el estado SMC completo del símbolo en H1.

        Retorna:
        {
          structure, swing_labels, bos, choch,
          order_blocks, fvg_zones, eqh, eql,
          pdh, pdl, pwh, pwl,
          session, bias, current_price,
          setup, setup_details
        }
        """
        df = SMCService._fetch_df(symbol, mt5.TIMEFRAME_H1, 150)
        if df is None or len(df) < 30:
            return {"error": "Datos insuficientes"}

        swings          = SMCService._find_swings(df)
        structure, lbls = SMCService._classify_structure(swings)
        bos, choch      = SMCService._detect_bos_choch(df, swings, structure)
        obs             = SMCService._detect_order_blocks(df, swings)
        fvgs            = SMCService._detect_fvg(df)
        eqh, eql        = SMCService._detect_equal_hl(swings)
        pdh, pdl        = SMCService._get_pdh_pdl(symbol)
        pwh, pwl        = SMCService._get_pwh_pwl(symbol)
        session         = SMCService._get_session()
        price           = round(float(df["close"].iloc[-1]), 5)
        bias            = ("LONG" if structure == "BULLISH"
                           else "SHORT" if structure == "BEARISH"
                           else "NEUTRAL")

        state = {
            "structure":     structure,
            "swing_labels":  lbls,
            "bos":           bos,
            "choch":         choch,
            "order_blocks":  obs,
            "fvg_zones":     fvgs,
            "eqh":           eqh,
            "eql":           eql,
            "pdh":           pdh,
            "pdl":           pdl,
            "pwh":           pwh,
            "pwl":           pwl,
            "session":       session,
            "bias":          bias,
            "current_price": price,
        }

        setup, details     = SMCService._determine_setup(state)
        state["setup"]         = setup
        state["setup_details"] = details
        return state

    # =========================================================================
    # DATOS
    # =========================================================================

    @staticmethod
    def _fetch_df(symbol: str, timeframe, count: int) -> pd.DataFrame | None:
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        if rates is None or len(rates) < 20:
            return None
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

    # =========================================================================
    # ESTRUCTURA DE MERCADO
    # =========================================================================

    @staticmethod
    def _find_swings(df: pd.DataFrame, n: int = None) -> list:
        """
        Detecta swing highs y swing lows con confirmación de n velas a cada lado.
        Retorna lista de {'type':'H'/'L', 'price':float, 'idx':int}.
        """
        n      = n if n is not None else SMCService.N_SWING
        highs  = df["high"].values
        lows   = df["low"].values
        swings = []

        for i in range(n, len(df) - n):
            is_sh = (all(highs[i] >= highs[i - j] for j in range(1, n + 1)) and
                     all(highs[i] >= highs[i + j] for j in range(1, n + 1)))
            is_sl = (all(lows[i]  <= lows[i - j]  for j in range(1, n + 1)) and
                     all(lows[i]  <= lows[i + j]   for j in range(1, n + 1)))

            if is_sh:
                swings.append({"type": "H", "price": float(highs[i]), "idx": i})
            elif is_sl:
                swings.append({"type": "L", "price": float(lows[i]),  "idx": i})

        return swings

    @staticmethod
    def _classify_structure(swings: list) -> tuple:
        """
        Clasifica la estructura de mercado a partir de los swings.
        Reglas:
          HH + HL → BULLISH
          LH + LL → BEARISH
          otro    → NEUTRAL
        """
        hs = [s for s in swings if s["type"] == "H"]
        ls = [s for s in swings if s["type"] == "L"]

        if len(hs) < 2 or len(ls) < 2:
            return "NEUTRAL", []

        hh = hs[-1]["price"] > hs[-2]["price"]
        hl = ls[-1]["price"] > ls[-2]["price"]
        lh = hs[-1]["price"] < hs[-2]["price"]
        ll = ls[-1]["price"] < ls[-2]["price"]

        if hh and hl:  return "BULLISH", ["HH", "HL"]
        if lh and ll:  return "BEARISH", ["LH", "LL"]
        if hh and ll:  return "NEUTRAL", ["HH", "LL"]  # expansión
        if lh and hl:  return "NEUTRAL", ["LH", "HL"]  # contracción
        return "NEUTRAL", []

    # =========================================================================
    # BOS / CHOCH
    # =========================================================================

    @staticmethod
    def _detect_bos_choch(df: pd.DataFrame, swings: list, structure: str) -> tuple:
        """
        BOS  : el precio rompe un swing en la MISMA dirección de la estructura
               (continuación de tendencia).
        CHOCH: el precio rompe un swing en CONTRA de la estructura
               (posible cambio de tendencia).
        """
        price = float(df["close"].iloc[-1])
        hs    = [s for s in swings if s["type"] == "H"]
        ls    = [s for s in swings if s["type"] == "L"]

        if not hs or not ls:
            return None, None

        last_sh = hs[-1]["price"]
        last_sl = ls[-1]["price"]
        bos = choch = None

        if price > last_sh:
            ev = {"type": "BOS_BULL" if structure == "BULLISH" else "CHOCH_BULL",
                  "price": round(last_sh, 5)}
            if structure == "BULLISH":
                bos   = ev
            else:
                choch = ev

        if price < last_sl:
            ev = {"type": "BOS_BEAR" if structure == "BEARISH" else "CHOCH_BEAR",
                  "price": round(last_sl, 5)}
            if structure == "BEARISH":
                bos   = ev
            else:
                choch = ev

        return bos, choch

    # =========================================================================
    # ORDER BLOCKS
    # =========================================================================

    @staticmethod
    def _detect_order_blocks(df: pd.DataFrame, swings: list) -> list:
        """
        Bullish OB: última vela bajista antes de un swing high (origen de impulso alcista).
        Bearish OB: última vela alcista antes de un swing low (origen de impulso bajista).
        Retorna hasta 4 OBs activos (no mitigados), ordenados por recencia.
        """
        opens  = df["open"].values
        closes = df["close"].values
        price  = closes[-1]
        obs    = []

        for swing in swings[-8:]:
            idx = swing["idx"]
            if idx < 3:
                continue

            if swing["type"] == "H":                  # busca vela bajista antes del SH
                for j in range(idx - 1, max(idx - 15, 0), -1):
                    if closes[j] < opens[j]:
                        ob_high = float(opens[j])
                        ob_low  = float(closes[j])
                        obs.append({
                            "type":      "BULL",
                            "high":      round(ob_high, 5),
                            "low":       round(ob_low,  5),
                            "idx":       j,
                            "active":    price > ob_low,
                            "mitigated": price < ob_low,
                        })
                        break

            else:                                     # busca vela alcista antes del SL
                for j in range(idx - 1, max(idx - 15, 0), -1):
                    if closes[j] > opens[j]:
                        ob_high = float(closes[j])
                        ob_low  = float(opens[j])
                        obs.append({
                            "type":      "BEAR",
                            "high":      round(ob_high, 5),
                            "low":       round(ob_low,  5),
                            "idx":       j,
                            "active":    price < ob_high,
                            "mitigated": price > ob_high,
                        })
                        break

        # Deduplicar y filtrar mitigados
        active = [o for o in obs if not o["mitigated"]]
        seen, unique = set(), []
        for o in reversed(active):
            key = f"{o['type']}_{o['low']:.4f}"
            if key not in seen:
                seen.add(key)
                unique.append(o)

        return unique[:4]

    # =========================================================================
    # FAIR VALUE GAPS
    # =========================================================================

    @staticmethod
    def _detect_fvg(df: pd.DataFrame) -> list:
        """
        Bullish FVG: vela[i].low  > vela[i-2].high  (hueco alcista entre 3 velas)
        Bearish FVG: vela[i].high < vela[i-2].low   (hueco bajista entre 3 velas)
        Retorna hasta 3 FVGs no rellenados más cercanos al precio actual.
        """
        highs  = df["high"].values
        lows   = df["low"].values
        closes = df["close"].values
        price  = closes[-1]
        fvgs   = []
        start  = max(2, len(df) - 60)   # últimas 60 velas

        for i in range(start, len(df)):
            # Bullish FVG
            if lows[i] > highs[i - 2]:
                top, bot = float(lows[i]), float(highs[i - 2])
                fvgs.append({"type": "BULL", "top": round(top, 5),
                             "bottom": round(bot, 5), "filled": price <= bot})
            # Bearish FVG
            if highs[i] < lows[i - 2]:
                top, bot = float(lows[i - 2]), float(highs[i])
                fvgs.append({"type": "BEAR", "top": round(top, 5),
                             "bottom": round(bot, 5), "filled": price >= top})

        unfilled = [f for f in fvgs if not f["filled"]]
        unfilled.sort(key=lambda x: abs((x["top"] + x["bottom"]) / 2 - price))
        return unfilled[:3]

    # =========================================================================
    # EQUAL HIGHS / EQUAL LOWS
    # =========================================================================

    @staticmethod
    def _detect_equal_hl(swings: list, tolerance: float = None) -> tuple:
        """
        EQH: dos swing highs con diferencia de precio ≤ tolerancia → liquidez buy-side.
        EQL: dos swing lows  con diferencia de precio ≤ tolerancia → liquidez sell-side.
        """
        tol   = tolerance if tolerance is not None else SMCService.EQ_TOLERANCE
        hs    = [s for s in swings if s["type"] == "H"]
        ls    = [s for s in swings if s["type"] == "L"]
        eqh, eql = [], []

        for i in range(len(hs) - 1):
            for j in range(i + 1, len(hs)):
                p1, p2 = hs[i]["price"], hs[j]["price"]
                if p1 > 0 and abs(p1 - p2) / p1 <= tol:
                    mid = round((p1 + p2) / 2, 5)
                    if mid not in eqh:
                        eqh.append(mid)

        for i in range(len(ls) - 1):
            for j in range(i + 1, len(ls)):
                p1, p2 = ls[i]["price"], ls[j]["price"]
                if p1 > 0 and abs(p1 - p2) / p1 <= tol:
                    mid = round((p1 + p2) / 2, 5)
                    if mid not in eql:
                        eql.append(mid)

        return eqh[-3:], eql[-3:]

    # =========================================================================
    # PDH / PDL / PWH / PWL
    # =========================================================================

    @staticmethod
    def _get_pdh_pdl(symbol: str) -> tuple:
        """Previous Day High / Low (D1 penúltima barra cerrada)."""
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_D1, 0, 3)
        if rates is None or len(rates) < 2:
            return None, None
        return round(float(rates[-2]["high"]), 5), round(float(rates[-2]["low"]), 5)

    @staticmethod
    def _get_pwh_pwl(symbol: str) -> tuple:
        """Previous Week High / Low (W1 penúltima barra cerrada)."""
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_W1, 0, 3)
        if rates is None or len(rates) < 2:
            return None, None
        return round(float(rates[-2]["high"]), 5), round(float(rates[-2]["low"]), 5)

    # =========================================================================
    # SESIONES / KILL ZONES
    # =========================================================================

    @staticmethod
    def _get_session() -> dict:
        """
        Sesiones y Kill Zones evaluadas en HORA LOCAL (configurable vía LOCAL_UTC_OFFSET).

        Horarios en hora local (por defecto Colombia, UTC-5):
          Asia    : 19:00 – 04:00  (cruza medianoche)
          London  : 02:00 – 11:00
          NY      : 08:00 – 17:00

        Kill Zones (high-probability):
          KZ London : 02:00 – 05:00
          KZ NY     : 08:00 – 11:00
        """
        from config import LOCAL_UTC_OFFSET
        from datetime import timedelta

        now_utc   = datetime.now(timezone.utc)
        now_local = now_utc + timedelta(hours=LOCAL_UTC_OFFSET)
        mins      = now_local.hour * 60 + now_local.minute

        def _in(s_h, s_m, e_h, e_m):
            """Rango con soporte a cruce de medianoche."""
            s = s_h * 60 + s_m
            e = e_h * 60 + e_m
            if s <= e:
                return s <= mins < e
            return mins >= s or mins < e

        # ── Sesión principal ──────────────────────────────────────────────────
        if _in(19, 0,  4, 0):
            session = "Asia"
        elif _in(2, 0, 11, 0):
            session = "London"
        elif _in(8, 0, 17, 0):
            session = "NY"
        else:
            session = "OFF"

        # ── Kill Zone ─────────────────────────────────────────────────────────
        in_kz = _in(2, 0, 5, 0) or _in(8, 0, 11, 0)

        return {
            "session":      session,
            "in_kill_zone": in_kz,
            "time_utc":     now_utc.strftime("%H:%M UTC"),
            "time_local":   now_local.strftime("%H:%M"),
        }

    # =========================================================================
    # CHECKLIST DE SETUP
    # =========================================================================

    @staticmethod
    def _determine_setup(state: dict) -> tuple:
        """
        Aplica el algoritmo SMC y retorna (setup_type, details).

        Algoritmo:
          1. ¿Estamos en Kill Zone?          → NO  : WAIT
          2. ¿Hay estructura clara (bias)?   → NO  : NO_TRADE
          3. ¿Hay CHOCH + OB + FVG?          → SÍ  : CONFIRMED
          4. ¿Hay CHOCH + OB (sin FVG)?      → SÍ  : AGGRESSIVE
          5. ¿Hay BOS en dirección del bias + OB? → CONFIRMED
          6. ¿Precio dentro de OB activo?    → SÍ  : AGGRESSIVE
          7. Ninguna condición cumplida      → WAIT
        """
        session = state["session"]
        bias    = state["bias"]
        bos     = state["bos"]
        choch   = state["choch"]
        obs     = state["order_blocks"]
        fvgs    = state["fvg_zones"]
        price   = state["current_price"]

        # 1. Kill Zone
        if not session["in_kill_zone"]:
            return "WAIT", (
                f"Fuera de Kill Zone ({session['time_utc']}). "
                "Próximas: London 08:00 UTC | NY 13:30 UTC."
            )

        # 2. Bias
        if bias == "NEUTRAL":
            return "NO_TRADE", (
                "Estructura mixta (sin bias claro). "
                "Esperar a que el precio defina HH+HL o LH+LL."
            )

        ob_side  = "BULL" if bias == "LONG" else "BEAR"
        act_obs  = [o for o in obs  if o["type"] == ob_side and o["active"]]
        act_fvgs = [f for f in fvgs if f["type"] == ob_side and not f["filled"]]

        # 3–4. CHOCH (cambio de carácter → setup de reversión)
        if choch:
            if act_obs and act_fvgs:
                ob, fvg = act_obs[0], act_fvgs[0]
                return "CONFIRMED", (
                    f"CHOCH {choch['type']} @ {choch['price']} | "
                    f"Bias: {bias} | "
                    f"OB POI: {ob['low']}–{ob['high']} | "
                    f"FVG: {fvg['bottom']}–{fvg['top']} | "
                    "Esperar retroceso OTE (61.8–78.6%) al OB/FVG."
                )
            if act_obs:
                ob = act_obs[0]
                return "AGGRESSIVE", (
                    f"CHOCH {choch['type']} @ {choch['price']} | "
                    f"Bias: {bias} | "
                    f"OB (POI): {ob['low']}–{ob['high']} | "
                    "Entrada agresiva al llegar al OB."
                )

        # 5. BOS (continuación) + OB
        if bos:
            bos_dir = "LONG" if "BULL" in bos["type"] else "SHORT"
            if bos_dir == bias and act_obs:
                ob = act_obs[0]
                return "CONFIRMED", (
                    f"BOS {bos['type']} @ {bos['price']} (continuación) | "
                    f"OB: {ob['low']}–{ob['high']} | "
                    "Esperar pullback al OB."
                )

        # 6. Precio dentro de OB activo
        for ob in act_obs:
            if ob["low"] <= price <= ob["high"]:
                return "AGGRESSIVE", (
                    f"Precio dentro de {ob_side} OB ({ob['low']}–{ob['high']}) | "
                    f"Bias: {bias} | Entrada agresiva activa."
                )

        # 7. Ninguna condición
        liq_target = (state["eqh"][-1] if bias == "LONG" and state["eqh"]
                      else state["eql"][-1] if state["eql"] else "N/A")
        return "WAIT", (
            f"Bias: {bias} | Sesión: {session['session']} | "
            f"Sin POI alcanzado. "
            f"Liquidez objetivo: {liq_target}. "
            "Esperar sweep de liquidez + retorno a OB."
        )
