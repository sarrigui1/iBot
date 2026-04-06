"""
iBot Enterprise Installer
Instala automaticamente: Python, dependencias, configura la app y crea accesos directos

Uso:
  python installer.py

O compilar con PyInstaller:
  pyinstaller --onefile --windowed installer.py
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime

# Si se ejecuta desde PyInstaller (.exe compilado)
# sys._MEIPASS contiene la ruta donde extrae los datos empaquetados
PYINSTALLER_ROOT = getattr(sys, '_MEIPASS', None)


class IBotInstaller:
    def __init__(self):
        self.app_dir = None
        self.source_dir = None  # Dónde están los archivos (puede ser diferente si viene de .exe)
        self.config_file = None
        self.log_file = None

    def log(self, message, level="INFO"):
        """Escribe mensaje a log y consola"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {message}"
        print(log_msg)

        if self.log_file:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_msg + "\n")

    def check_python(self):
        """Verifica que Python está instalado y accesible"""
        self.log("Verificando Python...")

        # Cuando se ejecuta desde .exe compilado, sys.executable apunta al .exe
        # Así que buscar python.exe en el PATH en lugar de usar sys.executable
        import shutil
        python_exe = shutil.which('python') or shutil.which('python3')

        if not python_exe:
            self.log("Python NO encontrado en PATH", "ERROR")
            return False

        self.log(f"  Python encontrado: {python_exe}")

        try:
            self.log("  Ejecutando: python --version...")
            result = subprocess.run([python_exe, "--version"],
                                  capture_output=True, text=True, timeout=10)
            version = result.stdout.strip() or result.stderr.strip()
            self.log(f"  stdout: {result.stdout}")
            self.log(f"  stderr: {result.stderr}")
            self.log(f"  returncode: {result.returncode}")

            if result.returncode == 0:
                self.log(f"Python encontrado: {version}", "OK")
                return True
            else:
                self.log(f"Python retornó error (code {result.returncode}): {result.stderr}", "ERROR")
                return False

        except subprocess.TimeoutExpired:
            self.log("Error: Python check timeout (10 segundos)", "ERROR")
            return False
        except Exception as e:
            self.log(f"Python NO encontrado: {type(e).__name__}: {e}", "ERROR")
            import traceback
            self.log(f"Traceback: {traceback.format_exc()}", "ERROR")
            return False

    def install_dependencies(self):
        """Instala requirements.txt"""
        self.log("=" * 60)
        self.log("Instalando dependencias (esto puede tomar 5-10 minutos)...")
        self.log("Verás el progreso abajo:")
        self.log("=" * 60)

        # Obtener Python real (no el .exe si se ejecuta compilado)
        import shutil
        python_exe = shutil.which('python') or shutil.which('python3') or sys.executable

        # Probar en orden: config/requirements.txt (en SOURCE_DIR si viene de .exe)
        req_file = os.path.join(self.source_dir, "config", "requirements.txt")
        self.log(f"Buscando requirements.txt en: {req_file}")

        if not os.path.exists(req_file):
            # Fallback: raíz del directorio (para compatibilidad)
            req_file = os.path.join(self.source_dir, "requirements.txt")
            self.log(f"No encontrado, intentando: {req_file}")

        if not os.path.exists(req_file):
            self.log(f"requirements.txt no encontrado en ninguna ubicación", "ERROR")
            self.log(f"  Buscó en: {os.path.join(self.source_dir, 'requirements.txt')}", "ERROR")
            self.log(f"  Buscó en: {req_file}", "ERROR")
            return False

        self.log(f"requirements.txt encontrado: {req_file}", "OK")

        try:
            self.log(f"Ejecutando: {python_exe} -m pip install -r {req_file}")
            # Mostrar output en tiempo real (sin capture_output)
            result = subprocess.run([
                python_exe, "-m", "pip", "install",
                "-r", req_file
            ], timeout=600)  # 10 minutos timeout

            self.log("=" * 60)
            if result.returncode == 0:
                self.log("Dependencias instaladas correctamente", "OK")
            else:
                self.log(f"Pip retornó código de error: {result.returncode}", "ERROR")
            self.log("=" * 60)
            return result.returncode == 0

        except subprocess.TimeoutExpired:
            self.log("Error: Instalación timeout (10 minutos)", "ERROR")
            return False
        except subprocess.CalledProcessError as e:
            self.log(f"Error CalledProcessError: {e}", "ERROR")
            self.log(f"  returncode: {e.returncode}", "ERROR")
            self.log(f"  output: {e.output}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Error instalando dependencias: {type(e).__name__}: {e}", "ERROR")
            import traceback
            self.log(f"Traceback: {traceback.format_exc()}", "ERROR")
            return False

    def copy_project_files(self):
        """Verifica/copia ejecutable compilado (NO código fuente)"""
        self.log("Verificando ejecutable compilado...")

        ibot_exe = os.path.join(self.app_dir, "ibot.exe")

        # Si ya existe, no hacer nada
        if os.path.exists(ibot_exe):
            self.log(f"  ibot.exe ya existe", "OK")
            return True

        # Si estamos en el directorio de desarrollo, copiar desde dist/
        dist_exe = os.path.join(self.source_dir, "..", "..", "dist", "iBot_Enterprise", "ibot.exe")
        if os.path.exists(dist_exe):
            shutil.copy(dist_exe, ibot_exe)
            self.log(f"  ibot.exe copiado desde dist/", "OK")
            return True

        # Si no lo encontramos, avisar al usuario
        self.log("  ibot.exe no encontrado", "WARN")
        self.log("  IMPORTANTE: Necesitas copiar ibot.exe a esta carpeta", "WARN")
        self.log(f"  Ubicación esperada: {ibot_exe}", "WARN")

        return True  # No es error crítico, usuario puede agregar después

    def setup_config(self):
        """Crea config.ini inicial si no existe"""
        self.log("Verificando configuracion...")

        # Buscar config.ini en source_dir (donde están los archivos originales)
        source_config = os.path.join(self.source_dir, "config", "config.ini")

        # Copiar a app_dir (carpeta de instalación del cliente)
        config_path = os.path.join(self.app_dir, "config", "config.ini")

        # Si app_dir es diferente de source_dir, copiar el archivo
        if self.app_dir != self.source_dir and os.path.exists(source_config):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            shutil.copy(source_config, config_path)
            self.log(f"config.ini copiado a: {config_path}", "OK")

        if os.path.exists(config_path):
            self.log("config.ini ya existe", "OK")
            return True

        # Si no existe, avisa al usuario
        self.log("ACCION REQUERIDA: Edita config.ini con tus credenciales MT5", "WARN")
        return True

    def create_shortcut(self):
        """Crea acceso directo en escritorio"""
        self.log("Creando acceso directo en escritorio...")

        try:
            import win32com.client

            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "iBot Trading.lnk"

            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))

            # Script que lanza streamlit
            launcher = os.path.join(self.app_dir, "launcher.bat")
            shortcut.Targetpath = launcher
            shortcut.WorkingDirectory = self.app_dir
            # Usar ícono de la app (en src/)
            shortcut.IconLocation = os.path.join(self.app_dir, "src", "app.py")
            shortcut.save()

            self.log(f"Acceso directo creado: {shortcut_path}", "OK")
            return True
        except Exception as e:
            self.log(f"No se pudo crear acceso directo: {e}", "WARN")
            # No es critico si falla
            return True

    def create_launcher(self):
        """Crea launcher.bat para iniciar la aplicación compilada"""
        self.log("Creando launcher.bat...")

        # Crear en app_dir (carpeta de instalación del cliente)
        launcher_path = os.path.join(self.app_dir, "launcher.bat")

        content = f"""@echo off
REM iBot - Intelligence Trading Launcher
REM Este archivo inicia la aplicacion compilada

cd /d "{self.app_dir}"
echo [iBot] Iniciando Intelligence Trading...
echo Abriendo navegador en http://localhost:8501
timeout /t 2 /nobreak

REM Ejecutar aplicacion compilada
ibot.exe

pause
"""

        try:
            with open(launcher_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.log(f"launcher.bat creado: {launcher_path}", "OK")
            return True
        except Exception as e:
            self.log(f"Error creando launcher.bat: {e}", "ERROR")
            return False

    def create_readme(self):
        """Crea README para primeros pasos"""
        self.log("Creando PRIMEROS_PASOS.txt...")

        # Crear en app_dir (carpeta de instalación del cliente)
        readme_path = os.path.join(self.app_dir, "PRIMEROS_PASOS.txt")

        content = """
================================================================================
iBot - Intelligence Trading
PRIMEROS PASOS DESPUES DE INSTALACION
================================================================================

GRACIAS por adquirir iBot! Aqui estan los pasos para comenzar:

PASO 1: CONFIGURAR CREDENCIALES
--------------------------------
1. Abre el archivo: config.ini
2. Completa estos campos con tus datos MT5:

   [MT5_ACCOUNT]
   MT5_LOGIN = tu_login_aqui
   MT5_PASSWORD = tu_password_aqui
   MT5_SERVER = tu_servidor_aqui

   [LICENSE]
   LICENSE_KEY = tu_license_key_aqui

3. Guarda el archivo

PASO 2: EJECUTAR LA APLICACION
------------------------------
Opcion A (Rapido):
  - Doble clic en: launcher.bat
  - Se abrira automáticamente en tu navegador

Opcion B (Desde cmd):
  - Abre cmd
  - Navega a esta carpeta
  - Ejecuta: streamlit run app.py

PASO 3: USAR LA APLICACION
---------------------------
1. Espera a que cargue el dashboard
2. En la sidebar izquierda:
   - Selecciona el par de divisas a operar
   - Configura el refresh interval
   - Activa/desactiva análisis IA
3. El bot mostrara:
   - Análisis técnico en tiempo real
   - Recomendaciones de IA
   - Posiciones abiertas
   - Historial de trades

CONFIGURACION RECOMENDADA INICIAL
----------------------------------
- Modo: MANUAL (no automatico)
- Simbolos: EURUSD (comienza con uno)
- Confianza minima: 0.85 (85%)
- Pérdida diaria max: 3%
- Refresh: 60 segundos

CONTACTO Y SOPORTE
------------------
Email: soporte@ibot-trading.com
Documentacion: Ver README.txt

DISCLAIMER
----------
El trading conlleva riesgo de pérdida total del capital.
Prueba en DEMO antes de usar dinero real.
Nunca trades con dinero que no puedas perder.

================================================================================
"""

        try:
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.log("PRIMEROS_PASOS.txt creado", "OK")
            return True
        except Exception as e:
            self.log(f"Error creando README: {e}", "WARN")
            return True

    def verify_installation(self):
        """Verifica que la instalacion fue exitosa"""
        self.log("Verificando instalacion...")

        # Archivos requeridos en raíz
        required_files = ["ibot.exe", "launcher.bat"]

        # Archivos en subdirectorios
        required_dirs = [
            ("config", "config.ini"),
            ("config", "requirements.txt"),
        ]

        # Verificar archivos en raíz
        all_ok = True
        for file in required_files:
            path = os.path.join(self.app_dir, file)
            if os.path.exists(path):
                self.log(f"  {file}: OK", "OK")
            else:
                self.log(f"  {file}: FALTANTE", "WARN")
                all_ok = False

        # Verificar archivos en subdirectorios
        for subdir, file in required_dirs:
            path = os.path.join(self.app_dir, subdir, file)
            if os.path.exists(path):
                self.log(f"  {subdir}/{file}: OK", "OK")
            else:
                self.log(f"  {subdir}/{file}: FALTANTE", "WARN")

        self.log("Verificacion completada", "OK")
        return all_ok

    def run(self, app_dir=None):
        """Ejecuta el instalador completo"""
        if app_dir:
            self.app_dir = os.path.abspath(app_dir)
        else:
            # Si se ejecuta desde PyInstaller (.exe compilado)
            if PYINSTALLER_ROOT:
                # Los archivos ORIGINALES están en sys._MEIPASS
                # Pero debemos INSTALAR en la carpeta donde está el .exe

                # sys.argv[0] contiene la ruta del .exe ejecutado
                exe_path = os.path.abspath(sys.argv[0])
                exe_dir = os.path.dirname(exe_path)

                self.app_dir = exe_dir  # Instalar en carpeta del .exe
                self.source_dir = PYINSTALLER_ROOT  # Archivos fuente temporales

                self.log("Ejecutando desde .exe compilado (PyInstaller)", "INFO")
                self.log(f"Ubicación del .exe: {exe_dir}", "INFO")
                self.log(f"Archivos temporales en: {PYINSTALLER_ROOT}", "INFO")
            else:
                # Se ejecuta como script Python normal
                script_dir = os.path.dirname(os.path.abspath(__file__))

                # Si está en tools/, subir a raíz del proyecto
                if os.path.basename(script_dir) == "tools":
                    self.app_dir = os.path.dirname(script_dir)
                else:
                    self.app_dir = script_dir

                self.source_dir = self.app_dir  # Los archivos están en el mismo lugar

        self.log_file = os.path.join(self.app_dir, "instalacion.log")

        self.log("=" * 70)
        self.log("iBot - Intelligence Trading - INSTALADOR")
        self.log("=" * 70)
        self.log(f"Directorio de instalación: {self.app_dir}")
        if self.app_dir != self.source_dir:
            self.log(f"Archivos fuente en: {self.source_dir}")

        # Validar que la ruta de ARCHIVOS FUENTE es correcta
        required_markers = ["app_main.py", "config", "src", "core"]
        missing = [m for m in required_markers if not os.path.exists(os.path.join(self.source_dir, m))]

        if missing:
            self.log(f"ERROR: Archivos fuente incompletos. Faltan: {missing}", "ERROR")
            self.log(f"Esperado encontrar en: {self.source_dir}", "ERROR")
            self.log(f"Problema: El instalador o los archivos están corruptos.", "ERROR")
            input("Presiona Enter para salir...")
            return False

        self.log("Estructura del proyecto validada correctamente", "OK")

        # Ejecutar pasos
        steps = [
            ("Verificar Python", self.check_python),
            ("Instalar dependencias", self.install_dependencies),
            ("Copiar archivos del proyecto", self.copy_project_files),
            ("Configurar aplicacion", self.setup_config),
            ("Crear launcher", self.create_launcher),
            ("Crear acceso directo", self.create_shortcut),
            ("Crear guia de primeros pasos", self.create_readme),
            ("Verificar instalacion", self.verify_installation),
        ]

        success_count = 0
        for step_name, step_func in steps:
            self.log(f"\n[PASO] {step_name}...")
            try:
                result = step_func()
                if result:
                    success_count += 1
                    self.log(f"[OK] {step_name} completado", "OK")
                else:
                    self.log(f"[ERROR] FALLO: {step_name}", "ERROR")
            except Exception as e:
                self.log(f"[ERROR] EXCEPCION en {step_name}", "ERROR")
                self.log(f"  Tipo: {type(e).__name__}", "ERROR")
                self.log(f"  Mensaje: {e}", "ERROR")
                import traceback
                self.log(f"  Traceback: {traceback.format_exc()}", "ERROR")

        # Resumen
        self.log("\n" + "=" * 70)
        if success_count == len(steps):
            self.log("INSTALACION COMPLETADA EXITOSAMENTE!", "OK")
            self.log("=" * 70)
            self.log("\nPROXIMOS PASOS:")
            self.log("1. Lee PRIMEROS_PASOS.txt")
            self.log("2. Edita config.ini con tus credenciales MT5")
            self.log("3. Ejecuta launcher.bat")
            self.log("\nLa app se abrira en: http://localhost:8501")
            self.log("\nLog guardado en: " + self.log_file)
        else:
            self.log(f"INSTALACION PARCIAL: {success_count}/{len(steps)} pasos exitosos", "WARN")
            self.log("Ver log para detalles: " + self.log_file)

        self.log("=" * 70)
        self.log("Presiona Enter para salir...")
        input()  # Esperar a que el usuario presione Enter

        return success_count == len(steps)


if __name__ == "__main__":
    installer = IBotInstaller()
    success = installer.run()

    if not success:
        sys.exit(1)
