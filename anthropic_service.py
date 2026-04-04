"""
Anthropic Service — Análisis de trading con IA institucional.

Modelo: claude-sonnet-4-6 (el más capaz de la familia Claude 4, Abril 2026).
Nota: los alias "latest" (ej. claude-3-5-sonnet-latest) fueron deprecados
en 2025 y producen HTTP 404. Siempre usar IDs completos con fecha/versión.
"""

import anthropic
import json
import os
import time
from dotenv import load_dotenv

load_dotenv(override=True)  # override=True: sobreescribe vars de entorno vacías del sistema

# JSON schema que la IA DEBE respetar (se inyecta en el system prompt)
_RESPONSE_SCHEMA = """{
  "decision":          "BUY | SELL | HOLD",
  "logic_path":        "razonamiento paso a paso: macro → técnico → entrada",
  "risk_reward_ratio": <float, ej. 2.5 significa RR 1:2.5>,
  "position_size":     <float 0.0–1.0, fracción del riesgo máximo a aplicar>,
  "confidence":        <float 0.0–1.0>,
  "sl_pips":           <integer>,
  "tp_pips":           <integer>,
  "reasoning":         "resumen ejecutivo de una línea"
}"""

_SYSTEM_PROMPT = f"""You are an Institutional Smart Money trader at a Tier-1 prop firm.
Your methodology is Smart Money Concepts (SMC): price moves from liquidity to liquidity,
driven by institutional order flow. You never trade against structure.

SMC ANALYSIS FRAMEWORK — apply in this exact order:

1. MACRO BIAS (D1):
   - Is price above or below EMA200? → determines bull/bear bias.
   - Is price above PDH or below PDL? → confirms intraday directional bias.
   - What is the D1 swing structure (HH+HL = bullish / LH+LL = bearish)?

2. LIQUIDITY CONTEXT (H1):
   - Identify nearest BSL (Buy-Side Liquidity): EQH, PDH, PWH (targets for shorts → inducement).
   - Identify nearest SSL (Sell-Side Liquidity): EQL, PDL, PWL (targets for longs → inducement).
   - Rule: price takes nearest liquidity FIRST. Confirm which side was swept.

3. STRUCTURAL EVENT (H1):
   - BOS (Break of Structure) = trend continuation signal.
   - CHOCH (Change of Character) = potential reversal signal.
   - Only trade AFTER a liquidity sweep + BOS/CHOCH confirmation.

4. POINT OF INTEREST — ENTRY (H1):
   Entry A — AGGRESSIVE: liquidity swept + price at Order Block (OB).
   Entry B — CONFIRMED : liquidity swept + CHOCH + FVG present + OTE retrace (61.8–78.6%).
   Never enter mid-range. Wait for price to return to POI.

5. SESSION FILTER:
   - Only trade during Kill Zones: London (08:00–12:00 UTC) or NY (13:30–17:00 UTC).
   - Asia (00:00–04:00 UTC) = accumulation / mark EQH-EQL. Do NOT trade Asia breakouts.

6. RISK / REWARD:
   - SL: below/above the OB or the candle that caused CHOCH (never arbitrary pips).
   - TP: next liquidity level (EQH/EQL, PDH/PDL, PWH/PWL).
   - Minimum RR: 1:2. If RR < 1.5 → output HOLD.

INVALIDATION RULES (output HOLD if any of these are true):
   - Outside Kill Zone.
   - No clear BOS or CHOCH after liquidity sweep.
   - Price is mid-range with no POI.
   - Bias from D1 conflicts with entry direction.
   - 2 losses already taken this session.

OUTPUT RULES — CRITICAL:
- Return ONLY a raw JSON object. No markdown, no backticks, no prose before or after.
- Adhere strictly to this schema:
{_RESPONSE_SCHEMA}
- logic_path: exactly 3 numbered steps → 1) Macro+Liquidity, 2) Structure+POI, 3) Entry+RR.
- sl_pips and tp_pips must be derived from the OB/structure, not arbitrary values.
- confidence above 0.85 triggers autonomous execution. Be conservative — only set ≥0.85
  when ALL 6 framework steps align perfectly."""


class AnthropicService:
    # claude-haiku-4-5-20251001: confirmado funcional en Abril 2026, económico ($5 budget).
    # Para mayor calidad usar "claude-sonnet-4-6" si el tier lo permite.
    MODEL = "claude-haiku-4-5-20251001"
    MAX_TOKENS = 500
    TIMEOUT_RETRIES = 2
    RETRY_DELAY = 2  # segundos entre reintentos

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def get_strategy_decision(
        self,
        symbol: str,
        mtf_data: dict,
        account_data,
        lang: str = "es",
        smc_state: dict = None,
        session_losses: int = 0,
        spread_pts: float = 0.0,
        feedback_block: str = "",
        fundamental_block: str = "",
    ) -> dict:
        """
        Analiza el mercado con contexto multi-temporalidad y retorna una decisión JSON.

        Args:
            symbol:       Nombre del par (ej. "EURUSD").
            mtf_data:     Resultado de IndicatorsService.get_multi_timeframe_state().
            account_data: Objeto mt5.account_info().
            lang:         "es" (español) o "en" (English). Controla el idioma de
                          los campos 'logic_path' y 'reasoning' en la respuesta.
        Returns:
            dict con las claves definidas en _RESPONSE_SCHEMA.
        """
        user_content = self._build_prompt(
            symbol, mtf_data, account_data, lang, smc_state,
            session_losses=session_losses, spread_pts=spread_pts,
            feedback_block=feedback_block,
            fundamental_block=fundamental_block,
        )
        last_error_msg = "Error desconocido"
        raw_text = ""

        for attempt in range(self.TIMEOUT_RETRIES + 1):
            try:
                response = self.client.messages.create(
                    model=self.MODEL,
                    max_tokens=self.MAX_TOKENS,
                    system=_SYSTEM_PROMPT,
                    # Assistant prefill: fuerza al modelo a iniciar con "{",
                    # garantizando JSON puro sin texto introductorio.
                    messages=[
                        {"role": "user",      "content": user_content},
                        {"role": "assistant", "content": "{"},
                    ],
                )

                # El modelo devuelve el cuerpo del JSON (sin el "{" inicial)
                raw_text = "{" + response.content[0].text.strip()
                result = json.loads(raw_text)
                return self._validate_and_fill(result)

            except json.JSONDecodeError as e:
                last_error_msg = f"JSON inválido: {e} | Texto recibido: {raw_text[:200]}"
                print(f"[AnthropicService] Intento {attempt + 1} — {last_error_msg}")
                if attempt < self.TIMEOUT_RETRIES:
                    time.sleep(self.RETRY_DELAY)

            except anthropic.APITimeoutError as e:
                last_error_msg = f"Timeout de red: {e}"
                print(f"[AnthropicService] Intento {attempt + 1} — {last_error_msg}")
                if attempt < self.TIMEOUT_RETRIES:
                    time.sleep(self.RETRY_DELAY)

            except anthropic.APIStatusError as e:
                # Guardamos código HTTP + mensaje para diagnóstico visible en la UI
                last_error_msg = f"HTTP {e.status_code} — {e.message}"
                print(f"[AnthropicService] Intento {attempt + 1} — {last_error_msg}")
                # Solo reintentar errores de servidor (5xx); 4xx son definitivos
                if e.status_code >= 500 and attempt < self.TIMEOUT_RETRIES:
                    time.sleep(self.RETRY_DELAY)
                else:
                    break

            except Exception as e:
                last_error_msg = f"{type(e).__name__}: {e}"
                print(f"[AnthropicService] Intento {attempt + 1} — Error inesperado: {last_error_msg}")
                break

        return self._error_response(last_error_msg)

    # -------------------------------------------------------------------------
    # HELPERS PRIVADOS
    # -------------------------------------------------------------------------

    @staticmethod
    def _build_prompt(
        symbol: str,
        mtf_data: dict,
        account_data,
        lang: str = "es",
        smc_state: dict = None,
        session_losses: int = 0,
        spread_pts: float = 0.0,
        feedback_block: str = "",
        fundamental_block: str = "",
    ) -> str:
        """Construye el mensaje con datos multi-TF + contexto SMC completo."""
        from i18n import get_translations
        t = get_translations(lang)

        d1  = mtf_data.get("d1",  {})
        h1  = mtf_data.get("h1",  {})
        m15 = mtf_data.get("m15", {})

        macro = (
            f"D1 MACRO — Trend: {d1.get('trend','N/A')} | "
            f"Price: {d1.get('close','N/A')} | EMA200: {d1.get('ema200','N/A')} | "
            f"RSI: {d1.get('rsi','N/A')} | ATR: {d1.get('atr','N/A')}"
        )
        technical = (
            f"H1 TECHNICAL — Trend: {h1.get('trend','N/A')} | "
            f"EMA20: {h1.get('ema20','N/A')} | EMA50: {h1.get('ema50','N/A')} | "
            f"RSI: {h1.get('rsi','N/A')} | ATR: {h1.get('atr','N/A')} | "
            f"MACD: {h1.get('macd','N/A')} | Signal: {h1.get('macd_signal','N/A')}"
        )
        entry = (
            f"M15 ENTRY — Momentum: {m15.get('momentum','N/A')} | "
            f"Price: {m15.get('close','N/A')} | EMA9: {m15.get('ema9','N/A')} | "
            f"RSI: {m15.get('rsi','N/A')} | ATR: {m15.get('atr','N/A')}"
        )
        account = (
            f"ACCOUNT — Equity: ${account_data.equity:,.2f} | "
            f"Balance: ${account_data.balance:,.2f} | "
            f"Open P&L: ${account_data.profit:,.2f}"
        )
        session_ctx = (
            f"SESSION CONTEXT — Losses today: {session_losses} | "
            f"Current spread: {spread_pts:.1f} pts"
        )

        # Bloque SMC (si está disponible)
        smc_block = ""
        if smc_state and not smc_state.get("error"):
            obs_str  = " | ".join(
                f"{o['type']} OB {o['low']}–{o['high']}"
                for o in smc_state.get("order_blocks", [])[:2]
            ) or "None"
            fvg_str  = " | ".join(
                f"{f['type']} FVG {f['bottom']}–{f['top']}"
                for f in smc_state.get("fvg_zones", [])[:2]
            ) or "None"
            bos_txt  = (f"{smc_state['bos']['type']} @ {smc_state['bos']['price']}"
                        if smc_state.get("bos") else "None")
            choch_txt = (f"{smc_state['choch']['type']} @ {smc_state['choch']['price']}"
                         if smc_state.get("choch") else "None")
            smc_block = (
                f"\nSMC CONTEXT (H1):\n"
                f"  Structure : {smc_state.get('structure','N/A')} "
                f"({', '.join(smc_state.get('swing_labels',[]))})\n"
                f"  BOS       : {bos_txt}\n"
                f"  CHOCH     : {choch_txt}\n"
                f"  Order Blocks: {obs_str}\n"
                f"  FVG Zones : {fvg_str}\n"
                f"  EQH (BSL) : {smc_state.get('eqh', [])}\n"
                f"  EQL (SSL) : {smc_state.get('eql', [])}\n"
                f"  PDH/PDL   : {smc_state.get('pdh','N/A')} / {smc_state.get('pdl','N/A')}\n"
                f"  PWH/PWL   : {smc_state.get('pwh','N/A')} / {smc_state.get('pwl','N/A')}\n"
                f"  Session   : {smc_state['session']['session']} "
                f"({'Kill Zone ACTIVE' if smc_state['session']['in_kill_zone'] else 'Outside KZ'})\n"
                f"  SMC Bias  : {smc_state.get('bias','N/A')}\n"
                f"  Setup     : {smc_state.get('setup','N/A')} — {smc_state.get('setup_details','')}"
            )

        feedback_section     = f"\n{feedback_block}\n"     if feedback_block     else ""
        fundamental_section  = f"\n{fundamental_block}\n"  if fundamental_block  else ""

        return (
            f"INSTRUMENT: {symbol}\n\n"
            f"{macro}\n{technical}\n{entry}\n"
            f"{smc_block}\n\n"
            f"{account}\n"
            f"{session_ctx}\n"
            f"{fundamental_section}"
            f"{feedback_section}\n"
            f"{t['ai_lang_instruction']}\n\n"
            "Provide your institutional SMC trade decision as a JSON object."
        )

    @staticmethod
    def _validate_and_fill(data: dict) -> dict:
        """Asegura que todos los campos requeridos existen con tipos correctos."""
        defaults = {
            "decision":          "HOLD",
            "logic_path":        "No logic path provided.",
            "risk_reward_ratio": 0.0,
            "position_size":     0.5,
            "confidence":        0.0,
            "sl_pips":           0,
            "tp_pips":           0,
            "reasoning":         "No reasoning provided.",
        }
        for key, default in defaults.items():
            if key not in data:
                data[key] = default

        # Normalizar tipos
        data["sl_pips"]           = int(data["sl_pips"])
        data["tp_pips"]           = int(data["tp_pips"])
        data["confidence"]        = float(data["confidence"])
        data["risk_reward_ratio"] = float(data["risk_reward_ratio"])
        data["position_size"]     = float(data["position_size"])
        data["decision"]          = str(data["decision"]).upper()
        return data

    @staticmethod
    def _error_response(reason: str) -> dict:
        return {
            "decision":          "HOLD",
            "logic_path":        f"Error: {reason}",
            "risk_reward_ratio": 0.0,
            "position_size":     0.0,
            "confidence":        0.0,
            "sl_pips":           0,
            "tp_pips":           0,
            "reasoning":         f"Error Técnico: {reason}",
        }
