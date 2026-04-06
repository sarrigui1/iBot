"""
License Manager — Validación de licencias contra Google Apps Script

Lee licencias de un endpoint privado (Google Apps Script) que accede a Google Sheets.
Mantiene un caché local para funcionar offline durante hasta 7 días.
"""

import json
import os
from datetime import datetime, timedelta
import urllib.request
import urllib.error
from typing import Tuple

from core.config_loader import ConfigLoader


class LicenseManager:
    """Valida licencias contra Google Apps Script con caché offline."""

    CACHE_DAYS = 7
    CACHE_FILE = "data/license_cache.json"
    DAILY_VALIDATION_FILE = "data/license_daily_check.json"
    # Endpoint privado de Google Apps Script (reemplaza acceso directo a Google Sheets)
    GOOGLE_APPS_SCRIPT_ENDPOINT = "https://script.google.com/macros/s/AKfycbwl-fdkWihZ58NT3y8SVUfQVJ9H_kYr8vrehjpYwR2t_zYSfcS-YmOBCPXVUrjKpl17/exec"

    def __init__(self, config: ConfigLoader):
        """
        Inicializa el gestor de licencias.

        Args:
            config: Instancia de ConfigLoader
        """
        self.license_key = config.license_key
        self.cache_file = self.CACHE_FILE

        # Crear directorio data si no existe
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)

    def validate(self) -> Tuple[bool, str, bool, str]:
        """
        Valida la licencia contra Google Sheets (máximo una vez por día).

        Returns:
            (is_valid, message, was_cached, cached_timestamp)
            - is_valid: True si la licencia es válida
            - message: Descripción del estado
            - was_cached: True si se usó caché local
            - cached_timestamp: Fecha de última validación exitosa (si fue cached)

        Flujo:
        1. Si ya validó hoy: retorna caché sin conexión
        2. Si no: intenta validación en línea
        3. Si éxito: guarda en caché y retorna True
        4. Si falla (sin internet):
           - Si caché existe y <7 días: retorna True + was_cached=True
           - Si caché expirado: retorna False
           - Si no hay caché: retorna False
        """

        # Optimización: verificar si ya validó hoy
        if self._already_validated_today():
            return self._validate_with_cache()

        # Intentar validación en línea (solo si no validó hoy)
        try:
            is_valid, msg = self._validate_online()
            if is_valid:
                self._save_cache()
                self._save_daily_check()  # Marca que validó hoy
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
        Valida contra Google Apps Script endpoint en línea.

        El endpoint es privado y solo devuelve datos, sin exponer la Google Sheet.

        Returns:
            (is_valid, message)

        Raises:
            urllib.error.URLError: Si no hay internet
            Exception: Para otros errores
        """
        try:
            # Conectar al endpoint privado de Google Apps Script
            with urllib.request.urlopen(self.GOOGLE_APPS_SCRIPT_ENDPOINT, timeout=5) as response:
                json_text = response.read().decode("utf-8")

            # Parsear JSON
            licenses = json.loads(json_text)

            if not licenses:
                return False, "No hay licencias registradas en el servidor"

            # Buscar la licencia en los datos
            for lic in licenses:
                # Limpiar espacios y convertir a string
                lic_key = str(lic.get("license_key", "")).strip() if lic.get("license_key") else ""

                if lic_key == self.license_key:
                    # Validar status (puede ser boolean True o string "TRUE"/"1")
                    status = lic.get("active_status")
                    is_active = status is True or str(status).strip().upper() in ("TRUE", "1")

                    if not is_active:
                        return False, f"Licencia '{self.license_key}' está inactiva"

                    # Validar expiry_date
                    expiry_str = str(lic.get("expiry_date", "")).strip()
                    if not expiry_str:
                        return False, "Fecha de expiración no definida"

                    try:
                        # Parsear fecha (puede venir como ISO o YYYY-MM-DD)
                        if "T" in expiry_str:
                            # Formato ISO: 2027-12-31T05:00:00.000Z
                            expiry_date = datetime.fromisoformat(expiry_str.split("T")[0]).date()
                        else:
                            # Formato simple: 2027-12-31
                            expiry_date = datetime.strptime(expiry_str[:10], "%Y-%m-%d").date()

                        if expiry_date < datetime.now().date():
                            return (
                                False,
                                f"Licencia expirada el {expiry_date}",
                            )
                    except (ValueError, AttributeError) as e:
                        return (
                            False,
                            f"Formato de fecha inválido: {expiry_str}",
                        )

                    # Información adicional
                    features = lic.get("features", "standard")
                    max_instances = lic.get("max_instances", 1)
                    customer = lic.get("customer_name", "")

                    return True, f"Licencia '{self.license_key}' válida hasta {expiry_date} ({features})"

            # No encontrada
            return (
                False,
                f"Licencia '{self.license_key}' no encontrada en el servidor",
            )

        except urllib.error.URLError as e:
            # Sin internet o endpoint no accesible
            raise
        except json.JSONDecodeError as e:
            raise ValueError(f"Error al parsear respuesta del servidor: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error al validar licencia: {str(e)}")

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

    def _already_validated_today(self) -> bool:
        """
        Verifica si ya validó la licencia hoy.

        Returns:
            True si ya validó hoy, False en caso contrario
        """
        if not os.path.exists(self.DAILY_VALIDATION_FILE):
            return False

        try:
            with open(self.DAILY_VALIDATION_FILE, "r") as f:
                data = json.load(f)

            last_check = datetime.fromisoformat(data.get("last_check", ""))
            today = datetime.now().date()
            last_check_date = last_check.date()

            # Retornar True si la última validación fue hoy
            return today == last_check_date

        except Exception:
            return False

    def _save_daily_check(self):
        """Guarda marca de validación diaria."""
        data = {
            "license_key": self.license_key,
            "last_check": datetime.now().isoformat(),
        }

        try:
            os.makedirs(os.path.dirname(self.DAILY_VALIDATION_FILE), exist_ok=True)
            with open(self.DAILY_VALIDATION_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            # No bloquear si falla
            print(f"[LicenseManager] Advertencia al guardar check diario: {e}")
