import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timezone, timedelta
from config import MAGIC_NUMBER, ORDER_DEVIATION, BROKER_UTC_OFFSET, LOCAL_UTC_OFFSET
from logger_service import LoggerService

class MT5Service:
    def __init__(self, config=None):
        """
        Inicializa MT5Service.

        Args:
            config: ConfigLoader instance (para distribución comercial).
                   Si es None, usa valores de config.py.
        """
        self.config = config
        if config is not None:
            self.login = config.mt5_login
            self.password = config.mt5_password
            self.server = config.mt5_server
            self.broker_utc_offset = config.broker_utc_offset
            self.local_utc_offset = config.local_utc_offset
        else:
            # Para desarrollo: importar desde config.py
            from config import LOGIN, PASSWORD, SERVER
            self.login = LOGIN
            self.password = PASSWORD
            self.server = SERVER
            self.broker_utc_offset = BROKER_UTC_OFFSET
            self.local_utc_offset = LOCAL_UTC_OFFSET

    def connect(self):
        if not mt5.initialize(login=self.login, password=self.password, server=self.server):
            return False, mt5.last_error()
        return True, "Conectado"

    def get_account(self):
        return mt5.account_info()

    def get_positions(self):
        positions = mt5.positions_get()
        if not positions: return pd.DataFrame()
        df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
        df['type_name'] = df['type'].apply(lambda x: 'BUY' if x == 0 else 'SELL')
        return df

    def get_times(self) -> dict:
        """
        Retorna las tres horas relevantes para el bot:
          - utc_dt    : hora UTC real del sistema operativo (siempre correcta)
          - broker_dt : hora del servidor del broker (UTC + BROKER_UTC_OFFSET)
          - col_dt    : hora Colombia (UTC-5, sin DST)

        NOTA: usamos datetime.now(UTC) del OS como fuente de verdad.
        tick.time de MT5 puede ser hora del broker codificada como timestamp,
        no UTC puro — no es fiable para cálculos de zona horaria.
        """
        utc_dt    = datetime.now(timezone.utc)
        broker_dt = utc_dt + timedelta(hours=self.broker_utc_offset)
        local_dt  = utc_dt + timedelta(hours=self.local_utc_offset)

        return {
            "utc":    utc_dt,
            "broker": broker_dt,
            "local":  local_dt,
        }

    def get_spread(self, symbol: str) -> float:
        """Retorna el spread actual en puntos (entero). 0.0 si no disponible."""
        tick = mt5.symbol_info_tick(symbol)
        info = mt5.symbol_info(symbol)
        if tick is None or info is None or info.point == 0:
            return 0.0
        return round((tick.ask - tick.bid) / info.point, 1)

    def get_pip_value_per_lot(self, symbol: str) -> float:
        """
        Retorna el valor USD por pip por lote estándar para el símbolo dado.
        Fórmula: tick_value / tick_size × pip_size
        """
        info = mt5.symbol_info(symbol)
        if not info:
            return 10.0  # fallback conservador (eurusd ~$10/pip/lot)
        # pip_size = 10 × point para pares de 4 decimales / 2 decimales
        pip_size = info.point * 10
        if info.trade_tick_size == 0:
            return 10.0
        return round((info.trade_tick_value / info.trade_tick_size) * pip_size, 4)

    def send_order(self, symbol, action, lot, sl_pips, tp_pips):
        mt5.symbol_select(symbol, True)
        tick = mt5.symbol_info_tick(symbol)
        point = mt5.symbol_info(symbol).point
        price = tick.ask if action == 'BUY' else tick.bid
        
        sl = price - (sl_pips * 10 * point) if action == 'BUY' else price + (sl_pips * 10 * point)
        tp = price + (tp_pips * 10 * point) if action == 'BUY' else price - (tp_pips * 10 * point)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(lot),
            "type": mt5.ORDER_TYPE_BUY if action == 'BUY' else mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": float(sl) if sl_pips > 0 else 0.0,
            "tp": float(tp) if tp_pips > 0 else 0.0,
            "deviation": ORDER_DEVIATION,
            "magic": MAGIC_NUMBER,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        res = mt5.order_send(request)
        status = "OK" if res.retcode == mt5.TRADE_RETCODE_DONE else "ERROR"
        LoggerService.log_event(res.order, symbol, action, lot, price, status, res.comment)
        return res

    def modify_sl(self, ticket: int, new_sl: float):
        """
        Modifica el Stop Loss de una posición abierta sin tocar el TP.
        Usa TRADE_ACTION_SLTP que solo actualiza niveles sin re-ejecutar.
        """
        pos_list = mt5.positions_get(ticket=ticket)
        if not pos_list:
            return None
        pos = pos_list[0]
        request = {
            "action":   mt5.TRADE_ACTION_SLTP,
            "symbol":   pos.symbol,
            "sl":       float(new_sl),
            "tp":       float(pos.tp),
            "position": ticket,
        }
        return mt5.order_send(request)

    def get_h1_atr(self, symbol: str) -> float:
        """ATR(14) de H1 para cálculo de trailing stop dinámico."""
        import pandas_ta as ta
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 20)
        if rates is None or len(rates) < 15:
            return 0.0
        df = pd.DataFrame(rates)
        df.ta.atr(length=14, append=True)
        val = df["ATRr_14"].iloc[-2]
        return float(val) if pd.notna(val) else 0.0

    def close_position(self, ticket):
        pos_list = mt5.positions_get(ticket=int(ticket))
        if not pos_list:
            return None
        pos  = pos_list[0]
        tick = mt5.symbol_info_tick(pos.symbol)
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY,
            "position": pos.ticket,
            "price": tick.bid if pos.type == 0 else tick.ask,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        # Capturamos el profit ANTES de enviar la orden (pos.profit = P&L flotante)
        realized_profit = round(pos.profit, 2)
        res = mt5.order_send(request)
        if res.retcode == mt5.TRADE_RETCODE_DONE:
            LoggerService.log_event(
                ticket, pos.symbol, "CLOSE", pos.volume, res.price,
                "CLOSED", profit=realized_profit
            )
        return res