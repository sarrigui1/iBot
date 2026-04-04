"""
FeedbackService -Sistema de aprendizaje incremental para iBot.

El modelo de IA (Claude) es stateless: no recuerda conversaciones anteriores.
Este servicio compensa eso construyendo un bloque de contexto de rendimiento
histórico que se inyecta en cada prompt, permitiendo que la IA calibre su
confianza basándose en qué condiciones han funcionado REALMENTE en el pasado.

Flujo:
  1. Al abrir una operación -> log_trade_context(ticket, sesión, setup, confianza AI)
  2. Al cerrar -> update_memory()  (re-analiza todo el historial)
  3. Antes de llamar a la IA -> build_prompt_block()  (inject en el prompt)

Archivos generados:
  trade_context.csv    -> contexto de cada trade al abrir (sesión, setup, confianza)
  strategy_memory.json -> estadísticas acumuladas de rendimiento
"""

import json
import os
import pandas as pd
from datetime import datetime


class FeedbackService:
    CONTEXT_FILE = "trade_context.csv"
    MEMORY_FILE  = "strategy_memory.json"

    CONTEXT_COLUMNS = [
        "fecha_open", "ticket", "simbolo", "direccion",
        "sesion", "setup", "ai_confidence", "planned_rr",
        "sl_pips", "tp_pips",
    ]

    # =========================================================================
    # 1. REGISTRAR CONTEXTO AL ABRIR TRADE
    # =========================================================================

    @classmethod
    def log_trade_context(
        cls,
        ticket: int,
        symbol: str,
        direction: str,
        smc_state: dict,
        ai_res: dict,
    ):
        """
        Guarda el contexto de la IA en el momento en que se abre la operación.
        Se llama justo después de que handle_trade confirma retcode 10009.

        Args:
            ticket    : número de ticket de MT5
            symbol    : par operado
            direction : "BUY" o "SELL"
            smc_state : resultado de SMCService.get_smc_state()
            ai_res    : respuesta completa de AnthropicService
        """
        session = (smc_state or {}).get("session", {}).get("session", "OFF")
        setup   = (smc_state or {}).get("setup",   "WAIT")
        entry = {
            "fecha_open":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ticket":         ticket,
            "simbolo":        symbol,
            "direccion":      direction,
            "sesion":         session,
            "setup":          setup,
            "ai_confidence":  round(float(ai_res.get("confidence",  0.0)), 3),
            "planned_rr":     round(float(ai_res.get("risk_reward_ratio", 0.0)), 2),
            "sl_pips":        int(ai_res.get("sl_pips", 0)),
            "tp_pips":        int(ai_res.get("tp_pips", 0)),
        }
        df = pd.DataFrame([entry])
        if not os.path.isfile(cls.CONTEXT_FILE):
            df.to_csv(cls.CONTEXT_FILE, index=False)
        else:
            df.to_csv(cls.CONTEXT_FILE, mode="a", header=False, index=False)

    # =========================================================================
    # 2. ACTUALIZAR MEMORIA DESPUÉS DE CADA CIERRE
    # =========================================================================

    @classmethod
    def update_memory(cls):
        """
        Re-analiza el historial completo (journal + context) y escribe
        strategy_memory.json con las estadísticas actualizadas.
        Debe llamarse después de cada cierre de posición.
        """
        journal = cls._load_journal()
        context = cls._load_context()
        if journal.empty:
            return

        closed = journal[journal["accion"] == "CLOSE"].copy()
        closed["profit"] = pd.to_numeric(closed["profit"], errors="coerce")
        closed = closed.dropna(subset=["profit"])
        if closed.empty:
            return

        # Join: unir cierre con contexto de apertura por ticket
        if not context.empty:
            context["ticket"] = pd.to_numeric(context["ticket"], errors="coerce")
            closed["ticket"]  = pd.to_numeric(closed["ticket"],  errors="coerce")
            merged = closed.merge(context, on="ticket", how="left")
        else:
            merged = closed.copy()
            for col in ["sesion", "setup", "ai_confidence", "planned_rr",
                        "sl_pips", "tp_pips", "simbolo_y"]:
                merged[col] = ""

        merged["win"] = (merged["profit"] > 0).astype(int)
        n_total = len(merged)
        n_wins  = merged["win"].sum()

        # ── Estadísticas globales ─────────────────────────────────────────────
        overall_wr  = round(n_wins / n_total, 3) if n_total > 0 else 0.0
        avg_profit  = round(merged["profit"].mean(), 2)
        total_pnl   = round(merged["profit"].sum(), 2)

        # ── Últimos 5 resultados ──────────────────────────────────────────────
        recent = merged.tail(5)["win"].tolist()
        recent_streak = [1 if x else -1 for x in recent]

        # ── Por tipo de setup ─────────────────────────────────────────────────
        by_setup = cls._group_stats(merged, "setup")

        # ── Por sesión ────────────────────────────────────────────────────────
        by_session = cls._group_stats(merged, "sesion")

        # ── Por símbolo ───────────────────────────────────────────────────────
        sym_col    = "simbolo_y" if "simbolo_y" in merged.columns else "simbolo"
        if sym_col not in merged.columns:
            sym_col = "simbolo"
        by_symbol  = cls._group_stats(merged, sym_col)

        # ── RR planeado vs real ───────────────────────────────────────────────
        if "planned_rr" in merged.columns:
            avg_planned_rr = round(
                pd.to_numeric(merged["planned_rr"], errors="coerce").mean(), 2
            )
        else:
            avg_planned_rr = 0.0

        # RR real: profit / (lot × pip_value × sl_pips) -aproximado como
        # profit / abs(avg_loss) para los que perdieron
        winners = merged[merged["profit"] > 0]["profit"]
        losers  = merged[merged["profit"] < 0]["profit"].abs()
        avg_win  = round(winners.mean(), 2) if not winners.empty else 0.0
        avg_loss = round(losers.mean(),  2) if not losers.empty  else 0.0
        avg_actual_rr = round(avg_win / avg_loss, 2) if avg_loss > 0 else 0.0

        # ── Notas de calibración (auto-generadas) ─────────────────────────────
        notes = cls._generate_calibration_notes(
            overall_wr, by_setup, by_session, by_symbol,
            avg_planned_rr, avg_actual_rr,
        )

        memory = {
            "last_updated":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_trades":   int(n_total),
            "total_wins":     int(n_wins),
            "win_rate":       overall_wr,
            "avg_profit":     avg_profit,
            "total_pnl":      total_pnl,
            "avg_win":        avg_win,
            "avg_loss":       avg_loss,
            "avg_planned_rr": avg_planned_rr,
            "avg_actual_rr":  avg_actual_rr,
            "recent_streak":  recent_streak,
            "by_setup":       by_setup,
            "by_session":     by_session,
            "by_symbol":      by_symbol,
            "calibration_notes": notes,
        }

        with open(cls.MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)

    # =========================================================================
    # 3. CONSTRUIR BLOQUE DE CONTEXTO PARA EL PROMPT
    # =========================================================================

    @classmethod
    def build_prompt_block(cls, symbol: str = "", session: str = "") -> str:
        """
        Construye el bloque de texto que se inyecta en el prompt de la IA.
        Si no hay datos suficientes, retorna string vacío (no afecta el prompt).

        Args:
            symbol  : activo actual (para destacar su estadística)
            session : sesión actual (para destacar su estadística)
        """
        mem = cls._load_memory()
        if not mem or mem.get("total_trades", 0) < 5:
            return ""   # sin datos suficientes, no contaminar el prompt

        n       = mem["total_trades"]
        wr_pct  = round(mem["win_rate"] * 100, 1)
        streak  = mem.get("recent_streak", [])
        streak_str = " ".join("W" if x > 0 else "L" for x in streak)

        lines = [
            f"HISTORICAL PERFORMANCE ({n} closed trades -use to calibrate confidence):",
            f"  Overall win rate : {wr_pct}%  ({mem['total_wins']}/{n})",
            f"  Avg win / loss   : ${mem['avg_win']:+.2f} / ${mem['avg_loss']:.2f}",
            f"  Planned RR 1:{mem['avg_planned_rr']}  ->  Actual RR achieved 1:{mem['avg_actual_rr']}",
            f"  Recent 5 trades  : {streak_str}",
            "",
        ]

        # Setup breakdown
        by_setup = mem.get("by_setup", {})
        if by_setup:
            lines.append("  By setup type:")
            for s, stats in by_setup.items():
                if not s or s == "nan":
                    continue
                tag = cls._perf_tag(stats["win_rate"], mem["win_rate"])
                lines.append(
                    f"    {s:<12} -> {stats['win_rate']*100:.0f}% "
                    f"({stats['wins']}/{stats['n']} trades)  {tag}"
                )

        # Session breakdown
        by_session = mem.get("by_session", {})
        if by_session:
            lines.append("  By session:")
            for s, stats in by_session.items():
                if not s or s in ("nan", "OFF"):
                    continue
                marker = " << CURRENT" if s == session else ""
                lines.append(
                    f"    {s:<8} -> {stats['win_rate']*100:.0f}% "
                    f"({stats['wins']}/{stats['n']} trades){marker}"
                )

        # Symbol breakdown
        by_symbol = mem.get("by_symbol", {})
        if by_symbol and symbol:
            sym_stats = by_symbol.get(symbol)
            if sym_stats and sym_stats["n"] >= 3:
                tag = cls._perf_tag(sym_stats["win_rate"], mem["win_rate"])
                lines.append(
                    f"  {symbol} specifically -> "
                    f"{sym_stats['win_rate']*100:.0f}% win rate "
                    f"({sym_stats['wins']}/{sym_stats['n']} trades)  {tag}"
                )

        # Calibration notes
        notes = mem.get("calibration_notes", [])
        if notes:
            lines.append("")
            lines.append("  CALIBRATION NOTES (auto-derived -adjust your confidence accordingly):")
            for note in notes:
                lines.append(f"    -> {note}")

        return "\n".join(lines)

    # =========================================================================
    # 4. LEER MEMORIA PARA MOSTRAR EN UI
    # =========================================================================

    @classmethod
    def get_memory(cls) -> dict:
        """Retorna la memoria actual (o {} si no existe)."""
        return cls._load_memory()

    # =========================================================================
    # HELPERS PRIVADOS
    # =========================================================================

    @classmethod
    def _load_journal(cls) -> pd.DataFrame:
        from logger_service import LoggerService
        return LoggerService.get_history()

    @classmethod
    def _load_context(cls) -> pd.DataFrame:
        if not os.path.isfile(cls.CONTEXT_FILE):
            return pd.DataFrame(columns=cls.CONTEXT_COLUMNS)
        try:
            df = pd.read_csv(cls.CONTEXT_FILE, on_bad_lines="skip")
        except Exception:
            df = pd.read_csv(cls.CONTEXT_FILE, engine="python", on_bad_lines="skip")
        for col in cls.CONTEXT_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df

    @classmethod
    def _load_memory(cls) -> dict:
        if not os.path.isfile(cls.MEMORY_FILE):
            return {}
        try:
            with open(cls.MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def _group_stats(df: pd.DataFrame, col: str) -> dict:
        """Agrupa por columna y calcula win_rate, n, wins, avg_profit."""
        if col not in df.columns:
            return {}
        result = {}
        for val, group in df.groupby(col):
            key = str(val)
            if not key or key == "nan":
                continue
            n    = len(group)
            wins = int(group["win"].sum())
            result[key] = {
                "n":          n,
                "wins":       wins,
                "win_rate":   round(wins / n, 3) if n > 0 else 0.0,
                "avg_profit": round(group["profit"].mean(), 2),
            }
        return result

    @staticmethod
    def _perf_tag(wr: float, overall: float) -> str:
        delta = wr - overall
        if delta >= 0.15:
            return "++ STRONG"
        if delta >= 0.05:
            return "+ ABOVE AVG"
        if delta <= -0.15:
            return "-- AVOID"
        if delta <= -0.05:
            return "- BELOW AVG"
        return "= AVERAGE"

    @staticmethod
    def _generate_calibration_notes(
        overall_wr: float,
        by_setup: dict,
        by_session: dict,
        by_symbol: dict,
        avg_planned_rr: float,
        avg_actual_rr: float,
    ) -> list:
        """
        Genera texto de calibración que la IA puede leer y aplicar.
        Solo incluye observaciones estadísticamente relevantes (n >= 5).
        """
        notes = []

        # Setup notes
        for s, st in by_setup.items():
            if st["n"] < 5 or not s or s == "nan":
                continue
            delta = st["win_rate"] - overall_wr
            if delta >= 0.15:
                notes.append(
                    f"{s} setups outperform average by {delta*100:.0f}% -"
                    f"increase confidence on {s} entries"
                )
            elif delta <= -0.15:
                notes.append(
                    f"{s} setups underperform by {abs(delta)*100:.0f}% -"
                    f"reduce confidence and require additional confirmation on {s}"
                )

        # Session notes
        sessions = {k: v for k, v in by_session.items()
                    if v["n"] >= 5 and k not in ("nan", "OFF")}
        if len(sessions) >= 2:
            best  = max(sessions.items(), key=lambda x: x[1]["win_rate"])
            worst = min(sessions.items(), key=lambda x: x[1]["win_rate"])
            if best[1]["win_rate"] - worst[1]["win_rate"] >= 0.10:
                notes.append(
                    f"{best[0]} session outperforms {worst[0]} by "
                    f"{(best[1]['win_rate'] - worst[1]['win_rate'])*100:.0f}% -"
                    f"be more conservative during {worst[0]}"
                )

        # Symbol notes
        for sym, st in by_symbol.items():
            if st["n"] < 5 or not sym or sym == "nan":
                continue
            delta = st["win_rate"] - overall_wr
            if delta <= -0.15:
                notes.append(
                    f"{sym} win rate is {st['win_rate']*100:.0f}% (below average {overall_wr*100:.0f}%) -"
                    f"require stronger confirmation for {sym} trades"
                )

        # RR gap note
        if avg_planned_rr > 0 and avg_actual_rr > 0:
            rr_gap = avg_planned_rr - avg_actual_rr
            if rr_gap >= 0.5:
                notes.append(
                    f"Planned RR 1:{avg_planned_rr} vs actual 1:{avg_actual_rr} -"
                    f"TPs are rarely fully hit; consider reducing TP targets by ~{rr_gap:.1f}R"
                )
            elif rr_gap <= -0.3:
                notes.append(
                    f"Actual RR 1:{avg_actual_rr} exceeds planned 1:{avg_planned_rr} -"
                    f"system is capturing more than planned; TP targets are well-calibrated"
                )

        return notes
