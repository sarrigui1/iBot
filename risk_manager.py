"""
Risk Manager — Gestión de riesgo institucional para el Trading Bot MT5.
Responsabilidades:
  - Cálculo de tamaño de lote basado en % de riesgo y ATR
  - Trailing Stop dinámico (ATR-based)
  - Break Even automático
"""


class RiskManager:
    MIN_LOT = 0.01
    MAX_LOT = 2.0
    DEFAULT_RISK_PCT = 1.0      # 1% de la cuenta por operación
    TRAIL_ATR_MULT = 1.5        # multiplicador ATR para trailing stop
    BE_ATR_MULT = 1.0           # mover a BE cuando el precio avanza 1x ATR

    # -------------------------------------------------------------------------
    # POSITION SIZING
    # -------------------------------------------------------------------------

    @staticmethod
    def calculate_lot_size(
        equity: float,
        risk_pct: float,
        sl_pips: float,
        pip_value_per_lot: float,
    ) -> float:
        """
        Calcula el tamaño de lote óptimo basándose en riesgo fijo.

        Fórmula: lot = (equity × risk_pct%) / (sl_pips × pip_value_per_lot)

        Args:
            equity: Saldo de la cuenta en USD.
            risk_pct: Porcentaje de riesgo (ej. 1.0 = 1%).
            sl_pips: Distancia del Stop Loss en pips.
            pip_value_per_lot: Valor USD por pip para un lote estándar
                               (obténlo de mt5.symbol_info(symbol).trade_tick_value
                                × 10 / mt5.symbol_info(symbol).trade_tick_size).
        Returns:
            Tamaño de lote redondeado a 2 decimales, entre MIN_LOT y MAX_LOT.
        """
        if sl_pips <= 0 or pip_value_per_lot <= 0 or equity <= 0:
            return RiskManager.MIN_LOT

        risk_amount = equity * (risk_pct / 100.0)
        lot = risk_amount / (sl_pips * pip_value_per_lot)
        lot = max(RiskManager.MIN_LOT, min(RiskManager.MAX_LOT, lot))
        return round(lot, 2)

    @staticmethod
    def atr_to_sl_pips(atr: float, multiplier: float = 1.5) -> float:
        """
        Convierte un valor ATR (en precio) a pips de Stop Loss.
        Detección automática de pip_size por magnitud del ATR:
          - ATR < 0.1   → forex 4 dec (EURUSD, etc.)  pip = 0.0001
          - ATR < 5     → forex 2 dec (USDJPY)          pip = 0.01
          - ATR >= 5    → metales/cripto (XAUUSD, BTC)  pip = 0.01
        Para XAU: ATR ~3-10 → pip=0.01 → SL ≈ ATR×mult/0.01 pips (correcto).
        """
        if atr <= 0:
            return 20.0  # fallback conservador

        if atr < 0.1:
            pip_size = 0.0001   # forex majors (EURUSD, GBPUSD, …)
        else:
            pip_size = 0.01     # JPY pairs, XAU, BTC (all use 0.01 pip)

        return round((atr * multiplier) / pip_size, 1)

    # -------------------------------------------------------------------------
    # SAFETY GATES — Motor de decisión
    # -------------------------------------------------------------------------

    @staticmethod
    def is_spread_ok(spread_pts: float, max_pts: float) -> bool:
        """True si el spread actual es aceptable para operar."""
        return spread_pts <= max_pts

    @staticmethod
    def has_open_position(df_positions, symbol: str, direction: str) -> bool:
        """
        True si ya existe una posición en el mismo símbolo Y misma dirección.
        Previene sobreexposición / duplicación de señales.
        """
        if df_positions is None or df_positions.empty:
            return False
        sym_pos = df_positions[df_positions["symbol"] == symbol]
        if sym_pos.empty:
            return False
        direction_type = 0 if direction == "BUY" else 1
        return (sym_pos["type"] == direction_type).any()

    @staticmethod
    def get_session_loss_count(history_df) -> int:
        """
        Cuenta las operaciones cerradas con pérdida en la sesión de trading actual
        (desde medianoche UTC del día actual). Requiere columnas 'fecha' y 'profit'.
        """
        if history_df is None or history_df.empty:
            return 0
        try:
            from datetime import datetime, timezone
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            closed = history_df[history_df.get("accion", pd.Series()) == "CLOSE"].copy()
            if closed.empty:
                return 0
            closed["profit"] = pd.to_numeric(closed["profit"], errors="coerce")
            today_losses = closed[
                closed["fecha"].str.startswith(today) & (closed["profit"] < 0)
            ]
            return len(today_losses)
        except Exception:
            return 0

    @staticmethod
    def is_daily_loss_limit_exceeded(history_df, balance: float, max_pct: float) -> bool:
        """
        True si la pérdida acumulada hoy supera max_pct% del balance.
        Ejemplo: balance=10000, max_pct=3.0 → bloquea si pérdidas del día > $300.
        """
        if history_df is None or history_df.empty or balance <= 0:
            return False
        try:
            from datetime import datetime, timezone
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            closed = history_df[history_df.get("accion", pd.Series()) == "CLOSE"].copy()
            if closed.empty:
                return False
            closed["profit"] = pd.to_numeric(closed["profit"], errors="coerce")
            daily_pnl = closed[closed["fecha"].str.startswith(today)]["profit"].sum()
            return daily_pnl < -(balance * max_pct / 100.0)
        except Exception:
            return False

    # -------------------------------------------------------------------------
    # TRAILING STOP
    # -------------------------------------------------------------------------

    @staticmethod
    def should_trail_stop(
        current_price: float,
        current_sl: float,
        action: str,
        atr: float,
        multiplier: float = None,
    ) -> tuple[bool, float]:
        """
        Determina si hay que actualizar el Stop Loss de seguimiento.

        El trailing stop sigue al precio manteniéndose a `multiplier × ATR`
        de distancia en la dirección favorable.

        Returns:
            (debe_actualizar: bool, nuevo_sl: float)
        """
        mult = multiplier if multiplier is not None else RiskManager.TRAIL_ATR_MULT
        trail_dist = atr * mult

        if action == 'BUY':
            candidate_sl = round(current_price - trail_dist, 5)
            if candidate_sl > current_sl:
                return True, candidate_sl
        else:  # SELL
            candidate_sl = round(current_price + trail_dist, 5)
            if current_sl == 0 or candidate_sl < current_sl:
                return True, candidate_sl

        return False, current_sl

    # -------------------------------------------------------------------------
    # BREAK EVEN
    # -------------------------------------------------------------------------

    @staticmethod
    def should_break_even(
        current_price: float,
        open_price: float,
        current_sl: float,
        action: str,
        atr: float,
        multiplier: float = None,
    ) -> tuple[bool, float]:
        """
        Determina si hay que mover el SL al precio de apertura (break even).

        Condición: el precio ha avanzado al menos `multiplier × ATR` en la
        dirección favorable Y el SL actual todavía está en pérdida.

        Returns:
            (debe_mover: bool, precio_be: float)
        """
        mult = multiplier if multiplier is not None else RiskManager.BE_ATR_MULT
        threshold = atr * mult

        if action == 'BUY':
            in_profit = current_price > open_price
            enough_room = (current_price - open_price) >= threshold
            sl_still_losing = current_sl < open_price
        else:  # SELL
            in_profit = current_price < open_price
            enough_room = (open_price - current_price) >= threshold
            sl_still_losing = current_sl > open_price or current_sl == 0

        if in_profit and enough_room and sl_still_losing:
            return True, open_price

        return False, open_price
