"""
Activity Logger — Registro de todas las acciones del usuario en la UI

Captura:
  - Cambios de configuración
  - Ejecuciones de análisis
  - Trades ejecutados
  - Cambios de modo (autónomo, idioma, etc.)
  - Errores y eventos importantes

Almacenamiento: data/activity_log.jsonl (JSON Lines)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class ActivityLogger:
    """Logger centralizado para actividades del usuario."""

    LOG_FILE = "data/activity_log.jsonl"
    MAX_LINES = 10000  # Rotación: crear nuevo archivo después de 10K líneas

    @classmethod
    def log(
        cls,
        action: str,
        category: str = "general",
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        user_symbol: Optional[str] = None,
    ):
        """
        Registra una acción del usuario.

        Args:
            action: Nombre de la acción (ej: "ANALYZE", "TRADE_EXECUTED", "CONFIG_CHANGED")
            category: Categoría (ej: "trading", "config", "system", "error")
            details: Diccionario con detalles adicionales
            status: "success", "failed", "warning", "info"
            user_symbol: Símbolo si es relevante (ej: "EURUSD")
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "category": category,
            "status": status,
            "symbol": user_symbol,
            "details": details or {},
        }

        try:
            # Crear directorio si no existe
            log_dir = Path(cls.LOG_FILE).parent
            log_dir.mkdir(parents=True, exist_ok=True)

            # Escribir entrada (JSONL = una línea JSON por evento)
            with open(cls.LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

            # Rotación: si hay muchas líneas, crear nuevo archivo
            cls._check_rotation()

        except Exception as e:
            print(f"[ActivityLogger] Error al registrar: {e}")

    @classmethod
    def log_analysis(cls, symbol: str, confidence: float, decision: str):
        """Registra ejecución de análisis."""
        cls.log(
            action="ANALYSIS_EXECUTED",
            category="trading",
            details={
                "confidence": round(confidence, 3),
                "decision": decision,
            },
            user_symbol=symbol,
        )

    @classmethod
    def log_trade(
        cls,
        symbol: str,
        direction: str,
        lot_size: float,
        sl_pips: int,
        tp_pips: int,
        ticket: Optional[int] = None,
        auto: bool = False,
    ):
        """Registra ejecución de trade."""
        cls.log(
            action="TRADE_EXECUTED",
            category="trading",
            details={
                "direction": direction,
                "lot_size": lot_size,
                "sl_pips": sl_pips,
                "tp_pips": tp_pips,
                "ticket": ticket,
                "automatic": auto,
            },
            user_symbol=symbol,
        )

    @classmethod
    def log_config_change(cls, section: str, param: str, old_value: Any, new_value: Any):
        """Registra cambio de configuración."""
        cls.log(
            action="CONFIG_CHANGED",
            category="config",
            details={
                "section": section,
                "parameter": param,
                "old_value": str(old_value),
                "new_value": str(new_value),
            },
        )

    @classmethod
    def log_mode_change(cls, mode: str, enabled: bool):
        """Registra cambio de modo (autónomo, etc.)."""
        cls.log(
            action="MODE_CHANGED",
            category="system",
            details={
                "mode": mode,
                "enabled": enabled,
            },
        )

    @classmethod
    def log_error(cls, error_type: str, error_message: str, context: Optional[str] = None):
        """Registra error."""
        cls.log(
            action="ERROR_OCCURRED",
            category="error",
            status="failed",
            details={
                "error_type": error_type,
                "error_message": error_message,
                "context": context,
            },
        )

    @classmethod
    def get_recent_activities(cls, limit: int = 100) -> list:
        """
        Retorna las últimas actividades del usuario.

        Args:
            limit: Número de actividades a retornar

        Returns:
            Lista de diccionarios con actividades
        """
        if not os.path.exists(cls.LOG_FILE):
            return []

        try:
            activities = []
            with open(cls.LOG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Leer últimas N líneas
            for line in lines[-limit:]:
                try:
                    activities.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue

            # Retornar en orden cronológico inverso (últimas primero)
            return list(reversed(activities))

        except Exception as e:
            print(f"[ActivityLogger] Error al leer actividades: {e}")
            return []

    @classmethod
    def get_activities_by_action(cls, action: str, limit: int = 50) -> list:
        """Retorna actividades filtradas por acción."""
        all_activities = cls.get_recent_activities(limit=limit * 2)
        return [a for a in all_activities if a.get("action") == action][:limit]

    @classmethod
    def get_activities_by_symbol(cls, symbol: str, limit: int = 50) -> list:
        """Retorna actividades filtradas por símbolo."""
        all_activities = cls.get_recent_activities(limit=limit * 2)
        return [a for a in all_activities if a.get("symbol") == symbol][:limit]

    @classmethod
    def get_stats(cls) -> dict:
        """Retorna estadísticas de actividades."""
        activities = cls.get_recent_activities(limit=1000)

        if not activities:
            return {
                "total_activities": 0,
                "trades_executed": 0,
                "analyses_run": 0,
                "errors": 0,
                "config_changes": 0,
            }

        trades = len([a for a in activities if a.get("action") == "TRADE_EXECUTED"])
        analyses = len([a for a in activities if a.get("action") == "ANALYSIS_EXECUTED"])
        errors = len([a for a in activities if a.get("category") == "error"])
        config = len([a for a in activities if a.get("action") == "CONFIG_CHANGED"])

        return {
            "total_activities": len(activities),
            "trades_executed": trades,
            "analyses_run": analyses,
            "errors": errors,
            "config_changes": config,
        }

    @classmethod
    def _check_rotation(cls):
        """Verifica si debe rotarse el archivo de log."""
        if not os.path.exists(cls.LOG_FILE):
            return

        try:
            with open(cls.LOG_FILE, "r") as f:
                line_count = sum(1 for _ in f)

            if line_count > cls.MAX_LINES:
                # Renombrar archivo actual
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = cls.LOG_FILE.replace(".jsonl", f"_{timestamp}.jsonl")
                os.rename(cls.LOG_FILE, backup_name)

        except Exception as e:
            print(f"[ActivityLogger] Error en rotación: {e}")


# Alias corto
activity_log = ActivityLogger()
