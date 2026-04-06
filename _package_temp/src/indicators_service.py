import MetaTrader5 as mt5
import pandas as pd
import pandas_ta as ta


class IndicatorsService:
    # -------------------------------------------------------------------------
    # API PÚBLICA PRINCIPAL
    # -------------------------------------------------------------------------

    @staticmethod
    def get_multi_timeframe_state(symbol: str) -> dict:
        """
        Retorna un diccionario con contexto técnico de tres temporalidades:
          - D1  : dirección macro (EMA200, RSI, ATR)
          - H1  : contexto técnico principal (EMA20/50, RSI, ATR, MACD)
          - M15 : precisión de entrada (RSI, EMA9, ATR)

        Estructura de retorno:
        {
            "symbol": str,
            "d1":  { "close", "ema200", "trend", "rsi", "atr" },
            "h1":  { "close", "ema20", "ema50", "trend", "rsi", "atr",
                     "macd", "macd_signal", "macd_hist" },
            "m15": { "close", "ema9", "rsi", "atr" }
        }
        """
        d1_state  = IndicatorsService._get_d1(symbol)
        h1_state  = IndicatorsService._get_h1(symbol)
        m15_state = IndicatorsService._get_m15(symbol)

        return {
            "symbol": symbol,
            "d1":  d1_state,
            "h1":  h1_state,
            "m15": m15_state,
        }

    # Retrocompatibilidad: mantiene la firma original para no romper nada
    @staticmethod
    def get_current_state(symbol: str, timeframe) -> dict:
        """Wrapper de compatibilidad. Devuelve la vela cerrada de la TF dada."""
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 100)
        if rates is None or len(rates) < 50:
            return {}
        df = IndicatorsService._build_df(rates)
        df.ta.rsi(length=14, append=True)
        df.ta.ema(length=20, append=True)
        df.ta.ema(length=50, append=True)
        df.ta.atr(length=14, append=True)
        df.ta.macd(append=True)
        return df.iloc[-2].to_dict()

    # -------------------------------------------------------------------------
    # TEMPORALIDADES INTERNAS
    # -------------------------------------------------------------------------

    @staticmethod
    def _build_df(rates) -> pd.DataFrame:
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    @staticmethod
    def _safe_float(series, idx=-2) -> float:
        """Extrae un float de una columna, devuelve 0.0 si no existe o es NaN."""
        try:
            val = series.iloc[idx]
            return float(val) if pd.notna(val) else 0.0
        except Exception:
            return 0.0

    @staticmethod
    def _get_d1(symbol: str) -> dict:
        """
        D1 — Contexto macro.
        Indicadores: EMA200 (dirección institucional), RSI14, ATR14.
        Necesita 250 velas para que EMA200 esté estabilizada.
        """
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_D1, 0, 250)
        if rates is None or len(rates) < 210:
            return {}

        df = IndicatorsService._build_df(rates)
        df.ta.ema(length=200, append=True)
        df.ta.rsi(length=14, append=True)
        df.ta.atr(length=14, append=True)

        close   = IndicatorsService._safe_float(df['close'])
        ema200  = IndicatorsService._safe_float(df.get('EMA_200', pd.Series([0])))
        rsi     = IndicatorsService._safe_float(df.get('RSI_14',  pd.Series([50])))
        atr     = IndicatorsService._safe_float(df.get('ATRr_14', pd.Series([0])))

        return {
            "close":  round(close,  5),
            "ema200": round(ema200, 5),
            "trend":  "UP" if close > ema200 > 0 else "DOWN",
            "rsi":    round(rsi, 2),
            "atr":    round(atr, 5),
        }

    @staticmethod
    def _get_h1(symbol: str) -> dict:
        """
        H1 — Contexto técnico principal.
        Indicadores: EMA20, EMA50, RSI14, ATR14, MACD(12,26,9).
        """
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 150)
        if rates is None or len(rates) < 60:
            return {}

        df = IndicatorsService._build_df(rates)
        df.ta.ema(length=20, append=True)
        df.ta.ema(length=50, append=True)
        df.ta.rsi(length=14, append=True)
        df.ta.atr(length=14, append=True)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)

        close       = IndicatorsService._safe_float(df['close'])
        ema20       = IndicatorsService._safe_float(df.get('EMA_20',      pd.Series([0])))
        ema50       = IndicatorsService._safe_float(df.get('EMA_50',      pd.Series([0])))
        rsi         = IndicatorsService._safe_float(df.get('RSI_14',      pd.Series([50])))
        atr         = IndicatorsService._safe_float(df.get('ATRr_14',     pd.Series([0])))
        macd        = IndicatorsService._safe_float(df.get('MACD_12_26_9',  pd.Series([0])))
        macd_signal = IndicatorsService._safe_float(df.get('MACDs_12_26_9', pd.Series([0])))
        macd_hist   = IndicatorsService._safe_float(df.get('MACDh_12_26_9', pd.Series([0])))

        return {
            "close":       round(close,       5),
            "ema20":       round(ema20,        5),
            "ema50":       round(ema50,        5),
            "trend":       "UP" if ema20 > ema50 > 0 else "DOWN",
            "rsi":         round(rsi,          2),
            "atr":         round(atr,          5),
            "macd":        round(macd,         5),
            "macd_signal": round(macd_signal,  5),
            "macd_hist":   round(macd_hist,    5),
        }

    @staticmethod
    def _get_m15(symbol: str) -> dict:
        """
        M15 — Precisión de entrada.
        Indicadores: EMA9 (momentum rápido), RSI14, ATR14.
        """
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 100)
        if rates is None or len(rates) < 20:
            return {}

        df = IndicatorsService._build_df(rates)
        df.ta.ema(length=9, append=True)
        df.ta.rsi(length=14, append=True)
        df.ta.atr(length=14, append=True)

        close = IndicatorsService._safe_float(df['close'])
        ema9  = IndicatorsService._safe_float(df.get('EMA_9',   pd.Series([0])))
        rsi   = IndicatorsService._safe_float(df.get('RSI_14',  pd.Series([50])))
        atr   = IndicatorsService._safe_float(df.get('ATRr_14', pd.Series([0])))

        return {
            "close": round(close, 5),
            "ema9":  round(ema9,  5),
            "rsi":   round(rsi,   2),
            "atr":   round(atr,   5),
            "momentum": "BULLISH" if close > ema9 > 0 else "BEARISH",
        }
