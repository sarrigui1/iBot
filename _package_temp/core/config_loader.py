"""
Config Loader — Lee y valida config.ini

Clase ConfigLoader que carga parámetros de config.ini y los expone como atributos.
Valida que todos los campos requeridos existan y sean del tipo correcto.
"""

import os
import configparser
from typing import Optional, List


class ConfigLoader:
    """Lee config.ini y expone parámetros como atributos."""

    def __init__(self, config_path: str = None):
        """
        Carga config.ini y valida todos los parámetros.

        Args:
            config_path: Ruta al archivo config.ini (default: busca en config/ o raíz)

        Raises:
            FileNotFoundError: Si config.ini no existe
            ValueError: Si hay campos requeridos inválidos o faltantes
        """
        # Si no se proporciona ruta, buscar en ubicaciones estándar
        if config_path is None:
            possible_paths = [
                os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini'),
                'config.ini',
                os.path.join('config', 'config.ini'),
            ]
            config_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break

            if config_path is None:
                raise FileNotFoundError(
                    "config.ini no encontrado. "
                    "Buscado en: config/config.ini o raíz del proyecto. "
                    "Por favor, copia el template y edítalo con tus valores."
                )
        elif not os.path.exists(config_path):
            raise FileNotFoundError(
                f"config.ini no encontrado en {config_path}. "
                f"Por favor, copia el template y edítalo con tus valores."
            )

        self.parser = configparser.ConfigParser()
        self.parser.read(config_path)
        self._validate()
        self._load_values()

    def _validate(self):
        """Valida que todas las secciones y campos requeridos existan."""
        required_sections = {
            "LICENSE": ["LICENSE_KEY", "GOOGLE_SHEET_ID"],
            "MT5_ACCOUNT": ["MT5_LOGIN", "MT5_PASSWORD", "MT5_SERVER"],
            "TRADING_PARAMETERS": [
                "SYMBOLS",
                "AUTONOMOUS_CONFIDENCE_THRESHOLD",
                "MAX_DAILY_LOSS_PCT",
                "MAX_SPREAD_POINTS",
            ],
            "TIMEZONE": ["LOCAL_UTC_OFFSET", "LOCAL_TZ_NAME"],
            "REFRESH_TIMING": ["DEFAULT_REFRESH_SECONDS", "AI_MIN_INTERVAL_MINS"],
            "NEWS_CONFIG": ["NEWS_SHIELD_MINUTES", "NEWS_CACHE_TTL"],
            "UI_LANGUAGE": ["LANGUAGE"],
        }

        for section, fields in required_sections.items():
            if not self.parser.has_section(section):
                raise ValueError(f"Sección [{section}] falta en config.ini")

            for field in fields:
                if not self.parser.has_option(section, field):
                    raise ValueError(f"Campo {field} falta en sección [{section}]")

    def _load_values(self):
        """Carga y convierte los valores de config.ini a atributos con tipos correctos."""

        # LICENSE
        self.license_key: str = self.parser.get("LICENSE", "LICENSE_KEY").strip()
        self.google_sheet_id: str = self.parser.get("LICENSE", "GOOGLE_SHEET_ID").strip()

        if not self.license_key:
            raise ValueError("LICENSE_KEY no puede estar vacío en config.ini")

        # MT5_ACCOUNT
        self.mt5_login: int = self.parser.getint("MT5_ACCOUNT", "MT5_LOGIN")
        self.mt5_password: str = self.parser.get("MT5_ACCOUNT", "MT5_PASSWORD").strip()
        self.mt5_server: str = self.parser.get("MT5_ACCOUNT", "MT5_SERVER").strip()

        if not self.mt5_password or not self.mt5_server:
            raise ValueError("MT5_PASSWORD y MT5_SERVER no pueden estar vacíos")

        # TRADING_PARAMETERS
        symbols_str = self.parser.get("TRADING_PARAMETERS", "SYMBOLS").strip()
        self.symbols: List[str] = [s.strip() for s in symbols_str.split(",")]

        self.autonomous_confidence_threshold: float = self.parser.getfloat(
            "TRADING_PARAMETERS", "AUTONOMOUS_CONFIDENCE_THRESHOLD"
        )
        self.max_daily_loss_pct: float = self.parser.getfloat(
            "TRADING_PARAMETERS", "MAX_DAILY_LOSS_PCT"
        )
        self.max_spread_points: int = self.parser.getint(
            "TRADING_PARAMETERS", "MAX_SPREAD_POINTS"
        )
        self.max_positions_per_symbol: int = self.parser.getint(
            "TRADING_PARAMETERS", "MAX_POSITIONS_PER_SYMBOL"
        )

        # Validar rangos
        if not (0 <= self.autonomous_confidence_threshold <= 1):
            raise ValueError(
                "AUTONOMOUS_CONFIDENCE_THRESHOLD debe estar entre 0 y 1"
            )
        if not (0 < self.max_daily_loss_pct <= 100):
            raise ValueError("MAX_DAILY_LOSS_PCT debe estar entre 0 y 100")
        if self.max_spread_points < 0:
            raise ValueError("MAX_SPREAD_POINTS debe ser positivo")

        # TIMEZONE
        self.local_utc_offset: int = self.parser.getint("TIMEZONE", "LOCAL_UTC_OFFSET")
        self.local_tz_name: str = self.parser.get("TIMEZONE", "LOCAL_TZ_NAME").strip()
        self.broker_utc_offset: int = self.parser.getint(
            "TIMEZONE", "BROKER_UTC_OFFSET"
        )

        # REFRESH_TIMING
        self.default_refresh_seconds: int = self.parser.getint(
            "REFRESH_TIMING", "DEFAULT_REFRESH_SECONDS"
        )
        self.ai_min_interval_mins: int = self.parser.getint(
            "REFRESH_TIMING", "AI_MIN_INTERVAL_MINS"
        )

        # NEWS_CONFIG
        self.news_shield_minutes: int = self.parser.getint(
            "NEWS_CONFIG", "NEWS_SHIELD_MINUTES"
        )
        self.news_cache_ttl: int = self.parser.getint("NEWS_CONFIG", "NEWS_CACHE_TTL")

        # UI_LANGUAGE
        self.language: str = self.parser.get("UI_LANGUAGE", "LANGUAGE").strip()
        if self.language not in ["es", "en"]:
            raise ValueError("LANGUAGE debe ser 'es' o 'en'")

    def __repr__(self) -> str:
        return f"<ConfigLoader license={self.license_key} symbols={len(self.symbols)} timezone={self.local_tz_name}>"
