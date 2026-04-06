"""
Build script for PyInstaller -- Compile app.py a ejecutable Windows.

Uso:
  python build_exe.py

Genera:
  dist/iBot_Enterprise/
  |-- ibot.exe
  |-- config.ini
  |-- data/
  |-- README.txt
  L-- [todas las dependencias compiladas]
"""

import subprocess
import shutil
import os
import sys


def build_exe():
    """Compila el app con PyInstaller y estructura la carpeta de distribucion."""

    print("=" * 70)
    print("iBot - Intelligence Trading - Build Script")
    print("=" * 70)

    # Limpiar builds previos
    print("\n[1/4] Limpiando builds previos...")
    for dirname in ['build', 'dist']:
        if os.path.exists(dirname):
            print(f"  Eliminando {dirname}/")
            shutil.rmtree(dirname)

    # Compilar con PyInstaller
    print("\n[2/4] Compilando con PyInstaller...")
    try:
        result = subprocess.run(
            ['pyinstaller', 'build_exe.spec'],
            check=True,
            capture_output=False
        )
        print("  [OK] Compilacion exitosa")
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] {e}")
        sys.exit(1)

    # Crear estructura iBot_Enterprise
    print("\n[3/4] Creando estructura de distribucion...")

    dist_dir = os.path.join('dist', 'iBot_Enterprise')
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    print(f"  Carpeta: {dist_dir}")

    # Mover exe
    src_exe = os.path.join('dist', 'ibot.exe')
    dst_exe = os.path.join(dist_dir, 'ibot.exe')
    if os.path.exists(src_exe):
        shutil.move(src_exe, dst_exe)
        print(f"  [OK] ibot.exe movido")

    # Copiar config.ini
    if os.path.exists('config.ini'):
        shutil.copy('config.ini', dist_dir)
        print(f"  [OK] config.ini copiado")

    # Copiar carpeta data
    if os.path.exists('data'):
        data_dst = os.path.join(dist_dir, 'data')
        if os.path.exists(data_dst):
            shutil.rmtree(data_dst)
        shutil.copytree('data', data_dst)
        print(f"  [OK] data/ copiado")

    # Copiar README.txt si existe
    if os.path.exists('README.txt'):
        shutil.copy('README.txt', dist_dir)
        print(f"  [OK] README.txt copiado")

    # Limpiar el directorio dist original (dejar solo iBot_Enterprise)
    print("\n[4/4] Limpiando artifacts...")
    try:
        # Eliminar todos los archivos/carpetas en dist/ excepto iBot_Enterprise
        for item in os.listdir('dist'):
            if item != 'iBot_Enterprise':
                path = os.path.join('dist', item)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
        print("  [OK] Artifacts limpios")
    except Exception as e:
        print(f"  [WARN] Error limpiando: {e}")

    # Resumen final
    print("\n" + "=" * 70)
    print("[OK] BUILD COMPLETO")
    print("=" * 70)
    print(f"\nArchivos listos para distribucion en:")
    print(f"  -> {os.path.abspath(dist_dir)}")
    print(f"\nArchivos generados:")
    try:
        for item in sorted(os.listdir(dist_dir)):
            path = os.path.join(dist_dir, item)
            if os.path.isdir(path):
                size = sum(os.path.getsize(os.path.join(root, f))
                          for root, dirs, files in os.walk(path)
                          for f in files)
                print(f"  {item:20} [DIR, ~{size/1024/1024:.1f} MB]")
            else:
                size = os.path.getsize(path) / 1024 / 1024
                print(f"  {item:20} [{size:.1f} MB]")
    except Exception as e:
        print(f"  [WARN] Error listando: {e}")

    print("\nProximos pasos:")
    print("  1. Edita config.ini con datos del cliente")
    print("  2. Entrega la carpeta iBot_Enterprise a cliente")
    print("  3. Cliente ejecuta: iBot_Enterprise/ibot.exe")
    print("\n")


if __name__ == '__main__':
    build_exe()
