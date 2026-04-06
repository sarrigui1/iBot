"""
iBot Trading - Instalador Avanzado

Instala la aplicación con:
- Solo archivos necesarios (código compilado + config + docs)
- Protección de código fuente
- Logs detallados en consola
- Validación de dependencias
- Generación de README post-instalación
- Launcher automático

Uso:
  python tools/advanced_installer.py <destino>

Ejemplo:
  python tools/advanced_installer.py "C:\iBot_Trading"
"""

import os
import sys
import shutil
import subprocess
import json
import py_compile
from pathlib import Path
from datetime import datetime
from typing import Tuple, List


class AdvancedInstaller:
    """Instalador avanzado con protección de código y logs detallados."""

    def __init__(self, install_dir: str):
        self.install_dir = Path(install_dir)
        self.project_root = Path(__file__).parent.parent
        self.log_file = self.install_dir / "installation.log"
        self.start_time = datetime.now()

    def log(self, message: str, level: str = "INFO"):
        """Log en consola y archivo."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level:7}] {message}"
        print(log_msg)

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_msg + "\n")
        except:
            pass  # No bloquear si el archivo no existe aún

    def print_header(self):
        """Imprime encabezado de instalación."""
        print("\n" + "=" * 80)
        print("iBot Trading - INSTALADOR AVANZADO")
        print("=" * 80)
        print(f"Destino: {self.install_dir}")
        print(f"Inicio: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80 + "\n")

    def check_python_version(self) -> bool:
        """Verifica que Python 3.8+ está instalado."""
        self.log("Verificando versión de Python...")

        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.log(f"Python 3.8+ requerido. Actual: {version.major}.{version.minor}", "ERROR")
            return False

        self.log(f"Python {version.major}.{version.minor}.{version.micro} - OK", "SUCCESS")
        return True

    def create_directories(self) -> bool:
        """Crea estructura de directorios."""
        self.log("Creando estructura de directorios...")

        dirs = [
            self.install_dir / "src",
            self.install_dir / "core",
            self.install_dir / "config",
            self.install_dir / "data",
            self.install_dir / "docs",
            self.install_dir / "tools",
        ]

        try:
            self.install_dir.mkdir(parents=True, exist_ok=True)
            for d in dirs:
                d.mkdir(exist_ok=True)
            self.log(f"Directorios creados: {len(dirs)} carpetas", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Error creando directorios: {e}", "ERROR")
            return False

    def compile_python_files(self) -> bool:
        """Compila archivos .py a bytecode .pyc para proteger código."""
        self.log("Compilando código fuente a bytecode...")

        files_to_compile = [
            # src/
            ("src/app.py", "src"),
            ("src/config.py", "src"),
            ("src/anthropic_service.py", "src"),
            ("src/mt5_service.py", "src"),
            ("src/smc_service.py", "src"),
            ("src/indicators_service.py", "src"),
            ("src/ui_components.py", "src"),
            ("src/risk_manager.py", "src"),
            ("src/logger_service.py", "src"),
            ("src/feedback_service.py", "src"),
            ("src/news_service.py", "src"),
            ("src/i18n.py", "src"),
            # core/
            ("core/config_loader.py", "core"),
            ("core/license_manager.py", "core"),
            # app_main.py
            ("app_main.py", "."),
        ]

        compiled = 0
        for source_file, dest_folder in files_to_compile:
            source_path = self.project_root / source_file
            if source_path.exists():
                try:
                    dest_dir = self.install_dir / dest_folder / "__pycache__"
                    dest_dir.mkdir(parents=True, exist_ok=True)

                    # Compilar a bytecode
                    py_compile.compile(str(source_path), cfile=str(dest_dir / Path(source_file).stem) + ".pyc")
                    compiled += 1
                except Exception as e:
                    self.log(f"Error compilando {source_file}: {e}", "WARN")

        self.log(f"Compilados {compiled} archivos a bytecode", "SUCCESS")
        return compiled > 0

    def copy_config_template(self) -> bool:
        """Copia template de config.ini."""
        self.log("Copiando configuración...")

        source = self.project_root / "config" / "config.ini"
        dest = self.install_dir / "config" / "config.ini"

        try:
            if source.exists():
                shutil.copy2(source, dest)
                self.log(f"config.ini copiado", "SUCCESS")
                return True
            else:
                self.log(f"No se encontró {source}", "WARN")
                return False
        except Exception as e:
            self.log(f"Error copiando config: {e}", "ERROR")
            return False

    def copy_documentation(self) -> bool:
        """Copia documentación para el usuario."""
        self.log("Copiando documentación...")

        docs_to_copy = [
            ("docs/USUARIO/README.txt", "docs"),
            ("SISTEMA_GESTION_LICENCIAS.txt", "."),
            ("VALIDACION_LICENCIA_SEGURA.txt", "."),
        ]

        copied = 0
        for source_rel, dest_folder in docs_to_copy:
            source = self.project_root / source_rel
            if source.exists():
                try:
                    dest_file = self.install_dir / dest_folder / source.name
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, dest_file)
                    copied += 1
                except Exception as e:
                    self.log(f"Error copiando {source_rel}: {e}", "WARN")

        self.log(f"Documentación copiada: {copied} archivos", "SUCCESS")
        return True

    def copy_requirements(self) -> bool:
        """Copia requirements.txt."""
        self.log("Copiando dependencias...")

        source = self.project_root / "config" / "requirements.txt"
        dest = self.install_dir / "requirements.txt"

        try:
            if source.exists():
                shutil.copy2(source, dest)
                self.log(f"requirements.txt copiado", "SUCCESS")
                return True
            else:
                self.log(f"No se encontró requirements.txt", "WARN")
                return False
        except Exception as e:
            self.log(f"Error copiando requirements: {e}", "ERROR")
            return False

    def install_dependencies(self) -> bool:
        """Instala dependencias Python."""
        self.log("Instalando dependencias Python...")

        requirements = self.install_dir / "requirements.txt"
        if not requirements.exists():
            self.log("requirements.txt no encontrado", "WARN")
            return False

        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r",
                str(requirements), "--quiet"
            ])
            self.log("Dependencias instaladas correctamente", "SUCCESS")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Error instalando dependencias: {e}", "ERROR")
            return False

    def create_launcher_batch(self) -> bool:
        """Crea launcher.bat para Windows."""
        self.log("Creando launcher...")

        launcher_content = f"""@echo off
REM iBot Trading Launcher
REM Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

echo.
echo ====================================
echo iBot Trading - Iniciando...
echo ====================================
echo.

cd /d "{self.install_dir}"
streamlit run app_main.py

pause
"""

        try:
            launcher_path = self.install_dir / "launcher.bat"
            with open(launcher_path, "w", encoding="utf-8") as f:
                f.write(launcher_content)
            self.log("launcher.bat creado", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Error creando launcher: {e}", "ERROR")
            return False

    def create_installation_readme(self) -> bool:
        """Crea README de instalación."""
        self.log("Creando README de instalación...")

        readme_content = f"""================================================================================
iBot Trading - GUIA DE INSTALACION
================================================================================
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Ubicación: {self.install_dir}

================================================================================
PRÓXIMOS PASOS - CONFIGURACIÓN
================================================================================

1. EDITAR CONFIGURACION
   ─────────────────────────────────────────────────────────────────

   Abre: config\\config.ini

   Edita SOLO estos campos:

   [LICENSE]
   LICENSE_KEY = Tu licencia (proporcionada en el email)

   [MT5_ACCOUNT]
   MT5_LOGIN = Tu número de cuenta en MetaTrader5
   MT5_PASSWORD = Tu contraseña MT5
   MT5_SERVER = Tu servidor de broker (ej: ICMarketsSC-Demo)

   [TRADING_PARAMETERS]
   SYMBOLS = Los símbolos a tradear (separados por comas)

   NO EDITES el resto de secciones.

2. EJECUTAR APLICACION
   ─────────────────────────────────────────────────────────────────

   Haz doble clic en: launcher.bat

   O desde terminal:
   streamlit run app_main.py

   La aplicación se abrirá en tu navegador (http://localhost:8501)

3. VALIDAR LICENCIA
   ─────────────────────────────────────────────────────────────────

   Al iniciar, el sistema:
   ✓ Validará tu licencia contra el servidor
   ✓ Conectará a tu cuenta MetaTrader5
   ✓ Iniciará el análisis de mercado

   Si ves "Licencia válida" - ¡Todo está listo!

================================================================================
ESTRUCTURA DE CARPETAS
================================================================================

{self.install_dir}/
├── launcher.bat .................. Acceso directo para ejecutar
├── config.ini .................... Configuración (EDITABLE)
├── requirements.txt .............. Dependencias instaladas
├── app_main.py ................... Punto de entrada
├── src/
│   ├── app.py .................... Aplicación principal (compilada)
│   ├── config.py ................. Configuración (compilada)
│   ├── anthropic_service.py ...... Servicio Claude (compilada)
│   ├── mt5_service.py ............ Conexión MT5 (compilada)
│   └── ... más archivos compilados
├── core/
│   ├── config_loader.py .......... Cargador de config (compilada)
│   └── license_manager.py ........ Validación de licencias (compilada)
├── config/
│   └── config.ini ................ Archivo de configuración
├── data/
│   ├── license_cache.json ........ Cache de validación (auto)
│   ├── trading_journal.csv ....... Diario de trades (auto)
│   └── strategy_memory.json ...... Memoria de estrategia (auto)
└── docs/
    └── README.txt ................ Documentación

================================================================================
PROTECCIÓN Y SEGURIDAD
================================================================================

✓ Código fuente compilado a bytecode (.pyc)
✓ Solo config.ini es editable
✓ Credenciales MT5 locales (no transmitidas)
✓ Validación de licencias en servidor
✓ Sin acceso a Google Sheets directamente

================================================================================
SOLUCION DE PROBLEMAS
================================================================================

Error: "Licencia inválida"
  → Verificar que LICENSE_KEY en config.ini coincida con el email
  → Revisar que tienes conexión a internet

Error: "No se puede conectar a MetaTrader5"
  → Asegurar que MT5 está abierto
  → Verificar que MT5_LOGIN, MT5_PASSWORD y MT5_SERVER son correctos
  → Probar directamente en MT5

Error: "ModuleNotFoundError"
  → Ejecutar: pip install -r requirements.txt
  → Verificar que Python 3.8+ está instalado

La aplicación no se abre
  → Revisar la terminal para mensajes de error
  → Ejecutar desde terminal: streamlit run app_main.py

================================================================================
SOPORTE Y DOCUMENTACION
================================================================================

Documentos en esta carpeta:
  - SISTEMA_GESTION_LICENCIAS.txt
  - VALIDACION_LICENCIA_SEGURA.txt
  - docs/README.txt

Para soporte:
  1. Revisar los documentos en la carpeta
  2. Verificar los logs en installation.log
  3. Contactar a support@ibot-trading.com

================================================================================
PROXIMOS PASOS
================================================================================

Después de la instalación:

1. Edita config\\config.ini con tus datos MT5
2. Ejecuta launcher.bat
3. Verifica que la licencia es válida
4. Comienza a operar

¡Bienvenido a iBot Trading!

================================================================================
Generado automáticamente por el instalador
================================================================================
"""

        try:
            readme_path = self.install_dir / "PRIMEROS_PASOS.txt"
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme_content)
            self.log("PRIMEROS_PASOS.txt creado", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Error creando README: {e}", "ERROR")
            return False

    def create_installation_summary(self) -> bool:
        """Crea resumen de instalación en JSON."""
        self.log("Creando resumen de instalación...")

        duration = (datetime.now() - self.start_time).total_seconds()

        summary = {
            "installation_date": datetime.now().isoformat(),
            "install_directory": str(self.install_dir),
            "duration_seconds": duration,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "status": "completed",
        }

        try:
            summary_path = self.install_dir / "installation_summary.json"
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
            self.log("Resumen guardado", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Error creando resumen: {e}", "WARN")
            return False

    def run(self) -> bool:
        """Ejecuta la instalación completa."""
        self.print_header()

        steps = [
            ("Verificar Python", self.check_python_version),
            ("Crear directorios", self.create_directories),
            ("Compilar código", self.compile_python_files),
            ("Copiar configuración", self.copy_config_template),
            ("Copiar documentación", self.copy_documentation),
            ("Copiar dependencias", self.copy_requirements),
            ("Instalar librerías", self.install_dependencies),
            ("Crear launcher", self.create_launcher_batch),
            ("Generar README", self.create_installation_readme),
            ("Crear resumen", self.create_installation_summary),
        ]

        completed = 0
        for step_name, step_func in steps:
            try:
                if step_func():
                    completed += 1
                else:
                    self.log(f"Paso '{step_name}' incompleto", "WARN")
            except Exception as e:
                self.log(f"Error en paso '{step_name}': {e}", "ERROR")

        # Resumen final
        print("\n" + "=" * 80)
        print(f"INSTALACION COMPLETADA: {completed}/{len(steps)} pasos exitosos")
        print("=" * 80)
        print(f"\nTiempo total: {(datetime.now() - self.start_time).total_seconds():.1f} segundos")
        print(f"\nPróximos pasos:")
        print(f"  1. Edita: {self.install_dir / 'config' / 'config.ini'}")
        print(f"  2. Haz doble clic en: {self.install_dir / 'launcher.bat'}")
        print(f"\nDocumentación: Revisa {self.install_dir / 'PRIMEROS_PASOS.txt'}")
        print(f"Logs: {self.log_file}")
        print("=" * 80 + "\n")

        return completed == len(steps)


def main():
    if len(sys.argv) < 2:
        print("Uso: python advanced_installer.py <directorio_destino>")
        print("\nEjemplo:")
        print("  python advanced_installer.py \"C:\\iBot_Trading\"")
        sys.exit(1)

    install_dir = sys.argv[1]
    installer = AdvancedInstaller(install_dir)

    try:
        success = installer.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInstalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\nError fatal durante la instalación: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
