from mt5_service import MT5Service
from indicators_service import IndicatorsService
import MetaTrader5 as mt5

# 1. Conectar
service = MT5Service()
service.connect()

# 2. Obtener datos procesados
symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_H1

print(f"--- Analizando {symbol} ---")
state = IndicatorsService.get_current_state(symbol, timeframe)

if state:
    print(f"Precio Cierre: {state['close']}")
    print(f"RSI (14):      {state['RSI_14']:.2f}")
    print(f"EMA 20:        {state['EMA_20']:.5f}")
    print(f"EMA 50:        {state['EMA_50']:.5f}")
    print(f"Volatilidad (ATR): {state['ATRr_14']:.5f}")
else:
    print("No se pudieron obtener indicadores.")

mt5.shutdown()