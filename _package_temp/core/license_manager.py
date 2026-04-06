"""
License Manager — Validación de licencias contra Google Sheets

Lee licencias de una Google Sheet pública y las valida localmente.
Mantiene un caché local para funcionar offline durante hasta 7 días.
"""

import json
import os
from datetime import datetime, timedelta
from io import StringIO
import urllib.request
import urllib.error
from typing import Tuple
import csv

from core.config_loader import ConfigLoader


class LicenseManager:
    """Valida licencias contra Google Sheets con caché offline."""

    CACHE_DAYS = 7
    CACHE_FILE = "data/license_cache.json"

    def __init__(self, config: ConfigLoader):
        """
        Inicializa el gestor de licencias.

        Args:
            config: Instancia de ConfigLoader
        """
        self.license_key = config.license_key
        self.sheet_id = config.google_sheet_id
        self.cache_file = self.CACHE_FILE

        # Crear directorio data si no existe
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)

    def validate(self) -> Tuple[bool, str, bool, str]:
        """
        Valida la licencia contra Google Sheets.

        Returns:
            (is_valid, message, was_cached, cached_timestamp)
            - is_valid: True si la licencia es válida
            - message: Descripción del estado
            - was_cached: True si se usó caché local
            - cached_timestamp: Fecha de última validación exitosa (si fue cached)

        Flujo:
        1. Intenta validar contra Google Sheet en línea
        2. Si éxito: guarda en caché y retorna True
        3. Si falla (sin internet):
           - Si caché existe y <7 días: retorna True + was_cached=True
           - Si caché expirado: retorna False
           - Si no hay caché: retorna False
        """

        # Intentar validación en línea
        try:
            is_valid, msg = self._validate_online()
            if is_valid:
                self._save_cache()
                return is_valid, msg, False, ""
            else:
                # Validación online falló (error en datos, no en conexión)
                # No usar caché si los datos son inválidos
                return False, msg, False, ""

        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
            # Error de conexión — intentar usar caché
            return self._validate_with_cache()

        except Exception as e:
            # Error inesperado
            return False, f"Error al validar licencia: {str(e)}", False, ""

    def _validate_online(self) -> Tuple[bool, str]:
        """
        Valida contra Google Sheets en línea.

        Returns:
            (is_valid, message)

        Raises:
            urllib.error.URLError: Si no hay internet
            Exception: Para otros errores
        """
        csv_url = (
            f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/"
            f"export?format=csv&gid=0"
        )

        try:
            # Descargar CSV
            with urllib.request.urlopen(csv_url, timeout=5) as response:
                csv_text = response.read().decode("utf-8")

            # Parsear CSV
            reader = csv.DictReader(StringIO(csv_text))
            rows = list(reader)

            if not rows:
                return False, "Google Sheet vacío"

            # Buscar la licencia en las filas
            for row in rows:
                # Limpiar espacios
                row_key = row.get("license_key", "").strip() if row.get("license_key") else ""

                if row_key == self.license_key:
                    # Validar status
                    status_str = row.get("active_status", "").strip().upper()
                    if status_str not in ("TRUE", "1"):
                        return False, f"Licencia '{self.license_key}' está inactiva"

                    # Validar expiry_date
                    expiry_str = row.get("expiry_date", "").strip()
                    if not expiry_str:
                        return False, "Fecha de expiración no definida"

                    try:
                        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                        if expiry_date < datetime.now().date():
                            return (
                                False,
                                f"Licencia expirada el {expiry_str}",
                            )
                    except ValueError:
                        return (
                            False,
                            f"Formato de fecha inválido en Google Sheet: {expiry_str}",
                        )

                    return True, f"Licencia '{self.license_key}' válida hasta {expiry_str}"

            # No encontrada
            return (
                False,
                f"Licencia '{self.license_key}' no encontrada en Google Sheets",
            )

        except urllib.error.URLError as e:
            # Sin internet o sheet no accesible
            raise
        except Exception as e:
            raise ValueError(f"Error al leer Google Sheets: {str(e)}")

    def _validate_with_cache(self) -> Tuple[bool, str, bool, str]:
        """
        Intenta usar caché local cuando no hay internet.

        Returns:
            (is_valid, message, was_cached, cached_timestamp)
        """
        if not os.path.exists(self.cache_file):
            return (
                False,
                "No hay conexión a internet y caché local no disponible",
                False,
                "",
            )

        try:
            with open(self.cache_file, "r") as f:
                cache = json.load(f)

            last_validated = datetime.fromisoformat(cache.get("last_validated", ""))
            days_since = (datetime.now() - last_validated).days

            if days_since > self.CACHE_DAYS:
                return (
                    False,
                    f"Caché expirado (última validación hace {days_since} días)",
                    False,
                    "",
                )

            # Caché válido
            is_valid = cache.get("is_valid", False)
            if not is_valid:
                return False, "Última validación falló", True, last_validated.isoformat()

            return (
                True,
                f"Usando caché local (última validación: {last_validated.strftime('%Y-%m-%d %H:%M')})",
                True,
                last_validated.isoformat(),
            )

        except Exception as e:
            return False, f"Error al leer caché: {str(e)}", False, ""

    def _save_cache(self):
        """Guarda el resultado de validación en caché local."""
        cache = {
            "license_key": self.license_key,
            "last_validated": datetime.now().isoformat(),
            "is_valid": True,
        }

        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, "w") as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            # No bloquear si el caché falla
            print(f"[LicenseManager] Advertencia al guardar caché: {e}")
