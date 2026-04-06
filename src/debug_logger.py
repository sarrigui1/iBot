"""
Debug Logger - Sistema de logging con niveles DEBUG e INFO

Modos:
  - DEBUG: Registra absolutamente TODO (errores, llamadas, variables, ejecución)
  - INFO: Solo registra validaciones importantes (AI, licencias, configuraciones)

Archivo de salida: data/ibot.log
"""

import os
import logging
from datetime import datetime
from pathlib import Path


class DebugLogger:
    """Logger centralizado con niveles DEBUG e INFO."""

    # Niveles de log
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

    _instance = None
    _logger = None
    _log_level = INFO
    _log_file = None

    def __new__(cls):
        """Singleton: una sola instancia del logger."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def initialize(cls, debug_mode: bool = False, log_dir: str = "data"):
        """
        Inicializa el logger.

        Args:
            debug_mode: Si True, nivel DEBUG. Si False, nivel INFO.
            log_dir: Directorio donde guardar los logs.
        """
        # Crear directorio de logs si no existe
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        cls._log_file = log_path / "ibot.log"
        cls._log_level = cls.DEBUG if debug_mode else cls.INFO

        # Crear logger con Python logging
        cls._logger = logging.getLogger("iBot")
        cls._logger.setLevel(logging.DEBUG)  # Acepta todo, filtramos después

        # Limpiar handlers anteriores
        cls._logger.handlers.clear()

        # Handler para archivo
        file_handler = logging.FileHandler(cls._log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Formato de log
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)-8s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        cls._logger.addHandler(file_handler)
        cls._logger.addHandler(console_handler)

        # Log inicial
        mode_text = "DEBUG (Todo registrado)" if debug_mode else "INFO (Solo importante)"
        cls._logger.info(f"═══════════════════════════════════════════════════════════")
        cls._logger.info(f"iBot Logger inicializado - Modo: {mode_text}")
        cls._logger.info(f"Log file: {cls._log_file}")
        cls._logger.info(f"═══════════════════════════════════════════════════════════")

    @classmethod
    def debug(cls, message: str, **kwargs):
        """Registra en nivel DEBUG (solo si debug_mode=True)."""
        if cls._should_log(cls.DEBUG):
            cls._log(logging.DEBUG, message, kwargs)

    @classmethod
    def info(cls, message: str, **kwargs):
        """Registra en nivel INFO (siempre)."""
        if cls._should_log(cls.INFO):
            cls._log(logging.INFO, message, kwargs)

    @classmethod
    def warning(cls, message: str, **kwargs):
        """Registra en nivel WARNING (siempre)."""
        cls._log(logging.WARNING, message, kwargs)

    @classmethod
    def error(cls, message: str, exc_info=None, **kwargs):
        """Registra en nivel ERROR con info de excepción (siempre)."""
        cls._log(logging.ERROR, message, kwargs, exc_info=exc_info)

    @classmethod
    def _should_log(cls, level: str) -> bool:
        """Determina si debe registrar según el nivel actual."""
        level_priority = {
            cls.DEBUG: 0,
            cls.INFO: 1,
            cls.WARNING: 2,
            cls.ERROR: 3,
        }

        current_priority = level_priority.get(cls._log_level, 1)
        message_priority = level_priority.get(level, 1)

        return message_priority >= current_priority

    @classmethod
    def _log(cls, level, message: str, kwargs: dict = None, exc_info=None):
        """Log interno que formatea el mensaje."""
        if cls._logger is None:
            # Si no está inicializado, inicializar con modo INFO
            cls.initialize(debug_mode=False)

        # Formatear mensaje con kwargs si existen
        if kwargs:
            try:
                message = message.format(**kwargs)
            except (KeyError, ValueError):
                # Si no se puede formatear, usar el mensaje original
                pass

        # Registrar según nivel
        if level == logging.DEBUG:
            cls._logger.debug(message, exc_info=exc_info)
        elif level == logging.INFO:
            cls._logger.info(message, exc_info=exc_info)
        elif level == logging.WARNING:
            cls._logger.warning(message, exc_info=exc_info)
        elif level == logging.ERROR:
            cls._logger.error(message, exc_info=exc_info)

    @classmethod
    def get_log_file(cls) -> Path:
        """Retorna la ruta del archivo de log."""
        return cls._log_file

    @classmethod
    def get_mode(cls) -> str:
        """Retorna el modo actual (DEBUG o INFO)."""
        return cls._log_level

    @classmethod
    def read_logs(cls, lines: int = 100) -> list:
        """Lee las últimas N líneas del archivo de log."""
        if cls._log_file is None or not cls._log_file.exists():
            return []

        try:
            with open(cls._log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
            return all_lines[-lines:]
        except Exception as e:
            return [f"Error leyendo logs: {e}"]


# Alias corto para uso rápido
log = DebugLogger()
