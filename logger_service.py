import pandas as pd
import os
from datetime import datetime

class LoggerService:
    FILE_NAME     = "trading_journal.csv"
    DECISION_FILE = "trading_decisions.csv"

    @classmethod
    def log_event(cls, ticket, symbol, action, lot, price, status, comment="", profit=None):
        new_entry = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ticket": ticket,
            "simbolo": symbol,
            "accion": action,
            "lote": lot,
            "precio": price,
            "profit": profit if profit is not None else "",
            "estado": status,
            "comentario": comment
        }
        df = pd.DataFrame([new_entry])
        if not os.path.isfile(cls.FILE_NAME):
            df.to_csv(cls.FILE_NAME, index=False)
        else:
            df.to_csv(cls.FILE_NAME, mode='a', header=False, index=False)

    # ── Log de operaciones ────────────────────────────────────────────────────
    COLUMNS = ["fecha", "ticket", "simbolo", "accion", "lote", "precio", "profit", "estado", "comentario"]

    # ── Log de decisiones AI ──────────────────────────────────────────────────
    DECISION_COLUMNS = ["fecha", "simbolo", "decision", "confianza", "sl_pips", "tp_pips", "aceptada", "motivo_rechazo"]

    @classmethod
    def log_decision(
        cls,
        symbol: str,
        decision: str,
        confidence: float,
        sl_pips: int,
        tp_pips: int,
        accepted: bool,
        reject_reason: str = "",
    ):
        """Registra cada señal AI con el motivo de aceptación o rechazo."""
        entry = {
            "fecha":           datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "simbolo":         symbol,
            "decision":        decision,
            "confianza":       round(confidence, 3),
            "sl_pips":         sl_pips,
            "tp_pips":         tp_pips,
            "aceptada":        "SI" if accepted else "NO",
            "motivo_rechazo":  reject_reason,
        }
        df = pd.DataFrame([entry])
        if not os.path.isfile(cls.DECISION_FILE):
            df.to_csv(cls.DECISION_FILE, index=False)
        else:
            df.to_csv(cls.DECISION_FILE, mode="a", header=False, index=False)

    @classmethod
    def get_decisions(cls) -> pd.DataFrame:
        """Lee el historial de decisiones AI."""
        if not os.path.isfile(cls.DECISION_FILE):
            return pd.DataFrame(columns=cls.DECISION_COLUMNS)
        try:
            df = pd.read_csv(cls.DECISION_FILE, on_bad_lines="skip")
        except Exception:
            df = pd.read_csv(cls.DECISION_FILE, engine="python", on_bad_lines="skip")
        for col in cls.DECISION_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df[cls.DECISION_COLUMNS].sort_values("fecha", ascending=False)

    @classmethod
    def get_history(cls):
        if not os.path.isfile(cls.FILE_NAME):
            return pd.DataFrame()
        try:
            df = pd.read_csv(cls.FILE_NAME, on_bad_lines="skip")
        except Exception:
            # Fallback con engine Python, más tolerante con CSVs malformados
            df = pd.read_csv(cls.FILE_NAME, engine="python", on_bad_lines="skip")

        # Añadir columnas faltantes (filas del formato antiguo sin 'profit')
        for col in cls.COLUMNS:
            if col not in df.columns:
                df[col] = ""

        return df[cls.COLUMNS].sort_values(by="fecha", ascending=False)